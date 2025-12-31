from datetime import date
from typing import Union

from fastapi import FastAPI, Query
from db import CreateNewInvoid, ListDiscount, SaveProperty, SubmitPayment, GetCouponTypes
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
from GBAPI import gb_router, find_member_info_brand, points_query, query_xfk_info, query_by_tmq

from syncAPI import sync_router
from PublicAPI import public_router
from Crm01API import crm01_router
from Crm02API import crm02_router


app = FastAPI()
app.include_router(gb_router)
app.include_router(sync_router)
app.include_router(public_router)
app.include_router(crm01_router)
app.include_router(crm02_router)


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