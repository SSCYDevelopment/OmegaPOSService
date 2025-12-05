# db.py
import pyodbc
import logging
import os
from config import DB_CONFIG

# ------------------------------
# 日志设定：logs/sql_error.log
# ------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/sql_error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']}",
            timeout=5
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        raise Exception("数据库连接失败，请检查服务器设置")  # 返回给上层


def ListDiscount(pcShop: str, pcUser: str = "", pcDefective: str = ""):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_ListDiscount ?, ?, ?"

        try:
            cursor.execute(sql, (pcShop, pcUser, pcDefective))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {pcShop}, {pcUser}, {pcDefective} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        # 读取返回结果
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        # 统一抛出，让 API 处理
        raise e


def GetSysConfig(pcShop: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_GetSyconf ?"

        try:
            cursor.execute(sql, (pcShop,))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {pcShop} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        # 读取返回结果
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        raise e


def GetCartItems(TransDate, Shop, Crid, CartID):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_GetCartItems ?, ?, ?, ?"

        try:
            cursor.execute(sql, (TransDate, Shop, Crid, CartID))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {TransDate}, {Shop}, {Crid}, {CartID} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        raise e

def DeleteCartItem(TransDate, Shop, Crid, CartID, Seqn):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_DeleteCartItem ?, ?, ?, ?, ?"

        try:
            cursor.execute(sql, (TransDate, Shop, Crid, CartID, Seqn))
            conn.commit()
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {TransDate}, {Shop}, {Crid}, {CartID}, {Seqn} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        affected = cursor.rowcount

        cursor.close()
        conn.close()

        return affected

    except Exception as e:
        raise e


def SaveCartItem(
    TransDate: str,
    Shop: str,
    Crid: str,
    CartID: str,
    Seqn: int,
    ItemType: str,
    skuBarcode: str,
    StyleCode: str,
    Color: str,
    Size: str,
    qty: int,
    Weight,
    Price,
    OPrice,
    Amnt,
    OAmnt,
    Discount,
    DiscountType: str,
    DiscountID: str,
    DiscountBrandBit: int,
    DiscountPtyp: str,
    PromotionCode: str = '',
    PromotionID: str = '',
    Message: str = '',
    Change: str = '',
    SaleType: str = '',
    Line: str = '',
    Brand: str = '',
    Cate: str = '',
    Ptype: str = '',
    Calced: str = '',
    Commision: float = 0,
    GPrice: float = 0,
    LostSales: str = '',
    CumulateValue: str = '',
    VoucherID: str = '',
    BrandBit: int = -1,
    SupplierID: str = '',
    PantsLength: int = 0,
    isEShop: str = ''
):
    """Call stored procedure MPos_Crm01_SaveCartItem.

    Pass parameters in the same order as the stored procedure. Parameters with
    defaults are optional here and default to the same values as the proc.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = (
            "EXEC MPos_Crm01_SaveCartItem " + 
            ", ".join(["?" for _ in range(40)])
        )

        params = (
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
            OPrice,
            Amnt,
            OAmnt,
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
            Cate,
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

        try:
            cursor.execute(sql, params)
            conn.commit()
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {params} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        raise e


def SaveCartInfo(
    TransDate: str,
    Shop: str,
    Crid: str,
    CartID: str,
    memberCard: str,
    SalesAssociate: str,
    isEshop: str = '',
    CityID: int = 0,
    DistID: int = 0,
    Mobile: str = '',
    ReceiverName: str = '',
    Address: str = '',
    Remark: str = ''
):
    """Call stored procedure MPos_Crm01_SaveCartInfo to insert/update crcarh."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_SaveCartInfo " + ", ".join(["?" for _ in range(13)])

        params = (
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

        try:
            cursor.execute(sql, params)
            conn.commit()
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {params} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        raise e


def SaveCartPayment(
    TransDate: str,
    Shop: str,
    Crid: str,
    CartID: str,
    paymentType: str,
    Code: str,
    currency: str,
    localAmount,
    originalAmount,
    exchangeRate,
    type_: int = 0,
    ptype: str = ''
):
    """Call stored procedure MPos_Crm01_SaveCartPayment to insert payment record.

    Note: Python parameter `type_` maps to proc parameter `@type` to avoid
    shadowing built-in `type`.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_SaveCartPayment " + ", ".join(["?" for _ in range(11)])

        params = (
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

        try:
            cursor.execute(sql, params)
            conn.commit()
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {params} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        raise e


def CleanCartPayment(TransDate, Shop, Crid, CartID):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_CleanCartPayment ?, ?, ?, ?"

        try:
            cursor.execute(sql, (TransDate, Shop, Crid, CartID))
            conn.commit()
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {TransDate}, {Shop}, {Crid}, {CartID} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        affected = cursor.rowcount

        cursor.close()
        conn.close()

        return affected

    except Exception as e:
        raise e



def GetPaymentType(lcMakt: str, lcMemberDate: str = 'N'):
    """Call stored procedure MPos_Crm01_GetPaymentType and return rows as list[dict].

    Parameters:
    - lcMakt: market code (char(2))
    - lcMemberDate: 'Y' or 'N' (char(1)), default 'N'
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_GetPaymentType ?, ?"

        try:
            cursor.execute(sql, (lcMakt, lcMemberDate))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {lcMakt}, {lcMemberDate} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        raise e


def GetSuspend(TransDate: str, Shop: str, Crid: str):
    """Call stored procedure MPos_crm01_GetSuspend and return suspended carts.

    Parameters:
    - TransDate: smalldatetime (string ISO format recommended)
    - Shop: char(5)
    - Crid: char(3)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_crm01_GetSuspend ?, ?, ?"

        try:
            cursor.execute(sql, (TransDate, Shop, Crid))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {TransDate}, {Shop}, {Crid} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        raise e


def CheckStyl(pcSkun: str, pcMakt: str = '', pcShop: str = ''):
    """Call stored procedure MPos_CheckStyl and return matching style info.

    Parameters:
    - pcSkun: sku barcode/string (varchar(21))
    - pcMakt: market code (char(2)), optional
    - pcShop: shop code (char(5)), optional
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_CheckStyl ?, ?, ?"

        try:
            cursor.execute(sql, (pcSkun, pcMakt, pcShop))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {pcSkun}, {pcMakt}, {pcShop} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        raise e