# public 接口API

from fastapi import APIRouter, Body, HTTPException, Query


# 创建API路由器
crm02_router = APIRouter(prefix="/crm02", tags=["发票管理接口"])