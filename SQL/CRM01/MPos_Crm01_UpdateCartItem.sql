CREATE PROC dbo.MPos_Crm01_UpdateCartItem
   @TransDate smalldatetime,--交易日期
   @Shop      char(5),--店铺
   @Crid      char(3),--收银机号
   @CartID    uniqueidentifier,--购物车ID
   @Seqn      int,--购物车商品序号
   @qty       int,--数量
   @Salm      varchar(20) =''
AS
   SET XACT_ABORT ON;

   BEGIN TRANSACTION;

   IF EXISTS ( SELECT *
               FROM   dbo.crcart(NOLOCK) a
               WHERE  a.TransDate = @TransDate AND
                      a.Shop = @Shop AND
                      a.Crid = @Crid AND
                      a.CartID = @CartID AND
                      a.Seqn = @Seqn )
      BEGIN
         IF @qty <> -1
            BEGIN
               UPDATE a
               SET    a.Qty = @qty,
                      a.Amnt = a.Price * @qty
               FROM   dbo.crcart(NOLOCK) a
               WHERE  a.TransDate = @TransDate AND
                      a.Shop = @Shop AND
                      a.Crid = @Crid AND
                      a.CartID = @CartID AND
                      a.Seqn = @Seqn
            END

         IF @Salm <> ''
            BEGIN
               UPDATE a
               SET    a.Salm = @Salm
               FROM   dbo.crcart(NOLOCK) a
               WHERE  a.TransDate = @TransDate AND
                      a.Shop = @Shop AND
                      a.Crid = @Crid AND
                      a.CartID = @CartID AND
                      a.Seqn = @Seqn
            END
      END

   COMMIT TRAN; 
 
