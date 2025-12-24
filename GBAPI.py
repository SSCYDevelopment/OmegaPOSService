"""
广百API接口模块
广百API调用
"""
from fastapi import APIRouter, Body, HTTPException
import requests
import json
from typing import Optional, Dict
import config
import time
from GBModel import BaseResponse, FindMemberInfoBrandRequest, QueryXfkInfoRequest, PayWithXfkRequest, XfkWriteoffCancelRequest, GetXfkTradeConfirmInfoRequest, XfkSettlementRequest
from GBModel import QueryByTmqRequest, PayWithTmqRequest, ReturnWithTmqRequest, GetTmqTradeConfirmInfoRequest, TmqSettlementRequest, GetSupplyInfo, BaseResponseByListData
from GBModel import PointsQueryRequest, PointsDealRequest, PointsTradeQueryRequest, PointsSettlementRequest, EaccQueryBalanceRequest, EaccDealRequest, EaccGetTradeComfirmInfo, EaccDailySettlementRequest

BASE_URL = config.GBAPI_CONFIG["BASE_URL"]
APPID = config.GBAPI_CONFIG["APPID"]
APPKEY = config.GBAPI_CONFIG["APPKEY"]

TOKEN = "" # api token
TOKEN_EXPIRE_TIME = 0  # api token 将会过期的时间

# 创建广百API路由器
gb_router = APIRouter(prefix="/gb", tags=["广百接口"])

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

@gb_router.post("/reset-gbapi-token", summary="重置接口Token缓存", response_model=BaseResponse)
def reset_gbapi_token():
    global TOKEN
    global TOKEN_EXPIRE_TIME
    TOKEN = ""
    TOKEN_EXPIRE_TIME = 0


@gb_router.post("/find-member-info-brand", summary="会员识别接口",  response_model=BaseResponse)
def find_member_info_brand(request: FindMemberInfoBrandRequest = Body(...)):
    """
    会员识别接口
    接口说明：识别广百会员身份，以及获取会员基本信息。

    Args:
        strCustomer: 会员卡号/会员码/手机号
    
    Returns:
        字典格式的响应数据或错误信息
    """

    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/member-api/memberApi/findmemberinfobrand"
        param = {
            "data": {
                "strCustomer" : request.strCustomer
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/query-xfk-info", summary="积分卡查询接口", response_model=BaseResponse)
def query_xfk_info(request: QueryXfkInfoRequest = Body(...)):
    """
    积分卡查询接口
    接口说明：识别积分卡，查询积分卡余额、卡号。广百、友谊积分卡无法通过数据区分，收款前端需分开广百、友谊两个入口，并传输相应的 vcardbrand 参数。

    Args:
        storeNo: 门店编号
        orderNo：销售小票号
        cashierId：收款员号
        terminalId：授权终端号，4位门店号+5位收款终端号
        vtrack2：磁道信息，刷卡获取的内容
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡

    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/queryXfkInfo"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vtrack2": request.vtrack2,
            "vcardbrand": request.vcardbrand,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/pay-with-xfk", summary="积分卡核销接口", response_model=BaseResponse)
def pay_with_xfk(request: PayWithXfkRequest = Body(...)):
    """
    积分卡核销接口
    接口说明：积分卡核销，核销金额不得大于积分卡余额。若交易未完成，支持原路退回，不支持售后退款。广百、友谊积分卡无法通过数据区分，收款前端需分开广百、友谊两个入口，并传输相应的 vcardbrand 参数。
    
    Args:
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        vtrack2：磁道信息，刷卡获取的内容\n
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡\n
        vtype：交易类型，默认 01\n
        vseqno：交易流水号，4位门店号+小票号+3位序列号\n
        vje：交易金额\n
        requestId：交易请求ID，一次交易行为的唯一标识\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/payWithXfk"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vtrack2": request.vtrack2,
            "vcardbrand": request.vcardbrand,
            "vtype": request.vtype,
            "vseqno": request.vseqno,
            "vje": request.vje,
            "requestId": request.requestId,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/xfk-writeoff-cancel", summary="积分卡冲正接口", response_model=BaseResponse)
def xfk_writeoff_cancel(request: XfkWriteoffCancelRequest = Body(...)):
    """
    积分卡冲正接口
    接口说明：积分卡冲正，销售小票已核销金额原路退回，不支持售后退款。广百、友谊积分卡无法通过数据区分，收款前端需分开广百、友谊两个入口，并传输相应的 vcardbrand 参数。

    Args:
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        vtrack2：磁道信息，刷卡获取的内容\n
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡\n
        vtype：交易类型，默认 01\n
        vseqno：交易流水号，4位门店号+小票号+3位序列号\n
        vje：交易金额\n
        vmemo：原交易流水号\n
        requestId：交易请求ID，一次交易行为的唯一标识\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/xfkWriteOffCancel"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vtrack2": request.vtrack2,
            "vcardbrand": request.vcardbrand,
            "vtype": request.vtype,
            "vseqno": request.vseqno,
            "vje": request.vje,
            "vmemo": request.vmemo,
            "requestId": request.requestId,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/get-xfk-trade-comfirm-info", summary="积分卡交易确认接口", response_model=BaseResponse)
def get_xfk_trade_comfirm_info(request: GetXfkTradeConfirmInfoRequest = Body(...)):
    """
    积分卡交易确认接口
    接口说明：可用于查询小票的交易信息，核对双方金额是否一致。

    Args:
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ibusiness/v2/xfk/getXfkTradeComfirmInfo"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vcardbrand": request.vcardbrand,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/xfk-settlement", summary="积分卡日结接口", response_model=BaseResponse)
def xfk_settlement(request: XfkSettlementRequest = Body(...)):
    """
    积分卡日结接口
    接口说明：收款员交班时结算积分卡数据，汇总交易笔数及金额。广百、友谊积分卡需分两次结算。

    Args:\n
        storeNo: 门店编号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡\n
        dh：日结单号，年月日+收款员号+序列号\n
        companyCode：企业编码，GB：广百\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/settlement/v2/xfkSettlement"
        param = {
            "storeNo": request.storeNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vcardbrand": request.vcardbrand,
            "dh" : request.dh,
            "companyCode" : request.companyCode,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/query-by-tmq", summary="条码现金券查询接口", response_model=BaseResponse)
def query_by_tmq(request: QueryByTmqRequest = Body(...)):
    """
    条码现金券查询接口
    接口说明：识别条码现金券，查询条码现金券余额。仅支持广百条码现金券。

    Args:
        storeNo: 门店编号
        orderNo：销售小票号
        cashierId：收款员号
        terminalId：授权终端号，4位门店号+5位收款终端号
        vtrack2：磁道信息，刷卡获取的内容
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡

    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/queryByTmq"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vtrack2": request.vtrack2,
            "vcardbrand": request.vcardbrand,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/pay-with-tmq", summary="条码现金券核销接口", response_model=BaseResponse)
def pay_with_tmq(request: PayWithTmqRequest = Body(...)):
    """
    条码现金券核销接口
    接口说明：条码现金券核销，需一次性抵扣剩余金额，不得分次核销。若交易未完成，支持原路退回，不支持售后退款。仅支持广百条码现金券。
    
    Args:
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        vtrack2：磁道信息，刷卡获取的内容\n
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡\n
        vtype：交易类型，默认 01\n
        vseqno：交易流水号，4位门店号+小票号+3位序列号\n
        vje：交易金额\n
        requestId：交易请求ID，一次交易行为的唯一标识\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/payWithTmq"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vtrack2": request.vtrack2,
            "vcardbrand": request.vcardbrand,
            "vtype": request.vtype,
            "vseqno": request.vseqno,
            "vje": request.vje,
            "requestId": request.requestId,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/return-with-tmq", summary="条码现金券冲正接口", response_model=BaseResponse)
def return_with_tmq(request: ReturnWithTmqRequest = Body(...)):
    """
    条码现金券冲正接口
    接口说明：条码现金券冲正，销售小票已核销金额原路退回，不支持售后退款。仅支持广百条码现金券。

    Args:
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        vtrack2：磁道信息，刷卡获取的内容\n
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡\n
        vtype：交易类型，默认 01\n
        vseqno：交易流水号，4位门店号+小票号+3位序列号\n
        vje：交易金额\n
        vmemo：原交易流水号\n
        requestId：交易请求ID，一次交易行为的唯一标识\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ipayment/pay/v2/returnWithTmq"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vtrack2": request.vtrack2,
            "vcardbrand": request.vcardbrand,
            "vtype": request.vtype,
            "vseqno": request.vseqno,
            "vje": request.vje,
            "vmemo": request.vmemo,
            "requestId": request.requestId,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/get-tmq-trade-confirm-info", summary="条码现金券交易确认接口", response_model=BaseResponse)
def get_tmq_trade_confirm_info(request: GetTmqTradeConfirmInfoRequest = Body(...)):
    """
    条码现金券交易确认接口
    接口说明：可用于查询小票的交易信息，核对双方金额是否一致。

    Args:
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/ibusiness/v2/xfk/getTmqTradeComfirmInfo"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vcardbrand": request.vcardbrand,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/tmq-settlement", summary="条码现金券日结接口", response_model=BaseResponse)
def tmq_settlement(request: TmqSettlementRequest = Body(...)):
    """
    条码现金券日结接口
    接口说明：收款员交班时结算条码现金券数据，汇总交易笔数及金额。

    Args:\n
        storeNo: 门店编号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        vcardbrand：卡类型，201广百积分卡，202友谊积分卡\n
        dh：日结单号，年月日+收款员号+序列号\n
        companyCode：企业编码，GB：广百\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/settlement/v2/tmqSettlement"
        param = {
            "storeNo": request.storeNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "vcardbrand": request.vcardbrand,
            "dh" : request.dh,
            "companyCode" : request.companyCode,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/get-supply-info", summary="专柜数据接口", response_model=BaseResponseByListData)
def get_supply_info(request: GetSupplyInfo = Body(...)):
    """
    专柜数据接口
    接口说明：该接口可通过供应商编号查询广百侧定义的门店、商场、专柜、收款员数据，为后续订单推送、支付等业务提供基础数据。

    Args:\n
        supplyId: 供应商编号
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/erp-api/gberp/outter/getSupplyInfo"
        param = {
            "supplyId": request.supplyId
        }
        result = gb_post(url, param)
        
        # 处理响应
        if result["code"] == 1:
            return BaseResponseByListData(
                success=True,
                code=result["code"],
                data=result.get("data"),
                message=result.get("message", "成功")
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/points-query", summary="积分查询接口", response_model=BaseResponse)
def points_query(request: PointsQueryRequest = Body(...)):
    """
    积分查询接口
    接口说明：识别支付二维码，查询会员积分余额及使用规则，使用积分时需符号特定规则。
    例如，人民币：积分兑换率为1：100，积分兑换倍数为10000，即积分支付只能为10000的倍数，对照到人民币即只能是100的倍数；最低起付为20000，即支付金额不能小于200；
    当前可用积分为36849，即支付金额不能大于300。以上数值均为举例，具体数额需通过接口获取。

    Args:\n
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        bisCode：业态编码，801：百货\n
        cardNo：会员卡号\n
        companyCode：企业编码，GB：广百\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/points/query"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "bisCode": request.bisCode,
            "cardNo": request.cardNo,
            "companyCode": request.companyCode,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/points-deal", summary="积分支付、撤销、退货接口", response_model=BaseResponse)
def points_deal(request: PointsDealRequest = Body(...)):
    """
    积分支付、撤销、退货接口
    接口说明：识别支付二维码，积分支付时支付金额需符合特定规则，且一笔交易只能使用一次。若交易未完成，支持原路退回，支持售后退款，售后不支持撤销。

    Args:\n
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        amt：交易金额，均为正值\n
        dealCode：支付二维码\n
        cardNo：会员卡号\n
        bisCode：业态编码，801：百货\n
        type：业务类型，1-消费 2-撤销 3-售后退款\n
        flag：增减类型，消费：-1，撤销或售后：1\n
        posDate：支付时间\n
        requestId：交易请求ID，一次交易行为的唯一标识\n
        companyCode：企业编码，GB：广百\n
        channelId：收款渠道\n
        afterSaleNo：退货小票号\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/points/deal"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "amt": request.amt,
            "dealCode": request.dealCode,
            "cardNo": request.cardNo,
            "bisCode": request.bisCode,
            "type": request.type,
            "flag": request.flag,
            "posDate": request.posDate,
            "requestId": request.requestId,
            "companyCode": request.companyCode,
            "channelId": request.channelId,
            "afterSaleNo": request.afterSaleNo,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/points-tradeQuery", summary="积分支付交易确认接口", response_model=BaseResponse)
def points_tradeQuery(request: PointsTradeQueryRequest = Body(...)):
    """
    积分支付交易确认接口
    接口说明：可用于查询小票的交易信息，核对双方金额是否一致。

    Args:\n
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        bisCode：业态编码，801：百货\n
        cardNo：会员卡号\n
        companyCode：企业编码，GB：广百\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/points/tradeQuery"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "biscode": request.bisCode,
            "cardNo": request.cardNo,
            "companyCode": request.companyCode,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/points-settlement", summary="积分支付日结接口", response_model=BaseResponse)
def points_settlement(request: PointsSettlementRequest = Body(...)):
    """
    积分支付日结接口
    接口说明：收款员交班时结算积分支付数据，汇总交易笔数及金额。

    Args:\n
        storeNo: 门店编号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        bisCode：业态编码，801：百货\n
        companyCode：企业编码，GB：广百\n
        dh：日结单号，年月日+收款员号+序列号\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/points/settlement"
        param = {
            "storeNo": request.storeNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "biscode": request.bisCode,
            "companyCode": request.companyCode,
            "dh": request.dh,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/eacc-queryBalance", summary="电子账户查询接口", response_model=BaseResponse)
def eacc_queryBalance(request: EaccQueryBalanceRequest = Body(...)):
    """
    电子账户查询接口
    接口说明：识别支付二维码，查询电子账户余额。

    Args:\n
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        dealCode：支付二维码\n
        cardNo：会员卡号\n
        companyCode：企业编码，GB：广百\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/eacc/queryBalance"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "dealCode": request.dealCode,
            "cardNo": request.cardNo,
            "companyCode": request.companyCode,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/eacc-deal", summary="电子账户支付、撤销、退货接口", response_model=BaseResponse)
def eacc_deal(request: EaccDealRequest = Body(...)):
    """
    电子账户支付、撤销、退货接口
    接口说明：查询时缓存支付二维码，支付时直接获取，避免二次扫码。电子账户交易系统内部按优先级依次抵扣现金金额、积分卡金额、赠送金额，并返回对应的抵扣金额，
    需根据抵扣金额拆分为三个支付方式。一笔交易只能使用一次。若交易未完成，支持原路退回，支持售后退款，售后不支持撤销。

    Args:\n
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        amt：交易金额，均为正值\n
        dealCode：支付二维码\n
        cardNo：会员卡号\n
        bisCode：业态编码，801：百货\n
        type：业务类型，5-消费 6-撤销 7-售后退款\n
        flag：增减类型，消费：-1，撤销或售后：1\n
        sysdate：支付时间\n
        requestId：交易请求ID，一次交易行为的唯一标识\n
        companyCode：企业编码，GB：广百\n
        channelId：收款渠道\n
        afterSaleNo：退货小票号\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/eacc/deal"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "amt": request.amt,
            "dealCode": request.dealCode,
            "cardNo": request.cardNo,
            "bisCode": request.bisCode,
            "type": request.type,
            "flag": request.flag,
            "sysdate": request.sysdate,
            "requestId": request.requestId,
            "companyCode": request.companyCode,
            "channelId": request.channelId,
            "afterSaleNo": request.afterSaleNo,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/eacc-get-trade-comfirm-info", summary="电子账户交易确认接口", response_model=BaseResponse)
def eacc_get_trade_comfirm_info(request: EaccGetTradeComfirmInfo = Body(...)):
    """
    电子账户交易确认接口
    接口说明：可用于查询小票的交易信息，核对双方金额是否一致。

    Args:\n
        storeNo: 门店编号\n
        orderNo：销售小票号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        bisCode：业态编码，801：百货\n
        flag：增减类型，消费：-1，撤销或售后：1\n
        companyCode：企业编码，GB：广百\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/eacc/getTradeComfirmInfo"
        param = {
            "storeNo": request.storeNo,
            "orderNo": request.orderNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "bisCode": request.bisCode,
            "flag": request.flag,
            "companyCode": request.companyCode,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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


@gb_router.post("/eacc-daily-Settlement", summary="电子账户日结接口", response_model=BaseResponse)
def eacc_daily_Settlement(request: EaccDailySettlementRequest = Body(...)):
    """
    电子账户日结接口
    接口说明：收款员交班时结算电子账户数据，汇总交易笔数及金额。

    Args:\n
        storeNo: 门店编号\n
        cashierId：收款员号\n
        terminalId：授权终端号，4位门店号+5位收款终端号\n
        bisCode：业态编码，801：百货\n
        companyCode：企业编码，GB：广百\n
        dh：日结单号，年月日+收款员号+序列号\n
    
    Returns:
        字典格式的响应数据或错误信息
    """
    try:
        # 解析参数并调用接口
        url = BASE_URL + "/openapi/payment-api/memberPayment/eacc/dailySettlement"
        param = {
            "storeNo": request.storeNo,
            "cashierId": request.cashierId,
            "terminalId": request.terminalId,
            "bisCode": request.bisCode,
            "dh": request.dh,
            "companyCode": request.companyCode,
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
            raise HTTPException(
                status_code=400,
                detail=BaseResponse(
                    success=False,
                    code=result["code"],
                    message=result.get("message", "请求失败")
                ).dict()
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
