# 广百接口一些请求入参/出仓的实体
from dataclasses import field
from datetime import date
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any


# ================ 基础响应模型 ================
class BaseResponse(BaseModel):
    success: bool
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


class BaseResponseByListData(BaseModel):
    success: bool
    code: int
    message: str
    data: Optional[list[Dict[str, Any]]] = None


# ================ 各接口请求模型 ================
class FindMemberInfoBrandRequest(BaseModel):
    """会员识别接口请求模型"""
    strCustomer: str = Field(..., description="会员卡号/会员码/手机号")


class QueryXfkInfoRequest(BaseModel):
    """积分卡查询接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vtrack2: str = Field(..., description="磁道信息，刷卡获取的内容")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v


class PayWithXfkRequest(BaseModel):
    """积分卡核销接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vtrack2: str = Field(..., description="磁道信息，刷卡获取的内容")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    vtype: str = Field(..., description="交易类型，默认 01")
    vseqno: str = Field(..., description="交易流水号，4位门店号+小票号+3位序列号")
    vje: float = Field(..., description="交易金额", gt=0)
    requestId: str = Field(..., description="交易请求ID，一次交易行为的唯一标识")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v
    
    @validator('vtype')
    def validate_vtype(cls, v):
        if v != '01':
            raise ValueError('交易类型目前只支持 01')
        return v


class XfkWriteoffCancelRequest(BaseModel):
    """积分卡冲正接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vtrack2: str = Field(..., description="磁道信息，刷卡获取的内容")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    vtype: str = Field(..., description="交易类型，默认 01")
    vseqno: str = Field(..., description="交易流水号，4位门店号+小票号+3位序列号")
    vje: float = Field(..., description="交易金额", gt=0)
    vmemo: str = Field(..., description="原交易流水号")
    requestId: str = Field(..., description="交易请求ID，一次交易行为的唯一标识")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v


class GetXfkTradeConfirmInfoRequest(BaseModel):
    """积分卡交易确认接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v


class XfkSettlementRequest(BaseModel):
    """积分卡日结接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    dh: str = Field(..., description="日结单号，年月日+收款员号+序列号")
    companyCode: str = Field(..., description="企业编码，GB：广百")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v


class QueryByTmqRequest(BaseModel):
    """条码现金券查询接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vtrack2: str = Field(..., description="磁道信息，刷卡获取的内容")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v


class PayWithTmqRequest(BaseModel):
    """条码现金券核销接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vtrack2: str = Field(..., description="磁道信息，刷卡获取的内容")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    vtype: str = Field(..., description="交易类型，默认 01")
    vseqno: str = Field(..., description="交易流水号，4位门店号+小票号+3位序列号")
    vje: float = Field(..., description="交易金额", gt=0)
    requestId: str = Field(..., description="交易请求ID，一次交易行为的唯一标识")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v
    
    @validator('vtype')
    def validate_vtype(cls, v):
        if v != '01':
            raise ValueError('交易类型目前只支持 01')
        return v


class ReturnWithTmqRequest(BaseModel):
    """条码现金券冲正接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vtrack2: str = Field(..., description="磁道信息，刷卡获取的内容")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    vtype: str = Field(..., description="交易类型，默认 01")
    vseqno: str = Field(..., description="交易流水号，4位门店号+小票号+3位序列号")
    vje: float = Field(..., description="交易金额", gt=0)
    vmemo: str = Field(..., description="原交易流水号")
    requestId: str = Field(..., description="交易请求ID，一次交易行为的唯一标识")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v


class GetTmqTradeConfirmInfoRequest(BaseModel):
    """条码现金券交易确认接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v


class TmqSettlementRequest(BaseModel):
    """条码现金券日结接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    vcardbrand: str = Field(..., description="卡类型，201广百积分卡，202友谊积分卡")
    dh: str = Field(..., description="日结单号，年月日+收款员号+序列号")
    companyCode: str = Field(..., description="企业编码，GB：广百")
    
    @validator('vcardbrand')
    def validate_vcardbrand(cls, v):
        if v not in ['201', '202']:
            raise ValueError('卡类型必须是 201(广百积分卡) 或 202(友谊积分卡)')
        return v


class GetSupplyInfo(BaseModel):
    """专柜数据接口请求模型"""
    supplyId: str = Field(..., description="供应商编号")


class PointsQueryRequest(BaseModel):
    """积分查询接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    bisCode: str = Field(..., description="业态编码，801：百货")
    cardNo: str = Field(..., description="会员卡号")
    companyCode: str = Field(..., description="企业编码，GB：广百")


class PointsDealRequest(BaseModel):
    """积分支付、撤销、退货接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    amt: float = Field(..., description="交易金额，均为正值")
    dealCode: str = Field(..., description="支付二维码")
    cardNo: str = Field(..., description="会员卡号")
    bisCode: str = Field(..., description="业态编码，801：百货")
    type: int = Field(..., description="业务类型，1-消费 2-撤销 3-售后退款")
    flag:int = Field(..., description="增减类型，消费：-1，撤销或售后：1")
    posDate: str = Field(..., description="支付时间")
    requestId: str = Field(..., description="交易请求ID，一次交易行为的唯一标识")
    companyCode: str = Field(..., description="企业编码，GB：广百")
    channelId: str = Field(..., description="收款渠道")
    afterSaleNo: str = Field(None, description="退货小票号")


class PointsTradeQueryRequest(BaseModel):
    """积分支付交易确认接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    bisCode: str = Field(..., description="业态编码，801：百货")
    cardNo: str = Field(..., description="会员卡号")
    companyCode: str = Field(..., description="企业编码，GB：广百")


class PointsSettlementRequest(BaseModel):
    """积分支付交易确认接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    bisCode: str = Field(..., description="业态编码，801：百货")
    companyCode: str = Field(..., description="企业编码，GB：广百")
    dh: str = Field(..., description="日结单号，年月日+收款员号+序列号")


class EaccQueryBalanceRequest(BaseModel):
    """电子账户查询接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    dealCode: str = Field(..., description="支付二维码")
    cardNo: str = Field(..., description="会员卡号")
    companyCode: str = Field(..., description="企业编码，GB：广百")


class EaccDealRequest(BaseModel):
    """电子账户支付、撤销、退货接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    amt: float = Field(..., description="交易金额，均为正值")
    dealCode: str = Field(..., description="支付二维码")
    cardNo: str = Field(..., description="会员卡号")
    bisCode: str = Field(..., description="业态编码，801：百货")
    type: int = Field(..., description="业务类型，5-消费 6-撤销 7-售后退款")
    flag:int = Field(..., description="增减类型，消费：-1，撤销或售后：1")
    sysdate: str = Field(..., description="支付时间")
    requestId: str = Field(..., description="交易请求ID，一次交易行为的唯一标识")
    companyCode: str = Field(..., description="企业编码，GB：广百")
    channelId: str = Field(..., description="收款渠道")
    afterSaleNo: str = Field(..., description="退货小票号")


class EaccGetTradeComfirmInfo(BaseModel):
    """电子账户交易确认接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    orderNo: str = Field(..., description="销售小票号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    bisCode: str = Field(..., description="业态编码，801：百货")
    flag: str = Field(..., description="增减类型，消费：-1，撤销或售后：1")
    companyCode: str = Field(..., description="企业编码，GB：广百")


class EaccDailySettlementRequest(BaseModel):
    """电子账户日结接口请求模型"""
    storeNo: str = Field(..., description="门店编号")
    cashierId: str = Field(..., description="收款员号")
    terminalId: str = Field(..., description="授权终端号，4位门店号+5位收款终端号")
    bisCode: str = Field(..., description="业态编码，801：百货")
    companyCode: str = Field(..., description="企业编码，GB：广百")
    dh: str = Field(..., description="日结单号，年月日+收款员号+序列号")








