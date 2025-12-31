# public 接口API

from fastapi import APIRouter, Body, HTTPException, Query


# 创建API路由器
public_router = APIRouter(prefix="/public", tags=["公共接口"])