import ctypes
from ctypes import c_int, c_char_p, byref, cdll, WinDLL
import configparser
import os
import logging
from datetime import datetime
import shutil
import json
import threading
import time

# 导入FastAPI相关模块
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

# 全局静态变量
DLL_FILENAME = 'MisPos.dll'
CONFIG_FILENAME = 'conf.ini'





# 定义MyMisPos接口的返回结果模型
class MyMisPosResult(BaseModel):
    res_code: str = Field(..., description="返回码 00：成功；其他都是失败")
    res_msg: str = Field(..., description="返回描述 返回码不为 00 时，此字段返回错误码中文说明")
    merchant_no: str = Field(..., description="商户号 15 位")
    terminal_no: str = Field(..., description="终端号 8 位")
    amt: str = Field(..., description="交易金额 单位：元；带小数点")
    trace_no: str = Field(..., description="凭证号 6 位")
    ref_no: str = Field(..., description="系统参考号 12 位，银行卡及云闪付消费、撤销、查询。12 位，银行卡退货返回“原系统参考号”。云收银返回“渠道流水号”")
    card_no: Optional[str] = Field(None, description="银行卡号 银行卡、云闪付返回")
    out_trade_no: Optional[str] = Field(None, description="商户单号 云收银返回“系统流水号”")
    date: Optional[str] = Field(None, description="交易日期 yyyy/mm/dd")
    time: Optional[str] = Field(None, description="交易时间 mm:hh:dd")
    channel_name: Optional[str] = Field(None, description="交易分类 消费交易时返回：微信钱包、支付宝钱包、银联扫码、医保扫码、银联刷卡、医保刷卡，等；撤销、退货和查询交易均返回“空”值")
    payment_voucher_no: Optional[str] = Field(None, description="付款凭证号 云闪付交易返回，扫码退货需要")
    trans_chn_name: Optional[str] = Field(None, description="交易类型 消费、撤销、退货、扫码消费、扫码撤销、扫码退货，等")
    c_psam_id: Optional[str] = Field(None, description="PSAM 卡号 32 位")
    sz_yb_card_no: Optional[str] = Field(None, description="社保卡号 一般为脱敏号码")
    s_mer_order_no: Optional[str] = Field(None, description="商户订单号 扫码订单号，银网扫码消费、退货返回")
    dct_amount: Optional[str] = Field(None, description="优惠金额 有优惠金额的时候返回")
    dev_info: Optional[str] = Field(None, description="机身号")
    app_name: Optional[str] = Field(None, description="应用名称")
    trans_id: Optional[str] = Field(None, description="交易类型")
    s_mer_type: Optional[str] = Field(None, description="商户资料 无硬件云收银消费时返回，用于查询和退货的时候传入")
    mcht_dct_amount: Optional[str] = Field(None, description="商户优惠金额 商户促销")
    third_party_dct_amount: Optional[str] = Field(None, description="第三方优惠金额 银行促销")


# 定义请求模型
class PaymentRequest(BaseModel):
    ip_address: str = Field(..., description="刷卡机IP地址")
    app_name: str = Field(..., description="应用名称")
    trans_id: str = Field(..., description="交易类型")
    time_str: str = Field(..., description="请求时间 yyyymmddhhmmss")
    json_data: Optional[str] = Field("", description="入参数据 JSON 字符串")
    

# 定义银行卡收款请求模型
class BankCardPaymentRequest(BaseModel):
    ip_address: str = Field(..., description="刷卡机IP地址")
    s_amt: str = Field(..., description="交易金额，元为单位，如1元：1.00")
    s_mer_order_no: str = Field(..., description="商户订单号")
    time_str: str = Field(..., description="请求时间 yyyymmddhhmmss")


# 定义银行卡退款请求模型
class BankCardRefundRequest(BaseModel):
    ip_address: str = Field(..., description="刷卡机IP地址")
    s_amt: str = Field(..., description="交易金额，元为单位，如1元：1.00")
    s_org_trace_no: str = Field(..., description="交易凭证号，撤销、退货、预授权完成撤销必填")
    s_dt: str = Field(..., description="原交易日期，格式为MMDD")
    s_mer_order_no: str = Field(..., description="商户订单号")
    time_str: str = Field(..., description="请求时间 yyyymmddhhmmss")


# 定义扫码收款请求模型
class ScanCodePaymentRequest(BaseModel):
    ip_address: str = Field(..., description="刷卡机IP地址")
    s_amt: str = Field(..., description="交易金额，元为单位，如1元：1.00")
    s_type: str = Field(..., description="支付渠道,01—支付宝,02—微信")
    s_mer_order_no: str = Field(..., description="商户订单号")
    qrcode: str = Field(..., description="支付二维码")
    time_str: str = Field(..., description="请求时间 yyyymmddhhmmss")


# 定义扫码退款请求模型
class ScanCodeRefundRequest(BaseModel):
    ip_address: str = Field(..., description="刷卡机IP地址")
    s_amt: str = Field(..., description="交易金额，元为单位，如1元：1.00")
    s_type: str = Field(..., description="支付渠道,01—支付宝,02—微信")
    s_org_trace_no: str = Field(..., description="交易凭证号，撤销、退货、预授权完成撤销必填")
    s_dt: str = Field(..., description="原交易日期，格式为MMDD")
    s_ref_no: str = Field(..., description="20位付款凭证号，云闪付,渠道流水号，云收银")
    s_mer_order_no: str = Field(..., description="商户订单号")
    qrcode: str = Field(..., description="支付二维码")
    time_str: str = Field(..., description="请求时间 yyyymmddhhmmss")


class AuthDeductionRequest(BaseModel):
    ip_address: str = Field(..., description="刷卡机IP地址")
    app_name: str = Field(..., description="应用名称")
    trans_id: str = Field(..., description="交易类型")
    amount: str = Field(..., description="交易金额 单位：分，不带小数点。如 1 元： 100")
    hosp_number: Optional[str] = Field("", description="医院编号")
    patient_name: Optional[str] = Field("", description="患者姓名")
    card_no: Optional[str] = Field("", description="卡号")
    out_info: Optional[str] = Field("", description="输出信息")


# 定义响应模型
class PaymentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    


# 创建路由器
unionpay_router = APIRouter(prefix="/unionpay", tags=["广百银联支付接口"])


class UnionPayDLL:
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
        
        # 设置日志
        self._setup_logging()

        # 读取配置文件
        self.config = self._load_config()
        
        
        # 每个实例有独立的支付结果缓存
        self._payment_cache = {}
        # 用于缓存操作的锁
        self._cache_lock = threading.Lock()
        
        # 设置实例的缓存文件夹路径
        self._instance_folder = self.ip_folder
        
        
        
        # 添加日志：打印DLL路径信息
        self.logger.info(f"尝试加载DLL: {self.dll_path}")
        if not os.path.exists(self.dll_path):
            raise FileNotFoundError(f"DLL文件不存在: {self.dll_path}")
        if not os.path.exists(os.path.join(self.ip_folder, CONFIG_FILENAME)):
            self.logger.error(f"配置文件不存在: {os.path.join(self.ip_folder, CONFIG_FILENAME)}")
        
        try:
            # 尝试加载DLL，优先使用CDLL（更兼容）
            self.mispos_dll = cdll.LoadLibrary(self.dll_path)
            self.logger.info(f"成功加载DLL: {self.dll_path}")
        except OSError as e:
            # 记录详细错误信息
            self.logger.error(f"加载DLL失败: {e}")
            # 尝试使用WinDLL作为备选方案
            try:
                self.mispos_dll = WinDLL(self.dll_path)
                self.logger.info(f"使用WinDLL成功加载DLL: {self.dll_path}")
            except Exception as ex:
                self.logger.error(f"使用WinDLL加载也失败: {ex}")
                raise
        
        
        
        # 初始化时从持久化存储加载缓存数据
        self._load_cache_from_persistence()
        

    def _is_valid_ip(self, ip):
        """
        验证IP地址格式
        """
        import re
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(pattern, ip) is not None

    def _get_cache_key(self, app_name, mer_order_no):
        """
        生成缓存键
        """
        if not app_name or not mer_order_no:
            raise ValueError("交易类型和商户订单号不能为空")
        return f"{app_name}_{mer_order_no}"

    def _get_payment_result_from_cache(self, app_name, mer_order_no):
        """
        从缓存获取支付结果
        """
        with self._cache_lock:
            key = self._get_cache_key(app_name, mer_order_no)
            return self._payment_cache.get(key)

    def _get_transaction_lock(self, app_name, mer_order_no):
        """
        获取特定交易的锁，防止同一笔交易的并发处理
        """
        key = self._get_cache_key(app_name, mer_order_no)
        with UnionPayDLL._transaction_locks_lock:
            if key not in UnionPayDLL._transaction_locks:
                UnionPayDLL._transaction_locks[key] = threading.Lock()
            return UnionPayDLL._transaction_locks[key]

    def _store_payment_result_to_cache(self, app_name, mer_order_no, result_data):
        """
        将支付结果存储到缓存
        """
        with self._cache_lock:
            key = self._get_cache_key(app_name, mer_order_no)
            # 添加时间戳，以便后续清理过期缓存
            result_data_copy = result_data.copy()
            
            # 检查是否有parsed_result字段，如果有则转换为字典
            if 'parsed_result' in result_data_copy and result_data_copy['parsed_result'] is not None:
                # 将Pydantic模型转换为字典
                parsed_result = result_data_copy['parsed_result']
                if hasattr(parsed_result, 'dict'):
                    result_data_copy['parsed_result'] = parsed_result.dict()
                elif hasattr(parsed_result, '__dict__'):
                    result_data_copy['parsed_result'] = parsed_result.__dict__
                    
            result_data_copy['timestamp'] = datetime.now().isoformat()
            self._payment_cache[key] = result_data_copy
            # 同时持久化到文件
            self._save_cache_to_persistence()

    def _save_cache_to_persistence(self):
        """
        将缓存数据持久化到文件
        """
        cache_file = os.path.join(self._instance_folder, 'payment_cache.json')
        try:
            # 使用临时文件和原子操作，防止写入过程中程序崩溃导致数据丢失
            temp_file = cache_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self._payment_cache, f, ensure_ascii=False, indent=2)
            # 原子操作：重命名临时文件为实际文件
            os.replace(temp_file, cache_file)
        except Exception as e:
            print(f"持久化缓存失败: {e}")

    def _load_cache_from_persistence(self):
        """
        从持久化文件加载缓存数据
        """
        # 仅在_payment_cache为空时才加载
        if self._payment_cache and len(self._payment_cache) > 0:
            self.logger.info(f"缓存已存在 {len(self._payment_cache)} 条记录，跳过从文件加载")
            return
        
        cache_file = os.path.join(self._instance_folder, 'payment_cache.json')
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    loaded_cache = json.load(f)
                    
                # 检查加载的数据是否非空，如果是空的也要考虑跳过
                if loaded_cache:
                    self._payment_cache = loaded_cache
                    self.logger.info(f"从持久化文件加载了 {len(self._payment_cache)} 条缓存记录: {cache_file}")
                    
                    # 清理过期的缓存数据（超过24小时的）
                    self._cleanup_expired_cache()
                else:
                    self.logger.info(f"缓存文件为空，初始化为空字典: {cache_file}")
                    self._payment_cache = {}
            else:
                self.logger.info(f"缓存文件不存在，初始化为空字典: {cache_file}")
                self._payment_cache = {}
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"从持久化文件加载缓存失败，可能是文件格式错误: {e}")
            self._payment_cache = {}
        except Exception as e:
            self.logger.error(f"从持久化文件加载缓存失败: {e}")
            self._payment_cache = {}

    def _cleanup_expired_cache(self):
        """
        清理过期的缓存数据
        """
        current_time = datetime.now()
        expired_keys = []
        
        for key, data in self._payment_cache.items():
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
            del self._payment_cache[key]
        
        # 如果删除了过期数据，需要重新保存
        if expired_keys:
            self._save_cache_to_persistence()

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
                # if os.path.exists(config_path):
                #     current_ip = self._get_current_ip_from_config(config_path)
                #     if current_ip != self.ip_address:
                #         self._update_config_ip()
                # else:
                #     # 如果IP文件夹中没有配置文件，从原始位置复制
                #     original_config_path = os.path.join(os.path.dirname(__file__), 'GBunionpay', CONFIG_FILENAME)
                #     if os.path.exists(original_config_path):
                #         shutil.copy2(original_config_path, config_path)
                #         self._update_config_ip()
        except Exception as e:
            print(f"设置IP文件夹时出错: {e}")
            raise

    def _get_current_ip_from_config(self, config_path):
        """
        从配置文件获取当前IP地址
        """
        try:
            config = configparser.ConfigParser()
            # 使用GB2312编码读取配置文件
            with open(config_path, 'r', encoding='gb2312') as f:
                config.read_file(f)
            return config.get('net', 'ipaddr', fallback='')
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return ''

    def _update_config_ip(self):
        """
        更新配置文件中的IP地址，同时保留原有注释和格式，确保等号前后无空格
        """
        config_path = os.path.join(self.ip_folder, CONFIG_FILENAME)
        
        try:
            # 读取原配置文件内容到内存
            with open(config_path, 'r', encoding='gb2312') as f:
                lines = f.readlines()
            
            # 标记是否已更新IP地址
            ip_updated = False
            updated_lines = []
            
            for line in lines:
                # 检查是否是ipaddr行
                if line.strip().startswith('ipaddr='):
                    # 替换ipaddr的值，保持格式
                    updated_lines.append(f'ipaddr={self.ip_address}\n')
                    ip_updated = True
                else:
                    updated_lines.append(line)
            
            # 如果没有找到ipaddr行，则在[net]节下添加
            if not ip_updated:
                # 需要查找[net]节的位置并添加ipaddr
                net_section_found = False
                final_lines = []
                for i, line in enumerate(updated_lines):
                    final_lines.append(line)
                    if line.strip() == '[net]' and not net_section_found:
                        net_section_found = True
                        # 在[net]节后添加ipaddr行
                        final_lines.append(f'ipaddr={self.ip_address}\n')
                
                if not net_section_found:
                    # 如果没有[net]节，则添加该节和ipaddr
                    final_lines.extend(['\n[net]\n', f'ipaddr={self.ip_address}\n'])
                
                updated_lines = final_lines
            
            # 将更新后的内容写回文件
            with open(config_path, 'w', encoding='gb2312') as f:
                f.writelines(updated_lines)
                
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
            # 使用GB2312编码读取配置文件
            with open(config_path, 'r', encoding='gb2312') as f:
                config.read_file(f)
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            raise

    def my_mispos_transaction(self, app_name, trans_id, time_str, json_data):
        """
        MyMisPos接口主函数
        :param app_name: 应用名称
        :param trans_id: 交易类型 03-交易查询 21-余额查询 31-银行卡消费 32-银行卡撤销 34-银行卡退货 35-凭密消费 51-扫码消费 52-扫码撤销 54-扫码退货 61-签到 62-结算 63-结算重打印
        :param time_str: 请求时间 yyyymmddhhmmss
        :param json_data: 入参数据json串
        :return: 返回结果字典
        """
        # 生成缓存键 - 使用trans_id和json_data的某种组合，因为可能没有mer_order_no
        import hashlib
        json_data_hash = hashlib.md5(json_data.encode('utf-8')).hexdigest()
        cache_key = f"my_mispos_{trans_id}_{json_data_hash}"
        # 尝试从缓存获取结果
        cached_result = self._get_payment_result_from_cache(app_name, cache_key)
        if cached_result:
            self.logger.info(f"从缓存返回MyMisPos结果: app_name={app_name}, cache_key={cache_key}")
            return cached_result

        # 获取此特定交易的锁
        transaction_lock = self._get_transaction_lock(app_name, cache_key)
        with transaction_lock:
            # 再次检查缓存
            cached_result = self._get_payment_result_from_cache(app_name, cache_key)
            if cached_result:
                self.logger.info(f"从缓存返回MyMisPos结果: app_name={app_name}, cache_key={cache_key}")
                return cached_result

            
            try:
                # 记录调用日志
                self.logger.info(f"开始调用MyMisPos业务: app_name={app_name}, trans_id={trans_id}, time={time_str}, json_data={json_data}")

                # 将Python字符串转换为C字符串
                s_app_name = ctypes.c_char_p(app_name.encode('utf-8'))
                s_trans_id = ctypes.c_char_p(trans_id.encode('utf-8'))
                s_time = ctypes.c_char_p(time_str.encode('utf-8'))
                s_json_data = ctypes.c_char_p(json_data.encode('utf-8'))
                s_config_path = ctypes.c_char_p(self.ip_folder.encode('utf-8'))

                # 创建输出缓冲区
                out_buffer = ctypes.create_string_buffer(1024)  # 1024字节的缓冲区

                # 调用DLL函数
                result = self.mispos_dll.MyMisPos2(
                    s_app_name,
                    s_trans_id,
                    s_time,
                    s_json_data,
                    s_config_path,
                    out_buffer
                )

                # 解码返回的JSON字符串
                out_data_str = out_buffer.value.decode('gbk') if out_buffer.value else ''

                # 记录返回结果日志
                result_data = {
                    'result': result,
                    'app_name': s_app_name.value.decode('gbk') if s_app_name.value else '',
                    'trans_id': s_trans_id.value.decode('gbk') if s_trans_id.value else '',
                    'time': s_time.value.decode('gbk') if s_time.value else '',
                    'json_data': s_json_data.value.decode('gbk') if s_json_data.value else '',
                    'out_data': out_data_str
                }

                # 解析返回的JSON数据
                parsed_result = None
                try:
                    import json as json_lib
                    if out_data_str:
                        json_result = json_lib.loads(out_data_str)
                        # 将JSON结果转换为MyMisPosResult对象
                        parsed_result = MyMisPosResult(
                            res_code=json_result.get('resCode', ''),
                            res_msg=json_result.get('resMsg', ''),
                            merchant_no=json_result.get('merchantNo', ''),
                            terminal_no=json_result.get('terminalNo', ''),
                            amt=json_result.get('amt', ''),
                            trace_no=json_result.get('traceNo', ''),
                            ref_no=json_result.get('refNo', ''),
                            card_no=json_result.get('cardNo', None),
                            out_trade_no=json_result.get('out_trade_no', None),
                            date=json_result.get('date', None),
                            time=json_result.get('time', None),
                            channel_name=json_result.get('channelName', None),
                            payment_voucher_no=json_result.get('paymentVoucherNo', None),
                            trans_chn_name=json_result.get('transChnName', None),
                            c_psam_id=json_result.get('cPsamId', None),
                            sz_yb_card_no=json_result.get('szYBCardNo', None),
                            s_mer_order_no=json_result.get('sMerOrderNo', None),
                            dct_amount=json_result.get('dctAmount', None),
                            dev_info=json_result.get('devInfo', None),
                            app_name=json_result.get('appName', None),
                            trans_id=json_result.get('transId', None),
                            s_mer_type=json_result.get('sMerType', None),
                            mcht_dct_amount=json_result.get('mchtDctAmount', None),
                            third_party_dct_amount=json_result.get('thirdPartyDctAmount', None)
                        )
                        result_data['parsed_result'] = parsed_result
                except json_lib.JSONDecodeError as e:
                    self.logger.error(f"解析返回的JSON数据失败: {e}, 数据: {out_data_str}")
                    result_data['parsed_result'] = None
                except Exception as e:
                    self.logger.error(f"处理返回数据时出错: {e}")
                    result_data['parsed_result'] = None

                self.logger.info(f"MyMisPos业务调用完成: result={result}, 返回数据={result_data}")

                # 只有交易成功(resCode="00")且json_data不为空时才将结果写入缓存
                if parsed_result and parsed_result.res_code == "00" and json_data:
                    # 将结果存储到缓存中
                    self._store_payment_result_to_cache(app_name, cache_key, result_data)
                else:
                    if not json_data:
                        self.logger.info(f"json_data为空，不存储到缓存: app_name={app_name}, cache_key={cache_key}")
                    else:
                        self.logger.info(f"交易失败或未成功解析结果，不存储到缓存: app_name={app_name}, cache_key={cache_key}")

                return result_data
            except Exception as e:
                self.logger.error(f"调用MyMisPos业务时出错: {e}")
                raise
            




@unionpay_router.post("/gbpayment", response_model=PaymentResponse, summary="广百收款业务接口", description="执行收款业务，处理支付请求")
def payment_api(request: PaymentRequest):
    """
    MyMisPos业务接口
    """
    try:
        
        unionpay = UnionPayDLL(request.ip_address)
        
        result = unionpay.my_mispos_transaction(
            app_name=request.app_name,
            trans_id=request.trans_id,
            time_str=request.time_str,
            json_data=request.json_data
        )
        
        # 检查是否成功解析了返回结果
        parsed_result = result.get('parsed_result')
        if parsed_result and ((hasattr(parsed_result, 'res_code') and parsed_result.res_code == "00") or 
                              (isinstance(parsed_result, dict) and parsed_result.get('res_code') == "00")):
            # 交易成功
            return PaymentResponse(success=True, message="广百收款业务调用成功", data=result)
        else:
            # 交易失败时，返回错误信息
            message = "广百收款业务调用失败"
            if parsed_result:
                if isinstance(parsed_result, dict):
                    message += f": {parsed_result.get('res_msg', '')}"
                else:
                    message += f": {parsed_result.res_msg}"
            return PaymentResponse(success=False, message=message, data=result)
    except Exception as e:
        return PaymentResponse(success=False, message=f"广百收款业务调用失败: {str(e)}")


@unionpay_router.post("/gbbankcard-payment", response_model=PaymentResponse, summary="银行卡收款接口", description="执行银行卡收款业务")
def bankcard_payment_api(request: BankCardPaymentRequest):
    """
    银行卡收款接口
    sAppName固定为01，sTransId固定为31
    """
    # 验证参数，将字符串转换为浮点数进行比较
    if float(request.s_amt) <= 0.00:
        return PaymentResponse(success=False, message="交易金额必须大于0", data=None)
    
    try:
        unionpay = UnionPayDLL(request.ip_address)
        # 构建json_data参数
        json_data = f'{{"sAmt":"{request.s_amt}","sMerOrderNo":"{request.s_mer_order_no}"}}'
        
        result = unionpay.my_mispos_transaction(
            app_name="01",  # 固定为01
            trans_id="31",  # 固定为31
            time_str=request.time_str,
            json_data=json_data
        )
        
        # 检查是否成功解析了返回结果
        parsed_result = result.get('parsed_result')
        if parsed_result and ((hasattr(parsed_result, 'res_code') and parsed_result.res_code == "00") or 
                              (isinstance(parsed_result, dict) and parsed_result.get('res_code') == "00")):
            # 交易成功
            return PaymentResponse(success=True, message="银行卡收款业务调用成功", data=result)
        else:
            # 交易失败时，返回错误信息
            message = "银行卡收款业务调用失败"
            if parsed_result:
                if isinstance(parsed_result, dict):
                    message += f": {parsed_result.get('res_msg', '')}"
                else:
                    message += f": {parsed_result.res_msg}"
            return PaymentResponse(success=False, message=message, data=result)
    except Exception as e:
        return PaymentResponse(success=False, message=f"银行卡收款业务调用失败: {str(e)}")


@unionpay_router.post("/gbbankcard-refund", response_model=PaymentResponse, summary="银行卡退款接口", description="执行银行卡退款业务")
def bankcard_refund_api(request: BankCardRefundRequest):
    """
    银行卡退款接口
    sAppName固定为01，sTransId固定为34（假设为退货交易ID）
    """
    # 验证参数，将字符串转换为浮点数进行比较
    if float(request.s_amt) <= 0.00:
        return PaymentResponse(success=False, message="交易金额必须大于0", data=None)
    
    try:
        unionpay = UnionPayDLL(request.ip_address)
        # 构建json_data参数
        json_data = f'{{"sAmt":"{request.s_amt}","sOrgTraceNo":"{request.s_org_trace_no}","sDt":"{request.s_dt}","sMerOrderNo":"{request.s_mer_order_no}"}}'
        
        result = unionpay.my_mispos_transaction(
            app_name="01",  # 固定为01
            trans_id="34",  # 固定为34（银行卡退货）
            time_str=request.time_str,
            json_data=json_data
        )
        
        # 检查是否成功解析了返回结果
        parsed_result = result.get('parsed_result')
        if parsed_result and ((hasattr(parsed_result, 'res_code') and parsed_result.res_code == "00") or 
                              (isinstance(parsed_result, dict) and parsed_result.get('res_code') == "00")):
            # 交易成功
            return PaymentResponse(success=True, message="银行卡退款业务调用失败", data=result)
        else:
            # 交易失败时，返回错误信息
            message = "银行卡退款业务调用失败"
            if parsed_result:
                if isinstance(parsed_result, dict):
                    message += f": {parsed_result.get('res_msg', '')}"
                else:
                    message += f": {parsed_result.res_msg}"
            return PaymentResponse(success=False, message=message, data=result)
    except Exception as e:
        return PaymentResponse(success=False, message=f"银行卡退款业务调用失败: {str(e)}")


@unionpay_router.post("/gbscancode-payment", response_model=PaymentResponse, summary="扫码收款接口", description="执行扫码收款业务")
def scancode_payment_api(request: ScanCodePaymentRequest):
    """
    扫码收款接口
    sAppName固定为01，sTransId固定为51（扫码消费）
    """
    # 验证参数，将字符串转换为浮点数进行比较
    if float(request.s_amt) <= 0.00:
        return PaymentResponse(success=False, message="交易金额必须大于0", data=None)
    
    # 验证支付渠道参数
    if request.s_type not in ["01", "02","00"]:
        return PaymentResponse(success=False, message="支付渠道参数错误：01—支付宝,02—微信,00-全部", data=None)
    
    try:
        unionpay = UnionPayDLL(request.ip_address)
        # 构建json_data参数
        json_data = f'{{"sAmt":"{request.s_amt}","sType":"{request.s_type}","sMerOrderNo":"{request.s_mer_order_no}","qrcode":"{request.qrcode}"}}'
        
        result = unionpay.my_mispos_transaction(
            app_name="04",  # 固定为04
            trans_id="51",  # 固定为51（扫码消费）
            time_str=request.time_str,
            json_data=json_data
        )
        
        # 检查是否成功解析了返回结果
        parsed_result = result.get('parsed_result')
        if parsed_result and ((hasattr(parsed_result, 'res_code') and parsed_result.res_code == "00") or 
                              (isinstance(parsed_result, dict) and parsed_result.get('res_code') == "00")):
            # 交易成功
            return PaymentResponse(success=True, message="扫码收款业务调用成功", data=result)
        else:
            # 交易失败时，返回错误信息
            message = "扫码收款业务调用失败"
            if parsed_result:
                if isinstance(parsed_result, dict):
                    message += f": {parsed_result.get('res_msg', '')}"
                else:
                    message += f": {parsed_result.res_msg}"
            return PaymentResponse(success=False, message=message, data=result)
    except Exception as e:
        return PaymentResponse(success=False, message=f"扫码收款业务调用失败: {str(e)}")


@unionpay_router.post("/gbscancode-refund", response_model=PaymentResponse, summary="扫码退款接口", description="执行扫码退款业务")
def scancode_refund_api(request: ScanCodeRefundRequest):
    """
    扫码退款接口
    sAppName固定为01，sTransId固定为54（扫码退货）
    """
    # 验证参数，将字符串转换为浮点数进行比较
    if float(request.s_amt) <= 0.00:
        return PaymentResponse(success=False, message="交易金额必须大于0", data=None)
    
    # 验证支付渠道参数
    if request.s_type not in ["01", "02", "00"]:
        return PaymentResponse(success=False, message="支付渠道参数错误：01—支付宝,02—微信,00-全部", data=None)
    
    try:
        unionpay = UnionPayDLL(request.ip_address)
        # 构建json_data参数
        json_data = f'{{"sAmt":"{request.s_amt}","sType":"{request.s_type}","sOrgTraceNo":"{request.s_org_trace_no}","sDt":"{request.s_dt}","sRefNo":"{request.s_ref_no}","sMerOrderNo":"{request.s_mer_order_no}","qrcode":"{request.qrcode}"}}'
        
        result = unionpay.my_mispos_transaction(
            app_name="04",  # 固定为04
            trans_id="54",  # 固定为54（扫码退货）
            time_str=request.time_str,
            json_data=json_data
        )
        
        # 检查是否成功解析了返回结果
        parsed_result = result.get('parsed_result')
        if parsed_result and ((hasattr(parsed_result, 'res_code') and parsed_result.res_code == "00") or 
                              (isinstance(parsed_result, dict) and parsed_result.get('res_code') == "00")):
            # 交易成功
            return PaymentResponse(success=True, message="扫码退款业务调用成功", data=result)
        else:
            # 交易失败时，返回错误信息
            message = "扫码退款业务调用失败"
            if parsed_result:
                if isinstance(parsed_result, dict):
                    message += f": {parsed_result.get('res_msg', '')}"
                else:
                    message += f": {parsed_result.res_msg}"
            return PaymentResponse(success=False, message=message, data=result)
    except Exception as e:
        return PaymentResponse(success=False, message=f"扫码退款业务调用失败: {str(e)}")


@unionpay_router.get("/health", summary="健康检查接口", description="检查服务是否健康运行")
def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy", "service": "unionpay"}
