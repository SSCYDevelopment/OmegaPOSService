

--1. 两件8折
INSERT crpomh (
	phshop,
	phtxnt,
	phfdat,
	phtdat,
	phvrgn,
	phcanx,
	phvlmt,
    phdesc
	)
VALUES (
	'GZ86',
	'CN000001',
	'2025-12-1',
	'2025-12-31',
	'',
	'',
	''，
    N'精选货品两件8折'
	)


 INSERT crpomd 
 (
	pdshop,
	pdtxnt,
	pdscop,
	pdcamt,
	pdcqty,
	pdovex,
	pdupri,
	pdudsc,
	pdseqn,
	pdstyp
)
VALUES 
(
	'GZ86',
	'CN000001',
	'CN000001A',
	0,
	2,
	'O',
	'',
	20,
	1,
	''
	)

        

insert crscop (
    scscop,
    scstyl,
    scstyp)
VALUES
(
    'CN000001A',
    '60017385',
    ''
    )
--找测试款

--select b.*,a.pcsprc from mfprch(nolock) a, mfskun(nolock) b where a.pcstyl= b.skstyl and b.skstyl in ('60017385','60019248')
-- 60017385       
-- 60019248       
insert crscop (
    scscop,
    scstyl,
    scstyp)
VALUES
(
    'CN000001A',
    '60017385',
    ''
    )

insert crscop (
    scscop,
    scstyl,
    scstyp)
VALUES
(
    'CN000001A',
    '60019248',
    ''
    )    


SELECT a.*,c.pdudsc
FROM crscop a,
	crpomh b,
	crpomd c
WHERE a.scscop = c.pdscop
	AND b.phtxnt = c.pdtxnt
	AND b.phshop = 'GZ86'
	AND b.phtxnt = 'CN000001'

--验证设置的促销
--60017385       	000	000	2050000178948        
--60019248       	000	000	2050000213144       

select NEWID()
-- 购物车ID: a230f500-1f7d-4d1a-b002-f967d386f673

EXEC MPos_Public_CheckStyl '2050000178948',
	'CN',
	'GZ86'

--添加商品到购物车 第一件商品
EXEC MPos_Crm01_SaveCartItem @TransDate = '2025-12-17',
	@Shop = 'GZ86',
	@Crid = '999',
	@CartID = 'a230f500-1f7d-4d1a-b002-f967d386f673',
	@Seqn = - 1,
	@ItemType = 'S',
	@skuBarcode = '2050000178948',
	@StyleCode = '60017385',
	@Color = '000',
	@Size = '000',
	@qty = 1,
	@Weight = 0,
	@Price = 91.67,
	@OPrice = 100,
	@Amnt = 91.67,
	@OAmnt = 100,
	@Discount = 0,
	@DiscountType = '',
	@DiscountID = '',
	@DiscountBrandBit = - 1,
	@DiscountPtyp = '',
	@PromotionCode = '',
	@PromotionID = ''

--检查一下购物车
SELECT *
FROM crcart
WHERE TransDate = '2025-12-17'
	AND Shop = 'GZ86'
	AND Crid = '999'
	AND CartID = 'a230f500-1f7d-4d1a-b002-f967d386f673'

--添加商品到购物车 第二件商品
EXEC MPos_Public_CheckStyl '2050000213144',
	'CN',
	'GZ86'

EXEC MPos_Crm01_SaveCartItem @TransDate = '2025-12-17',
	@Shop = 'GZ86',
	@Crid = '999',
	@CartID = 'a230f500-1f7d-4d1a-b002-f967d386f673',
	@Seqn = - 1,
	@ItemType = 'S',
	@skuBarcode = '2050000213144',
	@StyleCode = '60019248',
	@Color = '000',
	@Size = '000',
	@qty = 1,
	@Weight = 0,
	@Price = 71.07,
	@OPrice = 100,
	@Amnt = 71.07,
	@OAmnt = 100,
	@Discount = 0,
	@DiscountType = '',
	@DiscountID = '',
	@DiscountBrandBit = - 1,
	@DiscountPtyp = '',
	@PromotionCode = '',
	@PromotionID = ''

--检查一下购物车
SELECT *
FROM crcart
WHERE TransDate = '2025-12-17'
	AND Shop = 'GZ86'
	AND Crid = '999'
	AND CartID = 'a230f500-1f7d-4d1a-b002-f967d386f673'

--查看promotion计算结果
exec MPOS_Crm01_CalcCompaign 
    @transactionDate = '2025-12-17',
    @shopID = 'GZ86',
    @Crid = '999',
    @CartID = 'a230f500-1f7d-4d1a-b002-f967d386f673',
    @memberCard='',
    @debug='N'