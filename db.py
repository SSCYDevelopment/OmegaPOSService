# db.py
from datetime import date
import pyodbc
import logging
import os
from config import DB_CONFIG
from pydantic_core.core_schema import none_schema

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

        sql = "EXEC MPos_Crm01_SaveCartPayment " + ", ".join(["?" for _ in range(12)])

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


def SaveCartMemberCard(TransDate, Shop, Crid, CartID, memberCard):
    """Call stored procedure MPos_crm01_SaveCartMemberCard to save/update member card for a cart.

    Parameters:
    - TransDate: smalldatetime (string ISO format recommended)
    - Shop: char(5)
    - Crid: char(3)
    - CartID: uniqueidentifier/string
    - memberCard: char(10)

    Returns: True on success
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_crm01_SaveCartMemberCard ?, ?, ?, ?, ?"

        try:
            cursor.execute(sql, (TransDate, Shop, Crid, CartID, memberCard))
            conn.commit()
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {TransDate}, {Shop}, {Crid}, {CartID}, {memberCard} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        raise e


def SaveDiscountTicket(TransDate, Shop, Crid, cartID, DiscountTicketID, DiscountAmount):
    """Call stored procedure MPos_Crm01_SaveDiscountTicket to insert or update a discount ticket record.

    Parameters:
    - TransDate: smalldatetime string (ISO recommended)
    - Shop: char(5)
    - Crid: char(3)
    - cartID: uniqueidentifier/string
    - DiscountTicketID: varchar(25)
    - DiscountAmount: money/decimal

    Returns: True on success
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_SaveDiscountTicket ?, ?, ?, ?, ?, ?"

        try:
            cursor.execute(sql, (TransDate, Shop, Crid, cartID, DiscountTicketID, DiscountAmount))
            conn.commit()
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {TransDate}, {Shop}, {Crid}, {cartID}, {DiscountTicketID}, {DiscountAmount} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        raise e


def RemoveDiscountTicket(TransDate, Shop, Crid, cartID, DiscountTicketID):
    """Call stored procedure MPos_Crm01_RemoveDiscountTicket to delete a discount ticket record.

    Parameters:
    - TransDate: smalldatetime string (ISO recommended)
    - Shop: char(5)
    - Crid: char(3)
    - cartID: uniqueidentifier/string
    - DiscountTicketID: varchar(25)

    Returns: number of affected rows (int)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_RemoveDiscountTicket ?, ?, ?, ?, ?"

        try:
            cursor.execute(sql, (TransDate, Shop, Crid, cartID, DiscountTicketID))
            conn.commit()
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {TransDate}, {Shop}, {Crid}, {cartID}, {DiscountTicketID} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        affected = cursor.rowcount

        cursor.close()
        conn.close()

        return affected

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


def CleanCart(TransDate, Shop, Crid, CartID):
    """Call stored procedure MPos_Crm01_cleancart to clean a cart (delete/reset items).

    Parameters:
    - TransDate: smalldatetime (string ISO format recommended)
    - Shop: char(5)
    - Crid: char(3)
    - CartID: uniqueidentifier / string

    Returns: number of affected rows (int)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_cleancart ?, ?, ?, ?"

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


def GetShift(shopID: str, tranDate: str, crid: str):
    """Call stored procedure MPos_Crm01_GetShift and return the shift number (int).

    Parameters:
    - PCSHOP: shop code (char(5))
    - PDTXDT: transaction date (smalldatetime string, ISO recommended)
    - PCCRID: cash register id (char(3))
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_GetShift ?, ?, ?"

        try:
            cursor.execute(sql, (shopID, tranDate, crid))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {shopID}, {tranDate}, {crid} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            try:
                return int(row[0])
            except Exception:
                return row[0]
        return None

    except Exception as e:
        raise e


def NewInvo(PCSHOP: str, PDTXDT: str, PCCRID: str):
    """Call stored procedure MPos_Crm01_NewInvo to create a new invoice number.

    Returns the new invoice number (int) or None.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_NewInvo ?, ?, ?"

        try:
            cursor.execute(sql, (PCSHOP, PDTXDT, PCCRID))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {PCSHOP}, {PDTXDT}, {PCCRID} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            try:
                return int(row[0])
            except Exception:
                return row[0]
        return None

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

        sql = "EXEC MPos_Public_CheckStyl ?, ?, ?"

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



def SyncSaveStyle(styleID: str, localName: str, englishName: str, brand: str, unitPrice: float):
    """同步保存或更新款式信息（调用存储过程 MPos_Sync_SaveStyle）。

    参数：
    - styleID: 款式编号 (varchar(15))
    - localName: 本地语言名称 (nvarchar(100))
    - englishName: 英文名称 (nvarchar(100))
    - brand: 品牌代码 (varchar(15))
    - unitPrice: 单价 (smallmoney)

    返回：
    - 存储过程返回的记录列表（list[dict]），若无返回则为 []。
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Sync_SaveStyle ?, ?, ?, ?, ?"

        try:
            cursor.execute(sql, (styleID, localName, englishName, brand, unitPrice))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {styleID}, {localName}, {englishName}, {brand}, {unitPrice} | Error: {str(sql_ex)}")
            conn.rollback()
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.commit()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        logging.error(f"SQL Execute Error: {sql} | Params: {styleID}, {localName}, {englishName}, {brand}, {unitPrice} | Error: {str(e)}")
        conn.rollback()
        raise Exception("SQL 执行错误，请联系系统管理员")
            

def SyncSaveSku(barcode: str, styleID: str, colorID: str, sizeID: str):
    """Call stored procedure MPos_Sync_SaveSku to save SKU information.

    Parameters:
    - barcode: barcode (varchar(50))
    - styleID: style ID (varchar(15))
    - colorID: color ID (char(3))
    - sizeID: size ID (char(3))
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Sync_SaveSku ?, ?, ?, ?"

        try:
            cursor.execute(sql, (barcode, styleID, colorID, sizeID))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {barcode}, {styleID}, {colorID}, {sizeID} | Error: {str(sql_ex)}")
            conn.rollback()
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.commit()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        conn.rollback()
        raise e


def SyncSavePrice(shopID: str, styleID: str, price: float, fromDate: str, toDate: str, reason: str = '', priceType: int = 0):
    """Call stored procedure MPos_Sync_SavePrice to insert or update price record.

    Parameters:
    - shopID: varchar(10)
    - styleID: varchar(15)
    - price: smallmoney/decimal
    - fromDate: smalldatetime (ISO string recommended)
    - toDate: smalldatetime (ISO string recommended)
    - reason: nvarchar(255), optional
    - priceType: int, optional
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Sync_SavePrice ?, ?, ?, ?, ?, ?, ?"

        try:
            cursor.execute(sql, (shopID, styleID, price, fromDate, toDate, reason, priceType))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {shopID}, {styleID}, {price}, {fromDate}, {toDate}, {reason}, {priceType} | Error: {str(sql_ex)}")
            conn.rollback()
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.commit()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        conn.rollback()
        raise e

def GetInvoiceByIden(shopID: str, iden: str):
    """Call stored procedure MPos_Crm01_GetInoviceByIden which returns multiple result sets:
    1) crsalh (header)
    2) crsald (details)
    3) crctdr (payments)
    4) crprop (properties)

    Returns a dict with keys: `header`, `details`, `payments`, `props`, each is a list of dicts.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_GetInoviceByIden ?, ?"

        try:
            cursor.execute(sql, (shopID, iden))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {shopID}, {iden} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        result = {}
        sets = ["header", "details", "payments", "props"]
        idx = 0

        while True:
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            result_key = sets[idx] if idx < len(sets) else f"set_{idx}"
            result[result_key] = [dict(zip(columns, row)) for row in rows]

            idx += 1
            if not cursor.nextset():
                break

        cursor.close()
        conn.close()

        return result

    except Exception as e:
        logging.error(f"GetInvoiceByIden error: Params=({shopID},{iden}) Error={str(e)}")
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        raise e




def InsertInvoiceProperty(pdTxdt: str, pdShop: str, pcCrid: str, pnInvo: int, pcProp: str, pcValue: str):
    """Call stored procedure MPos_Crm01_InsertProperty to insert or update an invoice property.

    Returns True on success.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_InsertProperty ?, ?, ?, ?, ?, ?"
        params = (pdTxdt, pdShop, pcCrid, pnInvo, pcProp, pcValue)

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


def DeleteInvoiceProperty(pdTxdt: str, pdShop: str, pcCrid: str, pnInvo: int, pcProp: str):
    """Call stored procedure MPos_Crm01_DeleteProperty to query/delete properties for an invoice.

    Returns list[dict] of matching rows.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_DeleteProperty ?, ?, ?, ?, ?"

        try:
            cursor.execute(sql, (pdTxdt, pdShop, pcCrid, pnInvo, pcProp))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {pdTxdt}, {pdShop}, {pcCrid}, {pnInvo}, {pcProp} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        raise e
    
def GetMemberTypies(ShopID: str):
    """Call stored procedure MPos_Crm01_GetMemberTypies and return list[dict]."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_GetMemberTypies ?"

        try:
            cursor.execute(sql, (ShopID,))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {ShopID} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        raise e    


def GetGBConfig(shopid:str, crid:str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Public_GetShopAndCridConfig ?, ?"

        try:
            cursor.execute(sql, (shopid,crid))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {shopid},{crid}| Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        if not cursor.description :
            return
            
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as sql_ex:
        raise Exception("SQL 执行错误，请联系系统管理员")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def GetReceiptData(shopID : str, crid : str, invo : str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_GetReceiptData ?, ?, ?"

        # result_sets = []

        try:
            cursor.execute(sql, (shopID, crid, invo))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {shopID}, {crid}, {invo} | Error: {str(sql_ex)}")
            # raise Exception("SQL 执行错误，请联系系统管理员")
            return {
                            'success': False,
                            'code' : -1,
                            'message': 'SQL 执行错误，请联系系统管理员',
                            'head':None,
                            'detail':None
                        }
        
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            first_result = [dict(zip(columns, row)) for row in rows]
            
            # 检查第一个结果集的结果
            if first_result and len(first_result) > 0:
                first_row = first_result[0]
                
                # 检查获取结果
                if 'code' in first_row and first_row['code']:
                    headRes = None
                    detailRes = None
                    # 获取第二个结果集
                    if cursor.nextset() and cursor.description:
                        columns = [col[0] for col in cursor.description]
                        rows = cursor.fetchall()
                        headRes = [dict(zip(columns, row)) for row in rows]
                        
                    if cursor.nextset() and cursor.description:
                        columns = [col[0] for col in cursor.description]
                        rows = cursor.fetchall()
                        detailRes = [dict(zip(columns, row)) for row in rows]
                    return {
                        'success': True,
                        'code' : first_row["code"],
                        'message': first_row.get('msg', '未知错误'),
                        'head':headRes,
                        'detail':detailRes
                    }
                else:
                    return {
                        'success': False,
                        'code' : first_row["code"],
                        'message': first_row.get('msg', '未知错误'),
                        'head':None,
                        'detail':None
                    }
            else:
                return {
                        'success': False,
                        'code' : 0,
                        'message': '脚本返回结果集异常',
                        'head':None,
                        'detail':None
                    }
            
        else:
            return {
                    'success': False,
                    'code' : 0,
                    'message': '脚本返回结果集异常',
                    'head':None,
                    'detail':None
                }
    except Exception as e:
        # raise e
        return {
                'success': False,
                'code' : -1,
                'message': e,
                'head':None,
                'detail':None
            }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def GetCrid(shopID: str, machine: str):
    """
    根据店铺ID和设备ID获取机器号
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Public_CreateCrid ?, ?"

        try:
            cursor.execute(sql, (shopID, machine))
        except Exception as sql_ex:
            conn.rollback()
            logging.error(f"SQL Execute Error: {sql} | Params: {shopID}, {machine}| Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        row = cursor.fetchone()

        conn.commit()

        if row:
            return row[0]
        return None

    except Exception as e:
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def CreateNewInvoid(transDate: date, shopid: str, crid: str):
    """
    生成发票号
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_NewInvo ?, ?, ?"

        try:
            cursor.execute(sql, (shopid, transDate, crid))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {shopid}, {crid}| Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        row = cursor.fetchone()

        if row:
            return row[0]
        return None

    except Exception as e:
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def SubmitPayment(transDate: date, shopid: str, crid: str, cartID: str, invoiceID:int, memberCard: str, memberCardType: str, salesAssociate: str, usePromotion: str, operator: str, marketID: str ):
    """
    提交发票
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_SubmitInvoice ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?"

        try:
            cursor.execute(sql, (marketID, operator, transDate, shopid, crid, invoiceID, cartID, memberCard, memberCardType, salesAssociate, usePromotion))
        except Exception as sql_ex:
            conn.rollback()
            logging.error(f"SQL Execute Error: {sql} | Params: {shopid}, {cartID}, {invoiceID}| Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        row = cursor.fetchone()

        if row:
            conn.commit()
            return {'ReturnID': row[0], 'ReturnMessage':row[1]}
        else:
            conn.rollback()
            return {'ReturnID': 0, 'ReturnMessage':f'脚本返回解析失败：{row}'}

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def SaveProperty(transDate: date, shopid: str, crid: str, invoiceID:int, propKey:str, propValue:str):
    """
    生成发票号
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_InsertProperty ?, ?, ?, ?, ?, ?"

        try:
            cursor.execute(sql, (transDate, shopid, crid, invoiceID, propKey, propValue))
        except Exception as sql_ex:
            conn.rollback()
            logging.error(f"SQL Execute Error: {sql} | Params: {shopid}, {crid}| Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def SaveSupplyInfo(supplyInfo):
    """
    保存专柜数据
    """
    conn = None
    cursor = None
    try:
        if not supplyInfo:
            return {'success':True, 'message':'' }

        conn = get_connection()
        cursor = conn.cursor()

        if len(supplyInfo) > 0:
            # saveStoreSql = 'EXEC MPos_Crm01_SaveGBSupplyInfo_Store ?, ?, ?, ?, ?, ?'
            savMarketSql = 'EXEC MPos_Crm01_SaveGBSupplyInfo_Market ?, ?, ?, ?'
            savePostSql = 'EXEC MPos_Crm01_SaveGBSupplyInfo_Post ?, ?, ?, ?, ?, ?, ?, ?, ?'
            saveCashierSql = 'EXEC MPos_Crm01_SaveGBSupplyInfo_Cashier ?, ?, ?'

            for store in supplyInfo:
                # cursor.execute(saveStoreSql, (transDate, shopid, crid, invoiceID, propKey, propValue))

                if store['markets'] and len(store['markets']) > 0:
                    for market in store['markets']:
                        cursor.execute(savMarketSql, (store['storeNo'], store['storeName'], market['marketNo'], market['marketName']))
                        
                        if market['posts'] and len(market['posts']) > 0:
                            for post in market['posts']:
                                cursor.execute(savePostSql, (market['marketNo'], post['postNo'], post['postName'], post['postType'], post['czm'], post['categoryNo'], post['categoryName'], post['posName'], post['taxRate']))

                                if post['cashiers'] and len(post['cashiers']) > 0:
                                    for cashier in post['cashiers']:
                                        cursor.execute(saveCashierSql, (post['postNo'], cashier['cashierNo'], cashier['cashierName']))
            conn.commit()
        return {'success':True, 'message':'' }
    except Exception as e:
        conn.rollback()
        return {'success':False, 'message':f'{e}' }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def GetCouponTypes(lcMakt: str):
    """
    获取优惠券类型
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Crm01_GetCouponTypes ?"

        try:
            cursor.execute(sql, (lcMakt))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {lcMakt} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        raise e


# 获取要同步广百的商品信息
def GetGBPushProducts():
    getProductSql = ''


def SyncGetSales(ShopID: str, trandate: str, Crid: str, invoiceID: int):
    """Call stored procedure MPos_Sync_GetSales which returns 4 result sets:
    1) crsalh (header)
    2) crsald (details)
    3) crctdr (payments)
    4) crprop (props)

    Returns a dict with keys: `header`, `details`, `payments`, `props`.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = "EXEC MPos_Sync_GetSales ?, ?, ?, ?"

        try:
            cursor.execute(sql, (ShopID, trandate, Crid, invoiceID))
        except Exception as sql_ex:
            logging.error(f"SQL Execute Error: {sql} | Params: {ShopID}, {trandate}, {Crid}, {invoiceID} | Error: {str(sql_ex)}")
            raise Exception("SQL 执行错误，请联系系统管理员")

        result = {}
        sets = ["header", "details", "payments", "props"]
        idx = 0

        while True:
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall() if cursor.description else []
            key = sets[idx] if idx < len(sets) else f"set_{idx}"
            result[key] = [dict(zip(columns, row)) for row in rows]

            idx += 1
            if not cursor.nextset():
                break

        cursor.close()
        conn.close()

        return result

    except Exception as e:
        logging.error(f"SyncGetSales error: Params=({ShopID},{trandate},{Crid},{invoiceID}) Error={str(e)}")
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        raise e

