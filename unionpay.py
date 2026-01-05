import ctypes
from ctypes import c_int, c_char_p, byref, cdll
import configparser
import os
import logging
from datetime import datetime
import shutil
import json
import threading
import time

from fastapi import APIRouter, Query


# 全局静态变量
DLL_FILENAME = 'MisPos.dll'
CONFIG_FILENAME = 'conf.ini'

unionpay_router = APIRouter(prefix="/gbunionpay", tags=["广百银联支付接口"])


class UnionPayDLL:
    # 类级别的支付结果缓存，存储在内存中
    _payment_cache = {}
    # 用于缓存操作的全局锁
    _cache_lock = threading.Lock()
    # 用于特定交易的锁，防止同一笔交易的并发处理
    _transaction_locks = {}
    # 保护 _transaction_locks 字典本身的锁
    _transaction_locks_lock = threading.RLock()
    
    # 日志管理锁
    _log_lock = threading.Lock()

    def __init__(self, ip_address, dll_path=DLL_FILENAME):
        """
        初始化银联DLL调用类
        :param ip_address: 目标IP地址
        :param dll_path: DLL文件路径
        """
        if not ip_address:
            raise ValueError("IP地址不能为空")
        
        # 验证IP地址格式
        if not self._is_valid_ip(ip_address):
            raise ValueError(f"无效的IP地址格式: {ip_address}")
        
        self.ip_address = ip_address
        self.ip_folder = os.path.join(os.path.dirname(__file__), 'GBunionpay', ip_address)
        
        # 检查并创建IP对应的文件夹
        self._setup_ip_folder()
        
        # 使用IP文件夹中的DLL路径
        self.dll_path = os.path.join(self.ip_folder, os.path.basename(dll_path))
        
        try:
            # 加载DLL
            self.mispos_dll = cdll.LoadLibrary(self.dll_path)
        except OSError as e:
            print(f"加载DLL失败: {e}")
            raise

        # 设置日志
        self._setup_logging()

        # 读取配置文件
        self.config = self._load_config()
        
        # 初始化时从持久化存储加载缓存数据
        self._load_cache_from_persistence()

    def _is_valid_ip(self, ip):
        """
        验证IP地址格式
        """
        import re
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(pattern, ip) is not None

    @classmethod
    def _get_cache_key(cls, trans_id, mer_order_no):
        """
        生成缓存键
        """
        if not trans_id or not mer_order_no:
            raise ValueError("交易ID和商户订单号不能为空")
        return f"{trans_id}_{mer_order_no}"

    @classmethod
    def _get_payment_result_from_cache(cls, trans_id, mer_order_no):
        """
        从缓存获取支付结果
        """
        with cls._cache_lock:
            key = cls._get_cache_key(trans_id, mer_order_no)
            return cls._payment_cache.get(key)

    @classmethod
    def _get_transaction_lock(cls, trans_id, mer_order_no):
        """
        获取特定交易的锁，防止同一笔交易的并发处理
        """
        key = cls._get_cache_key(trans_id, mer_order_no)
        with cls._transaction_locks_lock:
            if key not in cls._transaction_locks:
                cls._transaction_locks[key] = threading.Lock()
            return cls._transaction_locks[key]

    @classmethod
    def _store_payment_result_to_cache(cls, trans_id, mer_order_no, result_data):
        """
        将支付结果存储到缓存
        """
        with cls._cache_lock:
            key = cls._get_cache_key(trans_id, mer_order_no)
            # 添加时间戳，以便后续清理过期缓存
            result_data['timestamp'] = datetime.now().isoformat()
            cls._payment_cache[key] = result_data
            # 同时持久化到文件
            cls._save_cache_to_persistence()

    @classmethod
    def _save_cache_to_persistence(cls):
        """
        将缓存数据持久化到文件
        """
        cache_file = os.path.join(os.path.dirname(__file__), 'payment_cache.json')
        try:
            # 使用临时文件和原子操作，防止写入过程中程序崩溃导致数据丢失
            temp_file = cache_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(cls._payment_cache, f, ensure_ascii=False, indent=2)
            # 原子操作：重命名临时文件为实际文件
            os.replace(temp_file, cache_file)
        except Exception as e:
            print(f"持久化缓存失败: {e}")

    @classmethod
    def _load_cache_from_persistence(cls):
        """
        从持久化文件加载缓存数据
        """
        cache_file = os.path.join(os.path.dirname(__file__), 'payment_cache.json')
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cls._payment_cache = json.load(f)
                    
                # 清理过期的缓存数据（超过24小时的）
                cls._cleanup_expired_cache()
        except (json.JSONDecodeError, ValueError) as e:
            print(f"从持久化文件加载缓存失败，可能是文件格式错误: {e}")
            cls._payment_cache = {}
        except Exception as e:
            print(f"从持久化文件加载缓存失败: {e}")
            cls._payment_cache = {}

    @classmethod
    def _cleanup_expired_cache(cls):
        """
        清理过期的缓存数据
        """
        current_time = datetime.now()
        expired_keys = []
        
        for key, data in cls._payment_cache.items():
            if 'timestamp' in data:
                try:
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    # 如果缓存数据超过24小时，则标记为过期
                    if (current_time - timestamp).total_seconds() > 24 * 3600:
                        expired_keys.append(key)
                except ValueError:
                    # 如果时间戳格式不正确，则删除该缓存
                    expired_keys.append(key)
        
        # 删除过期的缓存
        for key in expired_keys:
            del cls._payment_cache[key]
        
        # 如果删除了过期数据，需要重新保存
        if expired_keys:
            cls._save_cache_to_persistence()

    def _setup_ip_folder(self):
        """
        设置IP对应的文件夹，如果不存在则创建，并复制必要的文件
        """
        try:
            # 如果IP文件夹不存在，则创建
            if not os.path.exists(self.ip_folder):
                os.makedirs(self.ip_folder)
                
                # 获取原始DLL和配置文件路径
                original_dll_path = os.path.join(os.path.dirname(__file__), 'GBunionpay', DLL_FILENAME)
                original_config_path = os.path.join(os.path.dirname(__file__), 'GBunionpay', CONFIG_FILENAME)
                
                # 检查源文件是否存在
                if not os.path.exists(original_dll_path):
                    raise FileNotFoundError(f"源DLL文件不存在: {original_dll_path}")
                if not os.path.exists(original_config_path):
                    raise FileNotFoundError(f"源配置文件不存在: {original_config_path}")
                
                # 复制DLL和配置文件到IP文件夹
                shutil.copy2(original_dll_path, self.ip_folder)
                shutil.copy2(original_config_path, self.ip_folder)
                    
                # 更新配置文件中的IP地址
                self._update_config_ip()
            else:
                # 检查配置文件中的IP是否与传入IP一致
                config_path = os.path.join(self.ip_folder, CONFIG_FILENAME)
                if os.path.exists(config_path):
                    current_ip = self._get_current_ip_from_config(config_path)
                    if current_ip != self.ip_address:
                        self._update_config_ip()
                else:
                    # 如果IP文件夹中没有配置文件，从原始位置复制
                    original_config_path = os.path.join(os.path.dirname(__file__), 'GBunionpay', CONFIG_FILENAME)
                    if os.path.exists(original_config_path):
                        shutil.copy2(original_config_path, config_path)
                        self._update_config_ip()
        except Exception as e:
            print(f"设置IP文件夹时出错: {e}")
            raise

    def _get_current_ip_from_config(self, config_path):
        """
        从配置文件获取当前IP地址
        """
        try:
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')
            return config.get('net', 'ipaddr', fallback='')
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return ''

    def _update_config_ip(self):
        """
        更新配置文件中的IP地址
        """
        config_path = os.path.join(self.ip_folder, CONFIG_FILENAME)
        
        try:
            config = configparser.ConfigParser()
            # 检查配置文件是否存在，如果不存在则创建
            if os.path.exists(config_path):
                config.read(config_path, encoding='utf-8')
            else:
                # 如果配置文件不存在，从原始文件复制
                original_config_path = os.path.join(os.path.dirname(__file__), 'GBunionpay', CONFIG_FILENAME)
                if os.path.exists(original_config_path):
                    shutil.copy2(original_config_path, config_path)
                    config.read(config_path, encoding='utf-8')
        
            # 确保有net节
            if not config.has_section('net'):
                config.add_section('net')
            
            # 更新IP地址
            config.set('net', 'ipaddr', self.ip_address)
            
            # 保存配置文件
            with open(config_path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"更新配置文件失败: {e}")
            raise

    def _setup_logging(self):
        """
        设置日志记录
        """
        try:
            # 在IP文件夹内创建logs目录
            log_dir = os.path.join(self.ip_folder, 'logs')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 设置日志格式和文件
            log_file = os.path.join(log_dir, f"unionpay_{datetime.now().strftime('%Y%m%d')}.log")
            
            # 使用线程安全的日志记录器
            with self._log_lock:
                # 移除可能已存在的处理器以避免重复日志
                for handler in logging.root.handlers[:]:
                    logging.root.removeHandler(handler)
                
                # 为每个实例创建独立的logger
                self.logger = logging.getLogger(f"UnionPayDLL_{self.ip_address}")
                self.logger.handlers.clear()  # 清除已有的处理器
                
                # 创建文件处理器和控制台处理器
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                console_handler = logging.StreamHandler()
                
                # 设置日志格式
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                
                # 添加处理器到logger
                self.logger.addHandler(file_handler)
                self.logger.addHandler(console_handler)
                self.logger.setLevel(logging.INFO)
                
        except Exception as e:
            print(f"设置日志时出错: {e}")
            raise

    def _load_config(self):
        """
        加载配置文件
        """
        try:
            config_path = os.path.join(self.ip_folder, CONFIG_FILENAME)
            config = configparser.ConfigParser()
            if os.path.exists(config_path):
                config.read(config_path, encoding='utf-8')
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            raise

    def payment_transaction(self, app_name, trans_id, amount, org_id='', dt='', ref_no='', mer_order_no='', out_info=''):
        """
        收款业务主函数
        :param app_name: 应用名称
        :param trans_id: 交易ID
        :param amount: 金额
        :param org_id: 原始跟踪号
        :param dt: 日期时间
        :param ref_no: 参考号
        :param mer_order_no: 商户订单号
        :param out_info: 输出信息
        :return: 返回结果和更新后的参数
        """
        # 首先检查缓存中是否已有此交易的结果
        cached_result = self._get_payment_result_from_cache(trans_id, mer_order_no)
        if cached_result:
            self.logger.info(f"从缓存返回交易结果: trans_id={trans_id}, mer_order_no={mer_order_no}")
            return cached_result
        
        # 获取此特定交易的锁，防止同一笔交易的并发处理
        transaction_lock = self._get_transaction_lock(trans_id, mer_order_no)
        with transaction_lock:
            # 再次检查缓存，因为在等待锁的过程中可能已经有其他线程完成了处理
            cached_result = self._get_payment_result_from_cache(trans_id, mer_order_no)
            if cached_result:
                self.logger.info(f"从缓存返回交易结果: trans_id={trans_id}, mer_order_no={mer_order_no}")
                return cached_result
        
            try:
                # 记录调用日志
                self.logger.info(f"开始调用收款业务: app_name={app_name}, trans_id={trans_id}, amount={amount}, "
                                 f"org_id={org_id}, dt={dt}, ref_no={ref_no}, "
                                 f"mer_order_no={mer_order_no}, out_info={out_info}")
                
                # 将Python字符串转换为C字符串
                sappname = ctypes.c_char_p(app_name.encode('utf-8'))
                stransid = ctypes.c_char_p(trans_id.encode('utf-8'))
                samt = ctypes.c_char_p(amount.encode('utf-8'))
                sorgtraceno = ctypes.c_char_p(org_id.encode('utf-8'))
                sdt = ctypes.c_char_p(dt.encode('utf-8'))
                srefno = ctypes.c_char_p(ref_no.encode('utf-8'))
                merorderno = ctypes.c_char_p(mer_order_no.encode('utf-8'))
                poutinfo = ctypes.c_char_p(out_info.encode('utf-8'))

                # 调用DLL函数
                result = self.mispos_dll.MyMisPosfornet(
                    byref(sappname),
                    byref(stransid),
                    byref(samt),
                    byref(sorgtraceno),
                    byref(sdt),
                    byref(srefno),
                    byref(merorderno),
                    byref(poutinfo)
                )
                
                # 记录返回结果日志
                result_data = {
                    'result': result,
                    'app_name': sappname.value.decode('utf-8') if sappname.value else '',
                    'trans_id': stransid.value.decode('utf-8') if stransid.value else '',
                    'amount': samt.value.decode('utf-8') if samt.value else '',
                    'org_id': sorgtraceno.value.decode('utf-8') if sorgtraceno.value else '',
                    'dt': sdt.value.decode('utf-8') if sdt.value else '',
                    'ref_no': srefno.value.decode('utf-8') if srefno.value else '',
                    'mer_order_no': merorderno.value.decode('utf-8') if merorderno.value else '',
                    'out_info': poutinfo.value.decode('utf-8') if poutinfo.value else ''
                }
                
                self.logger.info(f"收款业务调用完成: result={result}, 返回数据={result_data}")

                # 将结果存储到缓存中
                self._store_payment_result_to_cache(trans_id, mer_order_no, result_data)

                return result_data
            except Exception as e:
                self.logger.error(f"调用收款业务时出错: {e}")
                raise

    def auth_deduction_transaction(self, app_name, trans_id, amount, hosp_number='', patient_name='', card_no='', out_info=''):
        """
        授权划付主函数
        :param app_name: 应用名称
        :param trans_id: 交易ID
        :param amount: 金额
        :param hosp_number: 医院编号
        :param patient_name: 患者姓名
        :param card_no: 卡号
        :param out_info: 输出信息
        :return: 返回结果和更新后的参数
        """
        # 首先检查缓存中是否已有此交易的结果
        cached_result = self._get_payment_result_from_cache(trans_id, card_no)
        if cached_result:
            self.logger.info(f"从缓存返回授权划付结果: trans_id={trans_id}, card_no={card_no}")
            return cached_result
        
        # 获取此特定交易的锁，防止同一笔交易的并发处理
        transaction_lock = self._get_transaction_lock(trans_id, card_no)
        with transaction_lock:
            # 再次检查缓存，因为在等待锁的过程中可能已经有其他线程完成了处理
            cached_result = self._get_payment_result_from_cache(trans_id, card_no)
            if cached_result:
                self.logger.info(f"从缓存返回授权划付结果: trans_id={trans_id}, card_no={card_no}")
                return cached_result
        
            try:
                # 记录调用日志
                self.logger.info(f"开始调用授权划付业务: app_name={app_name}, trans_id={trans_id}, amount={amount}, "
                                 f"hosp_number={hosp_number}, patient_name={patient_name}, card_no={card_no}, out_info={out_info}")
                
                # 将Python字符串转换为C字符串
                sappname = ctypes.c_char_p(app_name.encode('utf-8'))
                stransid = ctypes.c_char_p(trans_id.encode('utf-8'))
                samt = ctypes.c_char_p(amount.encode('utf-8'))
                shospnumber = ctypes.c_char_p(hosp_number.encode('utf-8'))
                spatientname = ctypes.c_char_p(patient_name.encode('utf-8'))
                scardno = ctypes.c_char_p(card_no.encode('utf-8'))
                poutinfo = ctypes.c_char_p(out_info.encode('utf-8'))

                # 调用DLL函数
                result = self.mispos_dll.MyMisPos3fornet(
                    byref(sappname),
                    byref(stransid),
                    byref(samt),
                    byref(shospnumber),
                    byref(spatientname),
                    byref(scardno),
                    byref(poutinfo)
                )
                
                # 记录返回结果日志
                result_data = {
                    'result': result,
                    'app_name': sappname.value.decode('utf-8') if sappname.value else '',
                    'trans_id': stransid.value.decode('utf-8') if stransid.value else '',
                    'amount': samt.value.decode('utf-8') if samt.value else '',
                    'hosp_number': shospnumber.value.decode('utf-8') if shospnumber.value else '',
                    'patient_name': spatientname.value.decode('utf-8') if spatientname.value else '',
                    'card_no': scardno.value.decode('utf-8') if scardno.value else '',
                    'out_info': poutinfo.value.decode('utf-8') if poutinfo.value else ''
                }
                
                self.logger.info(f"授权划付业务调用完成: result={result}, 返回数据={result_data}")

                # 将结果存储到缓存中
                self._store_payment_result_to_cache(trans_id, card_no, result_data)

                return result_data
            except Exception as e:
                self.logger.error(f"调用授权划付业务时出错: {e}")
                raise

@unionpay_router.post("/process_payment")
def process_payment(ip_address, app_name, trans_id, amount, org_id='', dt='', ref_no='', mer_order_no='', out_info=''):
    """
    处理收款业务
    :param ip_address: 目标IP地址
    """
    try:
        unionpay = UnionPayDLL(ip_address)
        return unionpay.payment_transaction(app_name, trans_id, amount, org_id, dt, ref_no, mer_order_no, out_info)
    except Exception as e:
        print(f"处理收款业务时出错: {e}")
        raise

@unionpay_router.post("/process_auth_deduction")
def process_auth_deduction(ip_address, app_name, trans_id, amount, hosp_number='', patient_name='', card_no='', out_info=''):
    """
    处理授权划付业务
    :param ip_address: 目标IP地址
    """
    try:
        unionpay = UnionPayDLL(ip_address)
        return unionpay.auth_deduction_transaction(app_name, trans_id, amount, hosp_number, patient_name, card_no, out_info)
    except Exception as e:
        print(f"处理授权划付业务时出错: {e}")
        raise