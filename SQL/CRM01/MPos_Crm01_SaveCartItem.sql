DROP PROC MPos_Crm01_SaveCartItem;

GO

CREATE PROC MPos_Crm01_SaveCartItem
   @TransDate        smalldatetime,--交易日期
   @Shop             char(5),--店铺
   @Crid             char(3),--收银机号
   @CartID           uniqueidentifier,--购物车ID
   @Seqn             int,--购物车商品序号
   @ItemType         char(1),--销售类型 卖/退
   @skuBarcode       char(21),--条码
   @StyleCode        char(15),--货号/款号
   @Color            char(3),-- 颜色
   @Size             char(3),--尺码
   @qty              int,--数量
   @Weight           money,--重量
   @Price            money,--价格
   @OPrice           money,--原价
   @Amnt             money,
   @OAmnt            money,--原价金额合计
   @Discount         money,--折扣
   @DiscountType     char(1),--折扣类型
   @DiscountID       varchar(20),--折扣代码
   @DiscountBrandBit int,--折扣可用品牌
   @DiscountPtyp     char(1),--折扣可用付款方式
   @PromotionCode    varchar(12),
   @PromotionID      varchar(20),--促销代码
   @Message          nvarchar(100) = '',
   @Change           char(1) = '',
   @SaleType         char(1) = '',
   @Line             char(3) = '',
   @Brand            char(3) = '',
   @Cate             char(2) = '',
   @Ptype            char(1) = '',
   @Calced           char(1) = '',
   @Commision        money = 0,
   @GPrice           money = 0,
   @LostSales        char(1) = '',
   @CumulateValue    char(1) = '',
   @VoucherID        varchar(100) = '',
   @BrandBit         int = -1,
   @SupplierID       varchar(8) = '',
   @PantsLength      int = 0,
   @isEShop          char(1) = '',
   @Salm             varchar(20) =''
AS
   SET XACT_ABORT ON;

   BEGIN TRANSACTION;

   IF @Seqn = -1
      BEGIN
         IF NOT EXISTS ( SELECT *
                         FROM   crcart
                         WHERE  TransDate = @TransDate AND
                                Shop = @Shop AND
                                Crid = @Crid AND
                                CartID = @CartID )
            SELECT @Seqn = 1;
         ELSE
            BEGIN
               SELECT @Seqn = MAX(Seqn)

               FROM   crcart
               WHERE  TransDate = @TransDate AND
                      Shop = @Shop AND
                      Crid = @Crid AND
                      CartID = @CartID;

               SELECT @Seqn = @Seqn + 1;
            END;
      END;

   DELETE crcart
   WHERE  TransDate = @TransDate AND
          Shop = @Shop AND
          Crid = @Crid AND
          CartID = @CartID AND
          Seqn = @Seqn;

   INSERT crcart
          (TransDate,Shop,Crid,CartID,Seqn,ItemType,Sku,StyleCode,Color,Size,Price,Discount,Qty,DiscountType,PromotionCode,Amnt,OPrice,OAmnt,SaleType,Line,Change,Brand,Cate,Ptype,DMark,Commision,PromotionID,DiscountID,DiscountBrandBit,DiscountPtyp,GPrice,LostSales,CumulateValue,VoucherID,BrandBit,SupplierID,PantsLength,Calced,[Message],InputTime,IsEshop,Salm)
   SELECT @TransDate,@Shop,@Crid,@CartID,@Seqn,@ItemType,@skuBarcode,@StyleCode,@Color,@Size,@Price,@Discount,@qty,@DiscountType,@PromotionCode,@Amnt,@OPrice,@OAmnt,@SaleType,@Line,@Change,@Brand,@Cate,@Ptype,@Weight,@Commision,@PromotionID,@DiscountID,@DiscountBrandBit,@DiscountPtyp,@GPrice,@LostSales,@CumulateValue,@VoucherID,@BrandBit,@SupplierID,@PantsLength,@Calced,@Message,GETDATE(),@isEShop,@Salm;

   IF NOT EXISTS ( SELECT *
                   FROM   crcarh
                   WHERE  TransDate = @TransDate AND
                          Shop = @Shop AND
                          Crid = @Crid AND
                          CartID = @CartID )
      BEGIN
         INSERT crcarh
                (TransDate,Shop,Crid,CartID,wwscard,salm,defective,usepromotion)
         SELECT @TransDate,@Shop,@Crid,@CartID,'','','','';
      END;

   COMMIT TRAN; 
 
GO 

--test
--PRINT NEWID()
--'F7DCD6D6-9042-43E4-82F1-09D65847F08C'
EXEC MPos_Crm01_SaveCartItem @TransDate='2025-12-1',@Shop='GZ86',@Crid='001',@Seqn = 1, @ItemType = 'S',@skuBarcode='123456789ABCDEF',@Color='ABC',@Size='DEF',@Price=289,@OPrice=489,@Amnt=289,@OAmnt=489,@Discount=0,@DiscountType='',@DiscountID='',@DiscountBrandBit=0,@PromotionCode='',@PromotionID='',@CartId='F7DCD6D6-9042-43E4-82F1-09D65847F08C',@StyleCode='123456789',@qty=1, @Weight=250,@DiscountPtyp='' 
GO
EXEC MPos_Crm01_GetCartItems @CartID='F7DCD6D6-9042-43E4-82F1-09D65847F08C',@Shop='GZ86', @Crid='001',@TransDate='2025-12-1'
