from fastapi import APIRouter, Query
from db import SyncGetSales

sync_router = APIRouter(prefix="/sync", tags=["sync"])

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

