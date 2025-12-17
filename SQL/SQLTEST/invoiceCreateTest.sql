/*
  文件名:        invoiceCreateTest.sql
  说明:          发票创建测试脚本，最简单模式
  作者:          Mike Chan
  日期:          2024-06-10
*/
--设置硬件ID(购物车id)
DECLARE @cartID UNIQUEIDENTIFIER

SET @cartID = NEWID()

PRINT @cartID

--临时购物车ID：'2031DC7C-7779-4509-B7A1-4B283CEAB59D'
/*section 1: 设置销售日期和收银机号测试*/
--设置销售日期
EXEC MPos_Public_changetrandate 'GZ86';
GO

--检查销售日期
SELECT *
FROM sysdat
WHERE ssshop = 'GZ86';

/*****************************************/
/*section 2: 获取收银机号                 */
/*****************************************/
--获取收银机号
-- 使用变量接收存储过程返回值（返回值为INT类型的返回码）
DECLARE @CreateCridReturn INT;

EXEC @CreateCridReturn = MPos_Public_CreateCrid 'GZ86',
	'2031DC7C-7779-4509-B7A1-4B283CEAB59D';

PRINT 'MPos_Public_CreateCrid 返回码：' + CAST(@CreateCridReturn AS VARCHAR(12));

--检查收银机号
SELECT *
FROM Mfcrid
WHERE mcshop = 'GZ86'
	AND mcmach = '2031DC7C-7779-4509-B7A1-4B283CEAB59D';

--临时收银机号(crid): '999'
--临时销售日期(txdt): '2025-12-17'
/*section 3: 创建发票测试*/
--创建发票获取发票号
-- 使用变量获取创建发票的存储过程MPos_Crm01_NewInvo返回的发票号码
-- 假设存储过程有一个 OUTPUT 参数名为 @invno（根据实际参数名调整）
DECLARE @CreateInvReturn INT;
DECLARE @InvoiceNo NVARCHAR(50);

EXEC @CreateInvReturn = MPos_Crm01_NewInvo @PCSHOP = 'GZ86',
	@PDTXDT = '2025-12-17',
	@PCCRID = '999'

PRINT 'MPos_Crm01_NewInvo 返回码：' + CAST(@CreateInvReturn AS VARCHAR(12));
PRINT '创建的发票号：' + ISNULL(@InvoiceNo, '');


/*****************************************/
/*section 4: 模拟输入条码到发票明细测试    */
/*****************************************/
--假设发票号(invoiceID)为1，检查发票头表和发票明细表
--清空购物车
DELETE
FROM crcart
WHERE TransDate = '2025-12-17'
	AND Shop = 'GZ86'
	AND Crid = '999'
	AND CartID = '2031DC7C-7779-4509-B7A1-4B283CEAB59D'

--检查条码
EXEC MPos_Public_CheckStyl '2050000227103',
	'CN',
	'GZ86'

--添加商品到购物车 第一件商品
EXEC MPos_Crm01_SaveCartItem @TransDate = '2025-12-17',
	@Shop = 'GZ86',
	@Crid = '999',
	@CartID = '2031DC7C-7779-4509-B7A1-4B283CEAB59D',
	@Seqn = - 1,
	@ItemType = 'S',
	@skuBarcode = '2050000227103',
	@StyleCode = '60019315',
	@Color = '000',
	@Size = '000',
	@qty = 1,
	@Weight = 0,
	@Price = 71.07,
	@OPrice = 100,
	@Amnt = 71.07,
	@OAmnt = 140,
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
	AND CartID = '2031DC7C-7779-4509-B7A1-4B283CEAB59D'



--添加商品到购物车 第二件商品
EXEC MPos_Public_CheckStyl '2050000221286',
	'CN',
	'GZ86'

EXEC MPos_Crm01_SaveCartItem @TransDate = '2025-12-17',
    @Shop = 'GZ86',
    @Crid = '999',
    @CartID = '2031DC7C-7779-4509-B7A1-4B283CEAB59D',
    @Seqn = - 1,
    @ItemType = 'S',
    @skuBarcode = '2050000221286',
    @StyleCode = '60020203',
    @Color = '000',
    @Size = '000',
    @qty = 2,
    @Weight = 0,
    @Price = 59.97,
    @OPrice = 84,
    @Amnt = 119.94,
    @OAmnt = 168,
    @Discount = 0,
    @DiscountType = '',
    @DiscountID = '',
    @DiscountBrandBit = - 1,
    @DiscountPtyp = '',
    @PromotionCode = '',
    @PromotionID = ''

--再检查一下购物车
SELECT *
FROM crcart
WHERE TransDate = '2025-12-17'
	AND Shop = 'GZ86'
	AND Crid = '999'
	AND CartID = '2031DC7C-7779-4509-B7A1-4B283CEAB59D'    

--获取购物车总金额和总数量
DECLARE @TotalAmount MONEY;
declare @UnipriceTotalAmount MONEY;
DECLARE @TotalQty INT;
SELECT @TotalAmount = SUM(Amnt),
       @UnipriceTotalAmount = SUM(OAmnt),
       @TotalQty = SUM(Qty) from crcart
WHERE TransDate = '2025-12-17'
    AND Shop = 'GZ86'
    AND Crid = '999'
    AND CartID = '2031DC7C-7779-4509-B7A1-4B283CEAB59D';

--打印总金额和总数量
PRINT '购物车总金额：' + CAST(@TotalAmount AS VARCHAR(20)); 
PRINT '购物车总数量：' + CAST(@TotalQty AS VARCHAR(10));    

--添加付款方式, 以先现金为例测试
exec MPos_Crm01_SaveCartPayment
    @TransDate = '2025-12-17',
    @Shop = 'GZ86',
    @Crid = '999',
    @CartID = '2031DC7C-7779-4509-B7A1-4B283CEAB59D',
    @paymentType = 'C',
    @code='',
    @currency='RMB',
    @localAmount = @TotalAmount,
    @originalAmount = @TotalAmount,
    @exchangeRate = 1,
    @type = 0,
    @ptype = ''

--检查付款方式保存记录
select * from crcinv
WHERE TransDate = '2025-12-17'
    AND Shop = 'GZ86'
    AND Crid = '999'
    AND CartID = '2031DC7C-7779-4509-B7A1-4B283CEAB59D'


/*****************************************/
/*section 5: 完成发票提交发票测试          */
/*****************************************/
--提交发票，返回0表示成功
EXEC MPos_Crm01_SubmitInvoice
    @marketID = 'CN',
    @operator = 'mikechan',
    @tranDate = '2025-12-17',
    @shopID = 'GZ86',
    @crid = '999',
    @invoiceID = 1,
    @cartID = '2031DC7C-7779-4509-B7A1-4B283CEAB59D',
    @memberCard = '',
    @memberCardType = '',
    @salesAssociate = '',
    @usePromotion = 'N'

 --查看创建出来的单据
select * from crsalh
WHERE shtxdt = '2025-12-17'
    AND shshop = 'GZ86'
    AND shcrid = '999'
    AND shinvo = 1
select * from crsald
WHERE sdtxdt = '2025-12-17'
    AND sdshop = 'GZ86'
    AND sdcrid = '999'
    AND sdinvo = 1
select * from crctdr
WHERE cttxdt = '2025-12-17'
    AND ctshop = 'GZ86'
    AND ctcrid = '999'
    AND ctinvo = 1
select * from crprop
WHERE cptxdt = '2025-12-17'
    AND cpshop = 'GZ86'
    AND cpcrid = '999'
    AND cpinvo = 1