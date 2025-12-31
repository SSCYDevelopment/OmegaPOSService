from typing import Union

from fastapi import FastAPI, Query
from db import ListDiscount
from db import GetSysConfig
from db import DeleteCartItem
from db import GetCartItems
from db import SaveCartItem
from db import SaveCartPayment
from db import SaveCartMemberCard
from db import SaveDiscountTicket
from db import SaveCartInfo
from db import RemoveDiscountTicket
from db import GetPaymentType
from db import GetSuspend
from db import CleanCart
from db import CleanCartPayment
from db import CheckStyl
from db import InsertInvoiceProperty
from db import DeleteInvoiceProperty
from db import SyncSaveStyle
from db import GetShift
from db import NewInvo
from db import GetInvoiceByIden
from db import SyncSaveSku
from db import SyncSavePrice
from db import GetReceiptData
from db import GetMemberTypies
import uvicorn
from GBAPI import gb_router, find_member_info_brand, points_query
from GBModel import FindMemberInfoBrandRequest, PointsQueryRequest

app = FastAPI()
app.include_router(gb_router)



@app.get("/member-lookup")
def api_member_lookup(
    memberType: str = Query(..., description="会员类型: 广百会员,SANSE会员,其他会员"),
    identifier: str = Query(..., description="会员识别号: 会员卡号/会员码/手机号"),
    shopID: str = Query('', description="店铺代码：可选"),
    Crid: str = Query('', description="收银机号：可选"),
):
    try:
        # 广百会员调用 GBAPI.find_member_info_brand
        if memberType == "GBM":
            req = FindMemberInfoBrandRequest(strCustomer=identifier)
            resp = find_member_info_brand(req)

            # 支持函数直接返回 Pydantic BaseResponse 或 dict
            data = None
            message = ""
            success_flag = 0
            if hasattr(resp, "data"):
                data = getattr(resp, "data")
                message = getattr(resp, "message", "")
                success_flag = 1 if getattr(resp, "success", False) else 0
            elif isinstance(resp, dict):
                data = resp.get("data")
                message = resp.get("message", "")
                success_flag = 1 if resp.get("code") == 1 else 0

            
            # 如果查询到会员信息，尝试调用 GBAPI.points_query 查询积分
            points = 0
            try:
                member_card = data.get("strCard") if isinstance(data, dict) else None
                if member_card:
                    pq_req = PointsQueryRequest(Shopid=shopID, Crid=Crid, MemberCard=member_card)
                    pq_resp = points_query(pq_req)
                    if hasattr(pq_resp, "data"):
                        data_obj = getattr(pq_resp, "data", {})
                        if isinstance(data_obj, dict):
                            pts = data_obj.get("points", 0)
                        else:
                            pts = 0
                    elif isinstance(pq_resp, dict):
                        data_obj = pq_resp.get("data", {})
                        if isinstance(data_obj, dict):
                            pts = data_obj.get("points", 0)
                        else:
                            pts = 0
                    else:
                        pts = 0
                    try:
                        points = int(pts) if pts is not None else 0
                    except Exception:
                        points = 0
            except Exception:
                points = -1

            if data:
                return {
                    "success": 1,
                    "message": message or "成功",
                    "card": data.get("strCard") if isinstance(data, dict) else None,
                    "mobile": data.get("strMobile") if isinstance(data, dict) else None,
                    "memberId": data.get("strNo") if isinstance(data, dict) else None,
                    "discount": 5,
                    "points": points,
                }
            else:
                return {"success": 0, "message": "未找到会员信息", "card": "", "mobile": "", "memberId": "", "discount": 0, "points": 0}

        # SANSE会员/其他会员 - placeholder 实现
        elif memberType == "SANSEclub":
            return {"success": 0, "message": "SANSE会员识别尚未实现", "card": "", "mobile": "", "memberId": "", "discount": 0, "points": 0}
        else:
            return {"success": 0, "message": "其他会员类型未实现", "card": "", "mobile": "", "memberId": "", "discount": 0, "points": 0}

    except Exception as e:
        return {"success": -1, "message": f"异常: {e}", "card": "", "mobile": "", "memberId": "", "discount": 0, "points": 0}
    
@app.get("/member-types")
def api_get_member_types(shopID: str = Query('', description="店铺代码（char(5），可选")):
    try:
        data = GetMemberTypies(shopID)
        count = len(data) if isinstance(data, (list, tuple)) else 0
        return {"success": True, "count": count, "data": data}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}    

@app.get("/")
def read_root():
    return {"Hello": "World"}

##测试方法1
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

##获取发票信息
@app.get("/invoice-by-iden")
def api_get_invoice_by_iden(
    shopID: str = Query(..., description="店铺编号（varchar）"),
    iden: str = Query(..., description="识别码/凭证号（char）"),
):
    """调用存储过程 MPos_Crm01_GetInoviceByIden 并返回多个结果集的结构化数据。

    返回格式：{ header: [...], details: [...], payments: [...], props: [...] }
    """
    try:
        data = GetInvoiceByIden(shopID, iden)
        return {"success": True, "count": sum(len(v) for v in data.values()), "data": data}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

##获取可用折扣列表
@app.get("/list-discount")
def api_list_discount(pcShop: str, pcUser: str = "", pcDefective: str = ""):
    data = ListDiscount(pcShop, pcUser, pcDefective)
    return {
        "success": True,
        "count": len(data),
        "data": data
    }

##获取系统配置
@app.get("/sysconfig")
def api_get_sysconfig(pcShop: str):
    data = GetSysConfig(pcShop)
    if data is None:
        count = 0
    elif isinstance(data, (list, tuple, set, dict)):
        count = len(data)
    else:
        try:
            count = len(data)
        except Exception:
            count = 1
    return {"success": True, "count": count, "data": data}

##删除购物车项目
@app.get("/delete-cart-item")
def api_delete_cart_item(TransDate: str, Shop: str, Crid: str, CartID: str, Seqn: int):

    result = DeleteCartItem(TransDate, Shop, Crid, CartID, Seqn)
    return {"success": True, "result": result}


## 清空/重置购物车（调用存储过程 MPos_Crm01_cleancart）
@app.get("/clean-cart")
def api_clean_cart(TransDate: str, Shop: str, Crid: str, CartID: str):
    result = CleanCart(TransDate, Shop, Crid, CartID)
    return {"success": True, "result": result}


## 清空/重置购物车支付信息（调用存储过程 MPos_Crm01_cleancartpayment）
@app.get("/clean-cart-payment")
def api_clean_cart_payment(TransDate: str, Shop: str, Crid: str, CartID: str):
    result = CleanCartPayment(TransDate, Shop, Crid, CartID)
    return {"success": True, "result": result}


## Invoice 属性：添加（调用 MPos_Crm01_InsertProperty）
@app.get("/invoice-property-add")
def api_insert_invoice_property(
    pdTxdt: str = Query(..., description="交易日期（smalldatetime），建议 ISO 格式"),
    pdShop: str = Query(..., description="店铺代码（char(5)）"),
    pcCrid: str = Query(..., description="收银机号（char(3)）"),
    pnInvo: int = Query(..., description="发票/交易编号（int）"),
    pcProp: str = Query(..., description="属性名（varchar(10)）"),
    pcValue: str = Query('', description="属性值（nvarchar，optional）"),
):
    result = InsertInvoiceProperty(pdTxdt, pdShop, pcCrid, pnInvo, pcProp, pcValue)
    return {"success": True, "result": result}


## Invoice 属性：查询/删除（调用 MPos_Crm01_DeleteProperty）
@app.get("/invoice-property-remove")
def api_delete_invoice_property(
    pdTxdt: str = Query(..., description="交易日期（smalldatetime），建议 ISO 格式"),
    pdShop: str = Query(..., description="店铺代码（char(5)）"),
    pcCrid: str = Query(..., description="收银机号（char(3)）"),
    pnInvo: int = Query(..., description="发票/交易编号（int）"),
    pcProp: str = Query(..., description="属性名（varchar(10)），支持前缀匹配"),
):
    data = DeleteInvoiceProperty(pdTxdt, pdShop, pcCrid, pnInvo, pcProp)
    if data is None:
        count = 0
    elif isinstance(data, (list, tuple, set, dict)):
        count = len(data)
    else:
        try:
            count = len(data)
        except Exception:
            count = 1
    return {"success": True, "count": count, "data": data}


##获取购物车项目
@app.get("/cart-items")
def api_get_cart_items(TransDate: str, Shop: str, Crid: str, CartID: str):
    data = GetCartItems(TransDate, Shop, Crid, CartID)
    if data is None:
        count = 0
    elif isinstance(data, (list, tuple, set, dict)):
        count = len(data)
    else:
        try:
            count = len(data)
        except Exception:
            count = 1
    return {"success": True, "count": count, "data": data}


##保存/更新购物车项目（调用存储过程）
@app.get("/save-cart-item")
def api_save_cart_item(
    TransDate: str = Query(..., description="交易日期（smalldatetime），建议 ISO 格式，例如 2025-12-01 或 2025-12-01 14:30:00"),
    Shop: str = Query(..., description="店铺代码（char(5)），5 字符店铺编号"),
    Crid: str = Query(..., description="收银机号（char(3)），3 字符收银机/柜台编号"),
    CartID: str = Query(..., description="购物车 ID（uniqueidentifier），UUID 字符串，例如 11111111-1111-1111-1111-111111111111"),
    Seqn: int = Query(..., description="购物车商品序号（int），传 -1 表示让存储过程自动分配新的序号"),
    ItemType: str = Query(..., description="销售类型（char(1)），表示卖/退 等代码"),
    skuBarcode: str = Query(..., description="条码（char(21)），商品条码/扫描码"),
    StyleCode: str = Query(..., description="货号/款号（char(15)），用于标识款式/货号"),
    Color: str = Query(..., description="颜色码（char(3)），颜色标识码"),
    Size: str = Query(..., description="尺码（char(3)），例如 M/L 或数字码"),
    qty: int = Query(..., description="数量（int），当前行项的商品数量"),
    Weight: float = Query(..., description="重量（money），前端传 float 即可，单位按系统约定"),
    Price: float = Query(..., description="单价（money）"),
    UnitPrice: float = Query(..., description="原价（money），销售前的原始单价"),
    Amnt: float = Query(..., description="金额（money），行项目实际金额（含折扣后的金额）"),
    UnitPriceAmnt: float = Query(..., description="原价金额合计（money），按原价计算的金额合计"),
    Discount: float = Query(..., description="折扣（money），折扣金额或折扣值，按系统约定"),
    DiscountType: str = Query(..., description="折扣类型（char(1)），表示折扣方式/类别的代码"),
    DiscountID: str = Query(..., description="折扣代码（varchar(20)），对应的折扣标识"),
    DiscountBrandBit: int = Query(..., description="折扣可用品牌（int），通常为品牌位掩码/标识"),
    DiscountPtyp: str = Query(..., description="折扣可用付款方式（char(1)），表示折扣可用于的付款类型代码"),
    PromotionCode: str = Query("", description="促销编码（varchar(12)，可选，默认空字符串"),
    PromotionID: str = Query("", description="促销标识/ID（varchar(20)，可选，默认空字符串"),
    Message: str = Query("", description="备注/信息（nvarchar(100)，可选）"),
    Change: str = Query("", description="变更标志（char(1)，可选），用于标识行项变更类型"),
    SaleType: str = Query("", description="销售子类型（char(1)，可选）"),
    Line: str = Query("", description="系列/线路代码（char(3)，可选）"),
    Brand: str = Query("", description="品牌代码（char(3)，可选）"),
    Category: str = Query("", description="类别代码（char(2)，可选）"),
    Ptype: str = Query("", description="销售类型（char(1)），表示卖/退 等代码，可选"),        
    Calced: str = Query("", description="是否已计算标志（char(1)，可选），表示是否已完成某类计算"),
    Commision: float = Query(0, description="佣金（money），行项目的佣金金额，默认 0"),
    GPrice: float = Query(0, description="GPrice（money），内部价格字段，默认 0"),
    LostSales: str = Query("", description="缺货销售标记（char(1)，可选）"),
    CumulateValue: str = Query("", description="是否计入累计值（char(1)，可选），例如是否计入积分/累计金额"),
    VoucherID: str = Query("", description="券/代金券 ID（varchar(100)，可选）"),
    BrandBit: int = Query(-1, description="品牌位（int），-1 常表示“不限制”或未设置，默认 -1"),
    SupplierID: str = Query("", description="供应商 ID（varchar(8)，可选）"),
    PantsLength: int = Query(0, description="裤长（int，可选），适用于裤装类的额外长度信息，默认 0"),
    isEShop: str = Query("", description="是否来自电商（char(1)，可选），如 'Y'/'N' 表示电商来源标记"),
):
    result = SaveCartItem(
        TransDate,
        Shop,
        Crid,
        CartID,
        Seqn,
        ItemType,
        skuBarcode,
        StyleCode,
        Color,
        Size,
        qty,
        Weight,
        Price,
        UnitPrice,
        Amnt,
        UnitPriceAmnt,
        Discount,
        DiscountType,
        DiscountID,
        DiscountBrandBit,
        DiscountPtyp,
        PromotionCode,
        PromotionID,
        Message,
        Change,
        SaleType,
        Line,
        Brand,
        Category,
        Ptype,
        Calced,
        Commision,
        GPrice,
        LostSales,
        CumulateValue,
        VoucherID,
        BrandBit,
        SupplierID,
        PantsLength,
        isEShop,
    )

    return {"success": True, "result": result}


## 保存/更新购物车头信息（调用存储过程 MPos_Crm01_SaveCartInfo）
@app.get("/save-cart-info")
def api_save_cart_info(
    TransDate: str = Query(..., description="销售日期（smalldatetime），建议使用 ISO 格式，例如 2025-12-01"),
    Shop: str = Query(..., description="销售门店（char(5）），5 字符店铺编号"),
    Crid: str = Query(..., description="收银机号码（char(3)），3 字符收银机/柜台编号"),
    CartID: str = Query(..., description="购物车 ID（uniqueidentifier），UUID 字符串"),
    memberCard: str = Query(..., description="会员卡号（char(10)），10 字符会员卡编号"),
    SalesAssociate: str = Query(..., description="销售/导购名称或 ID（varchar(40)）"),
    isEshop: str = Query('', description="是否来自电商（char(1)，可选，默认空字符串，例如 'Y'/'N'"),
    CityID: int = Query(0, description="城市 ID（int，可选，默认 0"),
    DistID: int = Query(0, description="区/县 ID（int，可选，默认 0"),
    Mobile: str = Query('', description="手机号（varchar(20)，可选）"),
    ReceiverName: str = Query('', description="收货人姓名（nvarchar(10)，可选）"),
    Address: str = Query('', description="收货地址（nvarchar(200)，可选）"),
    Remark: str = Query('', description="备注（nvarchar(200)，可选）"),
):
    result = SaveCartInfo(
        TransDate,
        Shop,
        Crid,
        CartID,
        memberCard,
        SalesAssociate,
        isEshop,
        CityID,
        DistID,
        Mobile,
        ReceiverName,
        Address,
        Remark,
    )

    return {"success": True, "result": result}


## 保存/更新支付信息（调用存储过程 MPos_Crm01_SavePayment）
@app.get("/save-payment")
def api_save_payment(
    TransDate: str = Query(..., description="交易/销售日期（smalldatetime），建议 ISO 格式，例如 2025-12-01"),
    Shop: str = Query(..., description="店铺代码（char(5）），5 字符店铺编号"),
    Crid: str = Query(..., description="收银机号（char(3)），3 字符收银机/柜台编号"),
    CartID: str = Query(..., description="购物车 ID（uniqueidentifier），UUID 字符串"),
    paymentType: str = Query(..., description="支付方式（char(1)），例如 1=现金、2=卡、3=支付宝 等（按系统约定）"),
    Code: str = Query(..., description="支付序列号/卡号/账号（char(20)），支付凭证或卡号等"),
    currency: str = Query(..., description="货币代码（char(3)），例如 CNY、USD"),
    localAmount: float = Query(..., description="本币金额（money）"),
    originalAmount: float = Query(..., description="原币金额（money），如跨币种支付时使用"),
    exchangeRate: float = Query(..., description="汇率（MONEY），用于计算本币/原币换算"),
    type_: int = Query(0, description="类型（int，可选，默认 0，用作备用字段）"),
    ptype: str = Query('', description="类型2（char(1)，可选，备用字段）"),
):
    result = SaveCartPayment(
        TransDate,
        Shop,
        Crid,
        CartID,
        paymentType,
        Code,
        currency,
        localAmount,
        originalAmount,
        exchangeRate,
        type_,
        ptype,
    )

    return {"success": True, "result": result}


## 保存/更新购物车会员卡（调用存储过程 MPos_crm01_SaveCartMemberCard）
@app.get("/save-cart-membercard")
def api_save_cart_membercard(
    TransDate: str = Query(..., description="交易/销售日期（smalldatetime），建议 ISO 格式"),
    Shop: str = Query(..., description="店铺代码（char(5）），5 字符店铺编号"),
    Crid: str = Query(..., description="收银机号（char(3)），3 字符收银机/柜台编号"),
    CartID: str = Query(..., description="购物车 ID（uniqueidentifier），UUID 字符串"),
    memberCard: str = Query(..., description="会员卡号（char(10)）"),
):
    result = SaveCartMemberCard(TransDate, Shop, Crid, CartID, memberCard)
    return {"success": True, "result": result}


## 保存/更新折扣券（调用存储过程 MPos_Crm01_SaveDiscountTicket）
@app.get("/save-discount-ticket")
def api_save_discount_ticket(
    TransDate: str = Query(..., description="交易/销售日期（smalldatetime），建议 ISO 格式"),
    Shop: str = Query(..., description="店铺代码（char(5）），5 字符店铺编号"),
    Crid: str = Query(..., description="收银机号（char(3)），3 字符收银机/柜台编号"),
    CartID: str = Query(..., description="购物车 ID（uniqueidentifier），UUID 字符串"),
    DiscountTicketID: str = Query(..., description="折扣券 ID（varchar(25)）"),
    DiscountAmount: float = Query(..., description="折扣金额（money）"),
):
    result = SaveDiscountTicket(TransDate, Shop, Crid, CartID, DiscountTicketID, DiscountAmount)
    return {"success": True, "result": result}


## 删除折扣券（调用存储过程 MPos_Crm01_RemoveDiscountTicket）
@app.get("/remove-discount-ticket")
def api_remove_discount_ticket(
    TransDate: str = Query(..., description="交易/销售日期（smalldatetime），建议 ISO 格式"),
    Shop: str = Query(..., description="店铺代码（char(5）），5 字符店铺编号"),
    Crid: str = Query(..., description="收银机号（char(3)），3 字符收银机/柜台编号"),
    CartID: str = Query(..., description="购物车 ID（uniqueidentifier），UUID 字符串"),
    DiscountTicketID: str = Query(..., description="折扣券 ID（varchar(25)）"),
):
    affected = RemoveDiscountTicket(TransDate, Shop, Crid, CartID, DiscountTicketID)
    return {"success": True, "affected": affected}


## 获取可用支付方式（调用存储过程 MPos_Crm01_GetPaymentType）
@app.get("/payment-types")
def api_get_payment_types(
    lcMakt: str = Query(..., description="市场/货币代码（char(2)），例如系统中使用的市场代码"),
    lcMemberDate: str = Query('N', description="是否仅显示会员近期方式（char(1)，'Y' 或 'N'，默认 'N'）"),
):
    data = GetPaymentType(lcMakt, lcMemberDate)
    if data is None:
        count = 0
    elif isinstance(data, (list, tuple, set, dict)):
        count = len(data)
    else:
        try:
            count = len(data)
        except Exception:
            count = 1
    return {"success": True, "count": count, "data": data}



## 获取挂起购物车列表（调用存储过程 MPos_crm01_GetSuspend）
@app.get("/suspend-list")
def api_get_suspend_list(
    TransDate: str = Query(..., description="交易日期（smalldatetime），建议 ISO 格式，例如 2025-12-01"),
    Shop: str = Query(..., description="店铺代码（char(5)，5 字符店铺编号"),
    Crid: str = Query(..., description="收银机号（char(3)，3 字符收银机/柜台编号"),
):
    data = GetSuspend(TransDate, Shop, Crid)
    if data is None:
        count = 0
    elif isinstance(data, (list, tuple, set, dict)):
        count = len(data)
    else:
        try:
            count = len(data)
        except Exception:
            count = 1
    return {"success": True, "count": count, "data": data}


## 获取班次号（调用存储过程 MPos_Crm01_GetShift）
@app.get("/get-shift")
def api_get_shift(
    pcShop: str = Query(..., description="店铺代码（char(5)）"),
    pdTxdt: str = Query(..., description="交易日期（smalldatetime），建议 ISO 格式"),
    pcCrid: str = Query(..., description="收银机号（char(3)）"),
):
    shift = GetShift(pcShop, pdTxdt, pcCrid)
    if shift is None:
        return {"success": True, "count": 0, "data": None}
    return {"success": True, "count": 1, "data": shift}


## 创建新的空白销售发票（调用存储过程 MPos_Crm01_NewInvo）
@app.get("/new-invoice")
def api_new_invoice(
    pcShop: str = Query(..., description="店铺代码（char(5)）"),
    pdTxdt: str = Query(..., description="交易日期（smalldatetime），建议 ISO 格式"),
    pcCrid: str = Query(..., description="收银机号（char(3)）"),
):
    inv = NewInvo(pcShop, pdTxdt, pcCrid)
    if inv is None:
        return {"success": True, "count": 0, "data": None}
    return {"success": True, "count": 1, "data": inv}


## 检查货号/款号信息（调用存储过程 MPos_CheckStyl）
@app.get("/check-styl")
def api_check_styl(
    pcSkun: str = Query(..., description="SKU 字符串/条形码（varchar(21)），例如完整 SKU 或部分码"),
    pcMakt: str = Query('', description="市场代码（char(2)，可选，默认空字符串）"),
    pcShop: str = Query('', description="店铺代码（char(5)，可选，默认空字符串）"),
):
    data = CheckStyl(pcSkun, pcMakt, pcShop)
    if data is None:
        count = 0
    elif isinstance(data, (list, tuple, set, dict)):
        count = len(data)
    else:
        try:
            count = len(data)
        except Exception:
            count = 1
    return {"success": True, "count": count, "data": data}


## 同步保存/更新款式信息（调用存储过程 MPos_Sync_SaveStyle）
@app.get("/sync-save-style")
def api_sync_save_style(
    styleID: str = Query(..., description="款号/货号（varchar(15)），款式编号"),
    localName: str = Query(..., description="本地名称（nvarchar(100)），款式的本地语言名称"),
    englishName: str = Query(..., description="英文名称（nvarchar(100)），款式的英文名称"),
    brand: str = Query(..., description="品牌代码（varchar(15)），品牌编号"),
    unitPrice: float = Query(..., description="单价（smallmoney），款式的单价"),
):
    data = SyncSaveStyle(styleID, localName, englishName, brand, unitPrice)
    if data is None:
        count = 0
    elif isinstance(data, (list, tuple, set, dict)):
        count = len(data)
    else:
        try:
            count = len(data)
        except Exception:
            count = 1
    return {"success": True, "count": count, "data": data}

## 同步保存 SKU 信息（调用存储过程 MPos_Sync_SaveSku）
@app.get("/sync-save-sku")
def api_sync_save_sku(
    barcode: str = Query(..., description="条码（varchar(50)），SKU 条形码"),
    styleID: str = Query(..., description="款号/货号（varchar(15)），款式编号"),
    colorID: str = Query(..., description="颜色代码（char(3)），颜色标识码"),
    sizeID: str = Query(..., description="尺码代码（char(3)），尺码标识"),
):
    data = SyncSaveSku(barcode, styleID, colorID, sizeID)
    if data is None:
        count = 0
    elif isinstance(data, (list, tuple, set, dict)):
        count = len(data)
    else:
        try:
            count = len(data)
        except Exception:
            count = 1
    return {"success": True, "count": count, "data": data}


## 同步保存 价格信息（调用存储过程 MPos_Sync_SavePrice）
@app.get("/sync-save-price")
def api_sync_save_price(
    shopID: str = Query(..., description="店铺代码（varchar(10)），例如门店编号"),
    styleID: str = Query(..., description="款号/货号（varchar(15)），款式编号"),
    price: float = Query(..., description="价格（smallmoney/decimal），新的销售价格"),
    fromDate: str = Query(..., description="生效开始日期（smalldatetime），建议 ISO 格式，例如 2025-12-01"),
    toDate: str = Query(..., description="生效结束日期（smalldatetime），建议 ISO 格式，例如 2025-12-31"),
    reason: str = Query('', description="变更原因（nvarchar(255)，可选）"),
    priceType: int = Query(0, description="价格类型（int，可选，默认 0）"),
):
    data = SyncSavePrice(shopID, styleID, price, fromDate, toDate, reason, priceType)
    if data is None:
        count = 0
    elif isinstance(data, (list, tuple, set, dict)):
        count = len(data)
    else:
        try:
            count = len(data)
        except Exception:
            count = 1
    return {"success": True, "count": count, "data": data}


@app.get("/get-receipt-data")
def api_sync_save_price(
    shopID: str = Query(..., description="店铺代码（varchar(10)），例如门店编号"),
    crid: str = Query(..., description="款号/货号（varchar(15)），款式编号"),
    invo: int = Query(..., description="发票号"),
):
    data = GetReceiptData(shopID, crid, invo)
    return data
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)