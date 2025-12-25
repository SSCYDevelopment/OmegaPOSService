CREATE PROCEDURE dbo.MPos_Crm01_GetReceiptData
   @pShopid varchar(21),
   @pCrid   char(3),
   @pInvo   int
AS
   SET NOCOUNT ON

   CREATE TABLE #receiptH
   (
      ShopId      varchar( 5 ),
      ShopName    varchar( 20 ),
      ShopTele    varchar( 20 ),
      SalesData   varchar( 20 ),
      InvoiceNo   int,
      Salesperson varchar( 20 ),
      Cashier     varchar( 20 ),
      Qty         int,
      Amount      money,
      WarmTips    varchar( MAX ),
      FBTips      varchar( MAX ),
      InvoTips    varchar( MAX ),
   )

   CREATE TABLE #receiptD
   (
      ShopId       varchar( 5 ),
      Seqn         int,
      SType        varchar( 20 ),
      ProductSkuId varchar( 25 ),
      ProductName  varchar( 100 ),
      UnitPrice    money,
      Qty          int,
      TotalPrice   money
   )

   BEGIN
      PRINT '1'

      IF NOT EXISTS ( SELECT *
                      FROM   dbo.crsalh(NOLOCK)
                      WHERE  shshop = @pShopid AND
                             shcrid = @pCrid AND
                             shinvo = @pInvo )
         BEGIN
            SELECT 0 code,'没有找到相应的销售数据' msg

            RETURN
         END

      PRINT '1'

      INSERT #receiptH
             (ShopId,SalesData,InvoiceNo,Salesperson,Cashier,Qty,Amount)
      -- 销售主表
      SELECT shshop,CONVERT(VARCHAR(19), shtxdt, 120),shinvo,shuser,shuser,shtqty,shamnt
      FROM   dbo.crsalh(NOLOCK)
      WHERE  shshop = @pShopid AND
             shcrid = @pCrid AND
             shinvo = @pInvo

      INSERT #receiptD
             (ShopId,Seqn,SType,ProductSkuId,UnitPrice,Qty,TotalPrice)
      -- 销售明细表
      SELECT sdshop,sdseqn,sdtype,sdskun,sdsprc,sdtqty,sdsprc
      FROM   dbo.crsald(NOLOCK)
      WHERE  sdshop = @pShopid AND
             sdcrid = @pCrid AND
             sdinvo = @pInvo

      -- 店铺信息更新
      UPDATE a
      SET    a.ShopName = b.shldes,
             a.ShopTele = b.shtele
      FROM   #receiptH a,

             dbo.mfshop(NOLOCK) b
      WHERE  a.ShopId = b.shshop

      BEGIN -- 提示语更新
         IF EXISTS ( SELECT *
                     FROM   #receiptH a,dbo.syconf(NOLOCK) b
                     WHERE  a.ShopId = b.cnshop AND
                            b.cnprop = 'WarmTips' )
            BEGIN
               UPDATE a
               SET    a.WarmTips = b.cnvalu
               FROM   #receiptH a,
                      dbo.syconf(NOLOCK) b
               WHERE  a.ShopId = b.cnshop AND
                      b.cnprop = 'WarmTips'
            END

         IF EXISTS ( SELECT *
                     FROM   #receiptH a,dbo.syconf(NOLOCK) b
                     WHERE  a.ShopId = b.cnshop AND
                            b.cnprop = 'FBTips' )
            BEGIN
               UPDATE a
               SET    a.FBTips = b.cnvalu
               FROM   #receiptH a,
                      dbo.syconf(NOLOCK) b
               WHERE  a.ShopId = b.cnshop AND
                      b.cnprop = 'FBTips'
            END

         IF EXISTS ( SELECT *
                     FROM   #receiptH a,dbo.syconf(NOLOCK) b
                     WHERE  a.ShopId = b.cnshop AND
                            b.cnprop = 'InvoTips' )
            BEGIN
               UPDATE a
               SET    a.InvoTips = b.cnvalu
               FROM   #receiptH a,
                      dbo.syconf(NOLOCK) b
               WHERE  a.ShopId = b.cnshop AND
                      b.cnprop = 'InvoTips'
            END
      END

      UPDATE a
      SET    a.ProductName = c.smldes
      FROM   #receiptD a,
             dbo.mfskun(NOLOCK) b,
             dbo.mfstyl(NOLOCK) c
      WHERE  a.ProductSkuId = b.skskun AND
             b.skstyl = c.smstyl

      SELECT 1 code,'查询成功' msg

      SELECT *
      FROM   #receiptH

      SELECT *
      FROM   #receiptD
   END 
 
