drop PROCEDURE IF EXISTS MPos_Publi_CheckCartInfo
GO

CREATE PROCEDURE MPos_Publi_CheckCartInfo @TransDate SMALLDATETIME,
	@Shop CHAR(5),
	@Crid CHAR(3),
	@CartID UNIQUEIDENTIFIER,
	@usePromotion CHAR(1) = 'Y'
AS

SELECT a.wwscard 'MemberCard'
FROM crcarh a
WHERE a.CartID = @CartID
	AND a.Shop = @Shop
	AND a.Crid = @Crid
	AND a.TransDate = @TransDate

SELECT a.ddtick 'Ticket',
	a.dddsct 'Discount'
FROM crdtik a
WHERE a.ddcart = @CartID
	AND a.ddshop = @Shop
	AND a.ddcrid = @Crid
	AND a.ddtxdt = @TransDate

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
	b.smsprc,
	a.Weight
FROM crcart a,
	mfstyl b
WHERE a.CartID = @CartID
	AND a.StyleCode = b.smcode

SELECT a.pcstyl,
	a.pcsprc [商品部改价价钱],
	b.Price [购物车里面的价钱]
FROM mfprch(NOLOCK) a,
	crcart b
WHERE a.pcshop = @Shop
	AND b.CartID = @CartID
	AND a.pcstyl = b.StyleCode
ORDER BY a.pcstyl

EXEC MPOS_Crm01_CalcCompaign @transactionDate = @TransDate,
	@ShopID = @Shop,
	@Crid = @Crid,
	@CartID = @CartID,
	@usePromotion = @usePromotion
GO


