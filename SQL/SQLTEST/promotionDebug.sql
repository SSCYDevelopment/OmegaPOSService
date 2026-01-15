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


EXEC MPos_Publi_CheckCartInfo @TransDate = '2026-1-15',
	@Shop = 'GZ86',
	@Crid = '998',
	@CartID = 'cede7129-1403-4dfc-81a6-3884c9e7604c',
	@usePromotion = 'N'


EXEC MPos_Publi_CheckCartInfo @TransDate = '2026-1-15',
	@Shop = 'GZ86',
	@Crid = '998',
	@CartID = '36cde003-a53c-4c26-81b2-6a48460018c7',
	@usePromotion = 'Y'


select * from crcart a where a.CartID='36cde003-a53c-4c26-81b2-6a48460018c7'
update a set a.shupdt='' from crsalh a where a.shtxdt='2026-1-15' and a.shshop='GZ86' and a.shcrid='998' and a.shinvo=3
select * from crcinv a where a.CartID='36cde003-a53c-4c26-81b2-6a48460018c7'

select * from crsald a where a.sdtxdt='2026-1-15' and a.sdshop='GZ86' and a.sdcrid='998' and sdinvo=3
select * from crsalh a where a.shtxdt='2026-1-15' and a.shshop='GZ86' and a.shcrid='998' and a.shinvo=3
select * from crctdr a where a.cttxdt='2026-1-15' and a.ctshop='GZ86' and a.ctcrid='998' and a.ctinvo=3






EXEC MPos_Crm01_SubmitInvoice @marketID = 'CN',
	@operator = 'mikechan',
	@tranDate = '2026-1-15',
	@shopID = 'GZ86',
	@crid = '998',
	@invoiceID = 3,
	@cartID = '36cde003-a53c-4c26-81b2-6a48460018c7',
	@memberCard = '',
	@memberCardType = '',
	@salesAssociate = '',
	@usePromotion = 'Y'



EXEC MPos_Crm01_Update @shopID = 'GZ86',
	@transDate = '2026-1-15',
	@crid = '998',
	@invoiceID = 3,
	@discountAmount = 0