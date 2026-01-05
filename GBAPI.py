"""
广百API接口模块
广百API调用
"""
from fastapi import APIRouter, Body, HTTPException, Query
from datetime import datetime
import fastapi
import requests
import json
import uuid
from typing import Optional, Dict
import config
import time
from GBModel import BaseResponse

from db import GetGBConfig, SaveSupplyInfo

BASE_URL = config.GBAPI_CONFIG["BASE_URL"]
APPID = config.GBAPI_CONFIG["APPID"]
APPKEY = config.GBAPI_CONFIG["APPKEY"]

TOKEN = "" # api token
TOKEN_EXPIRE_TIME = 0  # api token 将会过期的时间
ShopConfig = {} # 店铺配置缓存


# 创建广百API路由器
gb_router = APIRouter(prefix="/gb", tags=["广百接口"])


# 获取店铺配置
def get_gb_config(shopid:str, crid:str):
    keyStr = f'{shopid}_{crid}'
    if keyStr in ShopConfig:
        return ShopConfig[keyStr]
    configData = GetGBConfig(shopid, crid)
    if configData and isinstance(configData, list):
        ShopConfig[keyStr] = configData[0]
        return configData[0]


# 获取每次接口请求的requestid
def get_request_id():
    # 广百接口request_id最大长度是32
    return str(uuid.uuid4()).replace('-','')


# 获取日结时的日结单号
def get_gb_settlement_dh_cnt(cashierId: str, cnt: int):
    """
    生成编码：年月日 + 收款员号 + 序列号
    
    Parameters:
    - cashier_id: 收款员号
    - cnt: 日结次数
    
    Returns:
    - 生成的编码字符串
    """
    # 1. 获取日期部分
    date_part = datetime.now().strftime("%Y%m%d")
    
    # 2. 获取收款员号部分
    cashier_part = cashierId
    
    # 3. 生成序列号（基于日结次数）
    # 序列号格式可以根据需求调整，比如固定4位
    seq_part = str(cnt).zfill(4)  # 左补零到4位
    
    # 4. 拼接编码
    code = f"{date_part}{cashier_part}{seq_part}"
    
    return code


# 获取日结时的日结单号
def get_gb_settlement_dh_seq(cashierId: str, seq: str):
    """
    生成编码：年月日 + 收款员号 + 序列号
    
    Parameters:
    - cashier_id: 收款员号
    - seq: 日结序号, 需要是3位长度
    
    Returns:
    - 生成的编码字符串
    """
    # 1. 获取日期部分
    date_part = datetime.now().strftime("%Y%m%d")
    
    # 2. 拼接编码
    code = f"{date_part}{cashierId}{seq}"
    
    return code

# 可信验签接口
def client_token():
    """
    可信验签接口
    接口说明：该接口用于验证调用方身份，生成鉴权token，调用其他接口时需在请求头携带token，token有效期1小时。

    Args:
        
    Returns:
        字典格式的响应数据或错误信息
    """

    url = BASE_URL + "/openapi/oauth/clientToken"
    param = {
        "appId": APPID,
        "appKey": APPKEY,
    }
    response = post(url=url, param=param)
    return response


@gb_router.get("/reset-gbapi-token", summary="重置接口Token缓存", response_model=BaseResponse)
def reset_gbapi_token():
    global TOKEN
    global TOKEN_EXPIRE_TIME
    TOKEN = ""
    TOKEN_EXPIRE_TIME = 0


@gb_router.get("/reset-gb-config", summary="重置广百店铺配置缓存", response_model=BaseResponse)
def reset_gb_config():
    global StoreConfig
    StoreConfig = {}


@gb_router.get("/find-member-info-brand", summary="会员识别接口",  response_model=BaseResponse)
#def find_member_info_brand(request: FindMemberInfoBrandRequest = Body(...)):
def find_member_info_brand(
    memberNo: str = Query(..., description="会员卡号/会员码/手机号"),
    ):
    """
    会员识别接口
    接口说明：识别广百会员身份，以及获取会员基本信息。

    Args:
        memberNo: 会员卡号/会员码/手机号
    
    Returns:
        字典格式的响应数据或错误信息
    """

    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/member-api/memberApi/findmemberinfobrand"
        param = {
            "data": {
                "strCustomer" : memberNo
            },
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/query-xfk-info", summary="积分卡查询接口", response_model=BaseResponse)
def query_xfk_info(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    couponNum: str = Query(..., description="优惠券号"),
):
    """
    广百积分卡查询接口
    接口说明：识别广百积分卡，查询积分卡余额、卡号。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/queryXfkInfo"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": '1',
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vtrack2": couponNum,
            "vcardbrand": '201',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/pay-with-xfk", summary="积分卡核销接口", response_model=BaseResponse)
def pay_with_xfk(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    orderNo: str = Query(..., description="销售小票号"),
    orderSeq: str = Query(..., description="3位序列号, 用来组成交易流水号"),
    couponNum: str = Query(..., description="优惠券号"),
    amount: float = Query(..., description="交易金额"),
):
    """
    广百积分卡核销接口
    接口说明：广百积分卡核销，核销金额不得大于积分卡余额。若交易未完成，支持原路退回，不支持售后退款。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/payWithXfk"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": orderNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vtrack2": couponNum,
            "vcardbrand": '201',
            "vtype": '01',
            "vseqno": shopConfig['storeNo'] + orderNo + orderSeq,
            "vje": amount,
            "requestId": get_request_id(),
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/xfk-writeoff-cancel", summary="积分卡冲正接口", response_model=BaseResponse)
def xfk_writeoff_cancel(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    orderNo: str = Query(..., description="销售小票号"),
    currentOrderSeq: str = Query(..., description="当前交易3位序列号, 用来组成交易流水号"),
    couponNum: str = Query(..., description="优惠券号"),
    amount: float = Query(..., description="交易金额"),
    originalOrderSeq: str = Query(..., description="原先交易订单的3位序列号, 用来组成原交易流水号"),
):
    """
    广百积分卡冲正接口
    接口说明：广百积分卡冲正，销售小票已核销金额原路退回，不支持售后退款。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/xfkWriteOffCancel"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": orderNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vtrack2": couponNum,
            "vcardbrand": '201',
            "vtype": '02',
            "vseqno": shopConfig['storeNo'] + orderNo + currentOrderSeq,
            "vje": amount,
            "vmemo": shopConfig['storeNo'] + orderNo + originalOrderSeq,
            "requestId": get_request_id(),
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/get-xfk-trade-comfirm-info", summary="积分卡交易确认接口", response_model=BaseResponse)
def get_xfk_trade_comfirm_info(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    orderNo: str = Query(..., description="销售小票号"),
):
    """
    广百积分卡交易确认接口
    接口说明：可用于查询小票的交易信息，核对双方金额是否一致。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ibusiness/v2/xfk/getXfkTradeComfirmInfo"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": orderNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vcardbrand": '201',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/xfk-settlement", summary="积分卡日结接口", response_model=BaseResponse)
def xfk_settlement(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    settlementSeq: int = Query(..., description="日结序号，需要是3位长度的序号"),
):
    """
    广百积分卡日结接口
    接口说明：收款员交班时结算积分卡数据，汇总交易笔数及金额。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/settlement/v2/xfkSettlement"
        param = {
            "storeNo": shopConfig['storeNo'],
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vcardbrand": '201',
            "dh" : get_gb_settlement_dh_seq(shopConfig['cashierId'], settlementSeq),
            "companyCode" : 'GB',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/query-by-tmq", summary="条码现金券查询接口", response_model=BaseResponse)
def query_by_tmq(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    CouponNum: str = Query(..., description="优惠券号"),
):
    """
    广百条码现金券查询接口
    接口说明：识别条码现金券，查询条码现金券余额。仅支持广百条码现金券。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/queryByTmq"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": '1',
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vtrack2": CouponNum,
            "vcardbrand": '201',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/pay-with-tmq", summary="条码现金券核销接口", response_model=BaseResponse)
def pay_with_tmq(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    orderNo: str = Query(..., description="销售小票号"),
    orderSeq: str = Query(..., description="3位序列号, 用来组成交易流水号"),
    couponNum: str = Query(..., description="优惠券号"),
    amount: float = Query(..., description="交易金额"),
):
    """
    条码现金券核销接口
    接口说明：条码现金券核销，需一次性抵扣剩余金额，不得分次核销。若交易未完成，支持原路退回，不支持售后退款。仅支持广百条码现金券。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/payWithTmq"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": orderNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vtrack2": couponNum,
            "vcardbrand": '201',
            "vtype": '01',
            "vseqno": shopConfig['storeNo'] + orderNo + orderSeq,
            "vje": amount,
            "requestId": get_request_id(),
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/return-with-tmq", summary="条码现金券冲正接口", response_model=BaseResponse)
def return_with_tmq(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    orderNo: str = Query(..., description="销售小票号"),
    currentOrderSeq: str = Query(..., description="当前交易3位序列号, 用来组成交易流水号"),
    couponNum: str = Query(..., description="优惠券号"),
    amount: float = Query(..., description="交易金额"),
    originalOrderSeq: str = Query(..., description="原先交易订单的3位序列号, 用来组成原交易流水号"),
):
    """
    条码现金券冲正接口
    接口说明：条码现金券冲正，销售小票已核销金额原路退回，不支持售后退款。仅支持广百条码现金券。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/returnWithTmq"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": orderNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vtrack2": couponNum,
            "vcardbrand": '201',
            "vtype": '201',
            "vseqno": shopConfig['storeNo'] + orderNo + currentOrderSeq,
            "vje": amount,
            "vmemo": shopConfig['storeNo'] + orderNo + originalOrderSeq,
            "requestId": get_request_id,
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/get-tmq-trade-confirm-info", summary="条码现金券交易确认接口", response_model=BaseResponse)
def get_tmq_trade_confirm_info(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    orderNo: str = Query(..., description="销售小票号"),
):
    """
    条码现金券交易确认接口
    接口说明：可用于查询小票的交易信息，核对双方金额是否一致。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ibusiness/v2/xfk/getTmqTradeComfirmInfo"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": orderNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vcardbrand": '201',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/tmq-settlement", summary="条码现金券日结接口", response_model=BaseResponse)
def tmq_settlement(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    settlementSeq: int = Query(..., description="日结序号，需要是3位长度的序号"),
):
    """
    条码现金券日结接口
    接口说明：收款员交班时结算条码现金券数据，汇总交易笔数及金额。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/settlement/v2/tmqSettlement"
        param = {
            "storeNo": shopConfig['storeNo'],
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "vcardbrand": '201',
            "dh" : get_gb_settlement_dh_seq(shopConfig['cashierId'], settlementSeq),
            "companyCode" : 'GB',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/get-supply-info", summary="专柜数据接口", response_model=BaseResponse)
def get_supply_info(
    supplyId: str = Query(..., description="供应商编号"),
):
    """
    专柜数据接口
    接口说明：该接口可通过供应商编号查询广百侧定义的门店、商场、专柜、收款员数据，为后续订单推送、支付等业务提供基础数据。
    """
    try:
        if not supplyId:
            return BaseResponse(
                success = False,
                code=0,
                data=None,
                message=f'供应商编号不能为空'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/erp-api/gberp/outter/getSupplyInfo"
        param = {
            "supplyId": supplyId
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1: # 成功
            saveResponse = SaveSupplyInfo(result['data'])
            if saveResponse['success'] == True:
                return BaseResponse(
                    success=True,
                    code=1,
                    data=None,
                    message=''
                )
            else:
                return BaseResponse(
                    success=False,
                    code=0,
                    data=None,
                    message=saveResponse.get('Message', '保存数据失败')
                )
        else:
            return BaseResponse(
                success = False,
                code=0,
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=BaseResponse(
                success=False,
                code=-1,
                message=f"接口调用异常: {str(e)}"
            ).dict()
        )


@gb_router.get("/points-query", summary="积分查询接口", response_model=BaseResponse)
def points_query(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    memberNo: str = Query(..., description="会员卡号"),
):
    """
    积分查询接口
    接口说明：识别支付二维码，查询会员积分余额及使用规则，使用积分时需符号特定规则。
    例如，人民币：积分兑换率为1：100，积分兑换倍数为10000，即积分支付只能为10000的倍数，对照到人民币即只能是100的倍数；最低起付为20000，即支付金额不能小于200；
    当前可用积分为36849，即支付金额不能大于300。以上数值均为举例，具体数额需通过接口获取。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/points/query"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": '',
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "bisCode": '801',
            "cardNo": memberNo,
            "companyCode": 'GB',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/points-deal", summary="积分支付、撤销、退货接口", response_model=BaseResponse)
def points_deal(
    shopid: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    invoiceNo: str = Query(..., description="广百（广百格式）销售小票号"),
    amount: float = Query(..., description="交易金额，均为正值"),
    dealCode: str = Query(..., description="支付二维码"),
    memberCard: str = Query(..., description="会员卡号"),
    type: int = Query(..., description="业务类型，1-消费 2-撤销 3-售后退款"),
    shtxdt: str = Query(..., description="支付时间"),
    returnInvoiceNo: str = Query(None, description="退货小票号"),
):
    """
    积分支付、撤销、退货接口
    接口说明：识别支付二维码，积分支付时支付金额需符合特定规则，且一笔交易只能使用一次。若交易未完成，支持原路退回，支持售后退款，售后不支持撤销。
    """
    try:
        if not shopid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopid, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopid}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/points/deal"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": invoiceNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "amt": amount,
            "dealCode": dealCode,
            "cardNo": memberCard,
            "bisCode": '801',
            "type": type,
            "flag":  -1 if type == 1 else 1,
            "posDate": shtxdt,
            "requestId": get_request_id(),
            "companyCode": 'GB',
            "channelId": '31',
            "afterSaleNo": returnInvoiceNo,
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/points-tradeQuery", summary="积分支付交易确认接口", response_model=BaseResponse)
def points_tradeQuery(
    Shopid: str = Query(..., description="门店编号"),
    Crid: str = Query(..., description="机器号"),
    InvoiceNo: str = Query(..., description="销售小票号"),
    MemberCard: str = Query(..., description="会员卡号"),
):
    """
    积分支付交易确认接口
    接口说明：可用于查询小票的交易信息，核对双方金额是否一致。
    """
    try:
        if not Shopid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not Crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(Shopid, Crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{Shopid}|{Crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/points/tradeQuery"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": InvoiceNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "biscode": '801',
            "cardNo": MemberCard,
            "companyCode": 'GB',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/points-settlement", summary="积分支付日结接口", response_model=BaseResponse)
def points_settlement(
    Shopid: str = Query(..., description="门店编号"),
    Crid: str = Query(..., description="机器号"),
    SettlementSeq: str = Query(..., description="日结序号，需要是3位长度的序号"),
):
    """
    积分支付日结接口
    接口说明：收款员交班时结算积分支付数据，汇总交易笔数及金额。
    """
    try:
        if not Shopid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not Crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(Shopid, Crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{Shopid}|{Crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/points/settlement"
        param = {
            "storeNo": shopConfig['storeNo'],
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "biscode": '801',
            "companyCode": 'GB',
            "dh": get_gb_settlement_dh_seq(shopConfig['cashierId'], SettlementSeq),
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/eacc-queryBalance", summary="电子账户查询接口", response_model=BaseResponse)
def eacc_queryBalance(
    shopID: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    memberNo: str = Query(..., description="会员卡号"),
    dealCode: str = Query(..., description="会员支付二维码")
):
    """
    电子账户查询接口
    接口说明：识别支付二维码，查询电子账户余额。
    """
    try:
        if not shopID:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopID, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopID}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/eacc/queryBalance"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": '',
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "dealCode": dealCode,
            "cardNo": memberNo,
            "companyCode": 'GB',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/eacc-deal", summary="电子账户支付、撤销、退货接口", response_model=BaseResponse)
def eacc_deal(
    shopid: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    invoiceNo: str = Query(..., description="广百（广百格式）销售小票号"),
    amount: float = Query(..., description="交易金额，均为正值"),
    dealCode: str = Query(..., description="支付二维码"),
    memberCard: str = Query(..., description="会员卡号"),
    type: int = Query(..., description="业务类型，1-消费 2-撤销 3-售后退款"),
    shtxdt: str = Query(..., description="支付时间"),
    returnInvoiceNo: str = Query(None, description="退货小票号"),
):
    """
    电子账户支付、撤销、退货接口
    接口说明：查询时缓存支付二维码，支付时直接获取，避免二次扫码。电子账户交易系统内部按优先级依次抵扣现金金额、积分卡金额、赠送金额，并返回对应的抵扣金额，
    需根据抵扣金额拆分为三个支付方式。一笔交易只能使用一次。若交易未完成，支持原路退回，支持售后退款，售后不支持撤销。
    """
    try:
        if not shopid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopid, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopid}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/eacc/deal"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": invoiceNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "amt": amount,
            "dealCode": dealCode,
            "cardNo": memberCard,
            "bisCode": '801',
            "type": type,
            "flag": -1 if type == 5 else 1,
            "sysdate": shtxdt,
            "requestId": get_request_id(),
            "companyCode": 'GB',
            "channelId": '31',
            "afterSaleNo": returnInvoiceNo,
        }

        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/eacc-get-trade-comfirm-info", summary="电子账户交易确认接口", response_model=BaseResponse)
def eacc_get_trade_comfirm_info(
    shopid: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    invoiceNo: str = Query(..., description="销售小票号"),
    type: int = Query(..., description="消费类型，消费：-1，撤销或售后：1"),
):
    """
    电子账户交易确认接口
    接口说明：可用于查询小票的交易信息，核对双方金额是否一致。
    """
    try:
        if not shopid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopid, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopid}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/eacc/getTradeComfirmInfo"
        param = {
            "storeNo": shopConfig['storeNo'],
            "orderNo": invoiceNo,
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "bisCode": '801',
            "flag": type,
            "companyCode": 'GB',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/eacc-daily-Settlement", summary="电子账户日结接口", response_model=BaseResponse)
def eacc_daily_Settlement(
    shopid: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    settlementSeq: str = Query(..., description="日结序号，需要是3位长度的序号")
):
    """
    电子账户日结接口
    接口说明：收款员交班时结算电子账户数据，汇总交易笔数及金额。
    """
    try:
        if not shopid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        if not crid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='设备ID不能为空'
            )

        shopConfig = get_gb_config(shopid, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopid}|{crid}]'
            )

        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/eacc/dailySettlement"
        param = {
            "storeNo": shopConfig['storeNo'],
            "cashierId": shopConfig['cashierId'],
            "terminalId": shopConfig['storeNo'] + shopConfig['terminalId'],
            "bisCode": '801',
            "dh": get_gb_settlement_dh_seq(shopConfig['cashierId'], settlementSeq),
            "companyCode": 'GB',
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )


@gb_router.get("/", summary="商品推送接口", response_model=BaseResponse)
def push_products(
    shopid: str = Query(..., description="门店编号"),
    crid: str = Query(..., description="机器号"),
    settlementCnt: str = Query(..., description="日结次数"),
):
    """
    商品推送接口
    接口说明：品牌方通过该接口同步商品数据，以及操作商品上架、下架；商品明细资料由品牌方提供，操作码等广百方基础资料由专柜数据接口获取。

    Args:\n
        shopid: 门店编号\n
        crid: 机器号\n
        settlementCnt: 日结次数\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        if not shopid:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message='店铺ID不能为空'
            )

        shopConfig = get_gb_config(shopid, crid)

        if not shopConfig:
            return BaseResponse(
                success=False,
                code=0,
                data=None,
                message=f'获取店铺_机器配置为空，请检查店铺配置[{shopid}|{crid}]'
            )

        # 获取要同步的商品数据
        products = {}


        # 解析参数并调用接口
        url = BASE_URL + "/openapi/product-api/outter/pushProducts"
        param = {
            "supplyid": '',
            "czm": '',
            "poshh": '',
            "posname": '',
            "poslbmc": '',
            "taxRate": '',
            "createdbyid": '',
            "mdbm": '',
            "scbm": '',
            "zgbm": '',
            "products": products,
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponse(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            return BaseResponse(
                success=False,
                code=result["code"],
                data=None,
                message=result.get("message", "请求失败")
            )
    except Exception as e:
        return BaseResponse(
            success=False,
            code=-1,
            data=None,
            message=f"接口调用异常: {str(e)}"
        )




def gb_post(url: str, param: Optional[Dict[str, str]]):
    """
    向第三方接口发送POST请求
    请求TOKEN自动获取

    Args:
        url: 完整的API地址
        data: 请求参数
    
    Returns:
        字典格式的响应数据或错误信息
    """
    
    global TOKEN, TOKEN_EXPIRE_TIME  

    retry_count = 0
    max_retries = 1  # 最多重试一次
    
    while True:
        current_time = time.time()
        if (TOKEN == ""  or current_time >= TOKEN_EXPIRE_TIME - 300):
            write_info_log("TOKEN为空或即将过期，正在获取新TOKEN...")
            getTokenResponse = client_token()

            if getTokenResponse["code"] < 1:
                message = getTokenResponse["message"]
                # 这里如果报错是TOken过期的话，可以自动重取一下TOKEN，然后再Retry一次接口
                return get_api_response(0, f"获取接口TOKEN失败：{message}")
            else:
                responseData = getTokenResponse["data"]
                if responseData.get("accessToken"):
                    TOKEN = responseData["accessToken"]
                    # 设置TOKEN过期时间（1小时有效期）
                    TOKEN_EXPIRE_TIME = current_time + 3600
                    write_info_log(f"获取新TOKEN: {TOKEN[:20]}...")
                else:
                    return get_api_response(0, f"获取接口TOKEN失败：返回数据中找不到accessToken")
        
        post_headers = {
            "accessToken": TOKEN
        }

        response = post(url, param, post_headers)

        # 检查是否是TOKEN过期错误
        if response["code"] < 1 and "token授权过期" in response["message"].lower() and retry_count < max_retries:
            write_info_log(f"检测到TOKEN过期，正在进行第 {retry_count + 1} 次重试...")
            write_info_log(f"原始错误信息: {response['message']}")

            # 清空TOKEN
            TOKEN = ""
            TOKEN_EXPIRE_TIME = 0

            retry_count += 1

            # 上面清空了TOKEN，然后循环一次获取token后再次调用接口
            continue

        return response


def post(url: str, param: Optional[Dict[str, str]], headers: Optional[Dict[str, str]]=None):
    """
    发送POST请求
    方法封装了http post 请求和对接口返回数据的初步校验

    Args:
        url: 完整的API地址
        headers: 请求头，包含token等信息
        data: 请求参数
    
    Returns:
        字典格式的响应数据或错误信息
    """
    
    try:
        # 设置默认请求头
        default_headers = {
            'Content-Type': 'application/json'
        }

        # 合并自定义请求头
        if headers:
            default_headers.update(headers)

        # 发送 POST 请求
        response = requests.post(
            url=url,
            headers=default_headers,
            json=param
        )

        response.raise_for_status()
        
        # 解析 JSON 响应
        data = response.json()
        write_info_log(data)
        if data.get("code") == 200 and (data.get("subCode") == 1 or data.get("subCode") == 6000):
            return get_api_response(1, "", data.get("data"))
        else:
            if data.get("code") != 200:
                message = f"接口请求失败：{data.get('code')}|{data.get('msg')}\n{data.get('subCode')}|{data.get('subMsg')}"
                return get_api_response(0, message)
            else :
                message = f"接口请求获取业务失败：{data.get('subCode')}|{data.get('subMsg')}"
                return get_api_response(0, message)

    except requests.exceptions.Timeout:
        message = f"接口请求超时"
        write_info_log(message)
        return get_api_response(-1, message)
    except requests.exceptions.HTTPError as e:
        message = f"HTTP错误: {e}"
        write_info_log(message)
        return get_api_response(-1, message)
    except requests.exceptions.ConnectionError:
        message = "连接错误"
        write_info_log(message)
        return get_api_response(-1, message)
    except requests.exceptions.RequestException as e:
        message = f"请求异常: {e}"
        write_info_log(message)
        return get_api_response(-1, message)
    except json.JSONDecodeError:
        message = f"应不是有效的JSON格式"
        write_info_log(message)
        return get_api_response(-1, message)
    except Exception as e:
        message = f"出现异常：{e}"
        write_info_log(message)
        return get_api_response(-1, message)


def get_api_response(code : int, message : str, data : any = None):
    """
    获取API接口返回实体，定义接口成功 code 为 1， 失败 code 为 0， 接口异常 code 为 -1
    
    Args:
        code: 1 成功 0 失败 -1 异常
        message: 失败/异常 提示信息
        data: 接口返回数据
    
    Returns:
        字典格式的响应数据或错误信息
    """

    return {"code": code, "message" : message, "data" : data}


def write_info_log(message : str):
    print(message)
