/*
  文件名:        invoiceCreateTest.sql
  说明:          发票创建测试脚本
  作者:          Mike Chan
  日期:          2024-06-10
*/

--设置硬件ID(购物车id)
DECLARE @cartID UNIQUEIDENTIFIER
SET @cartID = NEWID()
print @cartID

--临时购物车ID：'2031DC7C-7779-4509-B7A1-4B283CEAB59D'



/*section 1: 设置销售日期和收银机号测试*/

--设置销售日期
exec MPos_Public_changetrandate 'GZ86';
go
--检查销售日期
select * from sysdat where ssshop='GZ86';


/*section 2: 获取收银机号*/
--获取收银机号
-- 使用变量接收存储过程返回值（返回值为INT类型的返回码）
DECLARE @CreateCridReturn INT;
EXEC @CreateCridReturn = MPos_Public_CreateCrid 'GZ86', '2031DC7C-7779-4509-B7A1-4B283CEAB59D';
PRINT 'MPos_Public_CreateCrid 返回码：' + CAST(@CreateCridReturn AS VARCHAR(12));
--检查收银机号
SELECT * FROM Mfcrid WHERE mcshop='GZ86' AND mcmach='2031DC7C-7779-4509-B7A1-4B283CEAB59D';


--临时收银机号(crid): '999'
--临时销售日期(txdt): '2025-12-17'
/*section 3: 创建发票测试*/
--创建发票获取发票号
-- 使用变量获取创建发票的存储过程MPos_Crm01_NewInvo返回的发票号码
-- 假设存储过程有一个 OUTPUT 参数名为 @invno（根据实际参数名调整）
DECLARE @CreateInvReturn INT;
DECLARE @InvoiceNo NVARCHAR(50);

EXEC @CreateInvReturn = MPos_Crm01_NewInvo
  @PCSHOP = 'GZ86',
  @PDTXDT = '2025-12-17',
  @PCCRID = '999'
PRINT 'MPos_Crm01_NewInvo 返回码：' + CAST(@CreateInvReturn AS VARCHAR(12));
PRINT '创建的发票号：' + ISNULL(@InvoiceNo,'');


--假设发票号(invoiceID)为1，检查发票头表和发票明细表