from datetime import date
from typing import Union

from fastapi import FastAPI
from db import GetSysConfig
import uvicorn
from GBAPI import gb_router
from syncAPI import sync_router
from PublicAPI import public_router
from Crm01API import crm01_router
from Crm02API import crm02_router
from unionpay import unionpay_router


app = FastAPI()
app.include_router(gb_router)
app.include_router(sync_router)
app.include_router(public_router)
app.include_router(crm01_router)
app.include_router(crm02_router)
app.include_router(unionpay_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}

##测试方法1
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)