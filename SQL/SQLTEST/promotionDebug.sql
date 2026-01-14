
-- Debug promotion pricing issue

SELECT a.TransDate,
	a.shop,
	a.Crid,
	a.InputTime,
	a.Sku,
	a.Seqn,
	a.Qty,
	a.OPrice,
	a.OAmnt,
	a.Price,
	a.Amnt,
	b.smsprc
FROM crcart a,
	mfstyl b
WHERE a.CartID = '9c1c3407-f95d-4410-a59c-5ad17c13816f'
	AND a.StyleCode = b.smcode

select b.Sku, a.pcstyl, a.pcsprc [mfprch单价], b.Price [购物车单价], b.Qty, b.PromotionID, b.PromotionCode from mfprch a, crcart b where b.CartID= '9c1c3407-f95d-4410-a59c-5ad17c13816f' and a.pcstyl=b.StyleCode and a.pcshop=b.Shop


SELECT a.TransDate,
	a.shop,
	a.Crid,
	a.InputTime,
	a.Sku,
	a.Seqn,
	a.Qty,
	a.OPrice,
	a.OAmnt,
	a.Price,
	a.Amnt,
	b.smsprc
FROM crcart a,
	mfstyl b
WHERE a.CartID = 'A4858BCB-F82B-4277-9605-1021C8DBAA71'
	AND a.StyleCode = b.smcode

select b.Sku, a.pcstyl, a.pcsprc [mfprch单价], b.Price [购物车单价], b.Qty, b.PromotionID, b.PromotionCode from mfprch a, crcart b where b.CartID= 'A4858BCB-F82B-4277-9605-1021C8DBAA71' and a.pcstyl=b.StyleCode and a.pcshop=b.Shop


exec MPos_Public_CheckStyl '2050000178948',
    'CN',
    'GZ86'


update  a set a.price=91.67, a.Amnt=91.67 * a.Qty from crcart a where a.CartID='a4858bcb-f82b-4277-9605-1021c8dbaa71'

exec MPOS_Crm01_CalcCompaign @transactionDate='2025-12-17',
    @ShopID='GZ86',
    @Crid='999',
    @CartID='A4858BCB-F82B-4277-9605-1021C8DBAA71'



select * from sysdat




