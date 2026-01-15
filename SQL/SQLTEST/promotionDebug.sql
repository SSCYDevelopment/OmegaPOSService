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

SELECT b.Sku,
	a.pcstyl,
	a.pcsprc [mfprch单价],
	b.Price [购物车单价],
	b.Qty,
	b.PromotionID,
	b.PromotionCode
FROM mfprch a,
	crcart b
WHERE b.CartID = '9c1c3407-f95d-4410-a59c-5ad17c13816f'
	AND a.pcstyl = b.StyleCode
	AND a.pcshop = b.Shop

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

SELECT b.Sku,
	a.pcstyl,
	a.pcsprc [mfprch单价],
	b.Price [购物车单价],
	b.Qty,
	b.PromotionID,
	b.PromotionCode
FROM mfprch a,
	crcart b
WHERE b.CartID = 'A4858BCB-F82B-4277-9605-1021C8DBAA71'
	AND a.pcstyl = b.StyleCode
	AND a.pcshop = b.Shop

SELECT *
FROM crcarh a
WHERE a.CartID = 'A4858BCB-F82B-4277-9605-1021C8DBAA71'

EXEC MPos_Public_CheckStyl '2050000178948',
	'CN',
	'GZ86'

UPDATE a
SET a.price = 91.67,
	a.Amnt = 91.67 * a.Qty
FROM crcart a
WHERE a.CartID = 'a4858bcb-f82b-4277-9605-1021c8dbaa71'

EXEC MPOS_Crm01_CalcCompaign @transactionDate = '2025-12-17',
	@ShopID = 'GZ86',
	@Crid = '998',
	@CartID = 'A4858BCB-F82B-4277-9605-1021C8DBAA71'

INSERT crdtik (
	ddtxdt,
	ddshop,
	ddcrid,
	ddcart,
	ddtick,
	dddsct
	)
VALUES (
	'2025-12-17',
	'GZ86',
	'998',
	'A4858BCB-F82B-4277-9605-1021C8DBAA71',
	'TESTTICK20231217001',
	30
	)

EXEC MPos_Publi_CheckCartInfo @TransDate = '2025-12-17',
	@Shop = 'GZ86',
	@Crid = '998',
	@CartID = 'A4858BCB-F82B-4277-9605-1021C8DBAA71',
	@usePromotion = 'N'
