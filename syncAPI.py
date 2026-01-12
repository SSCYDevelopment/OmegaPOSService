# sync 接口API

from fastapi import APIRouter, Query
from db import SyncGetSales, SyncGetSalesList, SyncSaveStyle, SyncSaveSku, SyncSavePrice


sync_router = APIRouter(prefix="/sync", tags=["同步接口"])




@sync_router.get("/get-sales")
def api_sync_get_sales(
    shopID: str = Query(..., description="店铺代码（varchar(5)）"),
    trandate: str = Query(..., description="交易日期（smalldatetime，ISO 字符串）"),
    Crid: str = Query(..., description="收银机号（char(3)）"),
    invoiceID: int = Query(..., description="发票编号（int）"),
):
    try:
        data = SyncGetSales(shopID, trandate, Crid, invoiceID)
        count = sum(len(v) for v in data.values()) if isinstance(data, dict) else 0
        return {"success": True, "count": count, "data": data}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


@sync_router.get("/get-sales-list")
def api_sync_get_sales_list(
    shopID: str = Query(..., description="店铺代码（varchar(5)）"),
    trandate: str = Query(..., description="交易日期（smalldatetime，ISO 字符串）"),
    Crid: str = Query(..., description="收银机号（char(3)）"),
    invoiceID: int = Query(..., description="发票编号（int）"),
):
    try:
        data = SyncGetSalesList(shopID, trandate, Crid, invoiceID)
        count = sum(len(v) for v in data.values()) if isinstance(data, dict) else 0
        return {"success": True, "count": count, "data": data}
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


## 同步保存/更新款式信息（调用存储过程 MPos_Sync_SaveStyle）
@sync_router.get("/sync-save-style")
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
@sync_router.get("/sync-save-sku")
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
@sync_router.get("/sync-save-price")
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


