DROP PROCEDURE if exists MPos_Crm01_SubmitInvoice;
GO
CREATE PROCEDURE dbo.MPos_Crm01_SubmitInvoice
   @marketID       char(2),
   @operator       varchar(25),--收银员
   @tranDate       smalldatetime,--销售日期
   @shopID         char(5),--店铺代码
   @crid           char(3),--收银机号
   @invoiceID      int,--发票号
   @cartID         uniqueidentifier,--购物车号
   @memberCard     varchar(25),
   @memberCardType varchar(15),
   @salesAssociate varchar(25),
   @usePromotion   char(1)
AS
   SET NOCOUNT ON;

   DECLARE @lnError int;

   SET @lnError = 0;

   DECLARE @return TABLE
   (
       ReturnID      int,
       ReturnMessage varchar( 256 )
   );

   -- 1. check payment
   IF NOT EXISTS ( SELECT *
                   FROM   dbo.crcinv (NOLOCK) a
                   WHERE  a.TransDate = @tranDate AND
                          a.Shop = @shopID AND
                          a.Crid = @crid )
      BEGIN
         INSERT @return
                (ReturnID,ReturnMessage)
         VALUES ( -1,-- ReturnID - int
                  '没有支付方式' -- ReturnMessage - varchar(256)
         );

         SELECT *
         FROM   @return;

         RETURN;
      END;

   -- 2. check whether  shopping cart is empty.
   IF NOT EXISTS ( SELECT *
                   FROM   crcart (NOLOCK) a
                   WHERE  a.TransDate = @tranDate AND
                          a.Shop = @shopID AND
                          a.Crid = @crid AND
                          a.CartID = @cartID )
      BEGIN
         INSERT @return
                (ReturnID,ReturnMessage)
         VALUES ( -2,-- ReturnID - int
                  '没有支付方式' -- ReturnMessage - varchar(256)
         );

         SELECT *
         FROM   @return;

         RETURN;
      END;

   --2.5 check crsalh exists
   IF EXISTS( SELECT *
              FROM   dbo.crsalh a
              WHERE  a.shtxdt = @tranDate AND
                     a.shshop = @shopID AND
                     a.shcrid = @crid AND
                     a.shinvo = @invoiceID AND
                     a.shupdt = 'Y' )

      BEGIN
         INSERT @return
                (ReturnID,ReturnMessage)
         VALUES ( -3,-- ReturnID - int
                  '该发票号码已经有单据了' -- ReturnMessage - varchar(256)
         );

         SELECT *
         FROM   @return;
      END

   -- 3. create crsalh
   BEGIN TRY
      IF NOT EXISTS( SELECT *
                     FROM   dbo.crsalh a
                     WHERE  a.shtxdt = @tranDate AND
                            a.shshop = @shopID AND
                            a.shcrid = @crid AND
                            a.shinvo = @invoiceID )
         BEGIN
            --DECLARE @t TABLE
            --(
            --   Invo int
            --);
            CREATE TABLE #t
            (
               Invo int
            )

            INSERT INTO #t
            EXEC dbo.MPos_Crm01_NewInvo @PCSHOP = @shopID,-- char(5)
                                        @PDTXDT = @tranDate,-- smalldatetime
                                        @PCCRID = @crid -- char(3)
            SELECT @invoiceID = Invo
            FROM   #t;

            INSERT dbo.crsalh
                   (shtxdt,shshop,shcrid,shinvo,shtxtm,shtqty,shamnt,shuser,shupdt,shvoid,shcust,shsalm,shiden,shforw)
            VALUES ( @tranDate,-- shtxdt - smalldatetime
                     @shopID,-- shshop - char(5)
                     @crid,-- shcrid - char(3)
                     @invoiceID,-- shinvo - int
                     GETDATE(),-- shtxtm - smalldatetime
                     0,-- shtqty - int
                     0,-- shamnt - money
                     @operator,-- shuser - char(40)
                     '',-- shupdt - char(1)
                     '',-- shvoid - char(1)
                     @memberCard,-- shcust - char(10)
                     @salesAssociate,-- shsalm - char(40)
                     '',-- shiden - char(12)
                     '' -- shforw - char(10)
            )
         END
      ELSE
         BEGIN
            UPDATE a

            SET    a.shsalm = @salesAssociate,
                   a.shcust = @memberCard,
                   a.shuser = @operator
            FROM   dbo.crsalh a
            WHERE  a.shtxdt = @tranDate AND
                   a.shshop = @shopID AND
                   a.shcrid = @crid AND
                   a.shinvo = @invoiceID
         END
   END TRY
   BEGIN CATCH
      INSERT @return
             (ReturnID,ReturnMessage)
      VALUES ( -4,-- ReturnID - int
               '创建CRSALH失败：' + ERROR_MESSAGE() -- ReturnMessage - varchar(256)
      );
      SELECT a.ReturnID,a.ReturnMessage
      FROM   @return a;
   END CATCH

   -- 4. create crsald
   -- store promotion calculation result from MPos_Crm01_CalcPromotion
   BEGIN TRY
      IF @usePromotion = 'Y'
         BEGIN
            CREATE TABLE #CalcPromotionResult
            (
               TransDate             smalldatetime,
               Shop                  char( 5 ),
               Crid                  char( 3 ),
               CartID                uniqueidentifier,
               InputTime             smalldatetime,
               Seqn                  int,
               ItemType              char( 1 ),
               Sku                   char( 21 ),
               StyleCode             char( 15 ),
               StyleLocalDescription nvarchar( 100 ),
               Color                 char( 3 ),
               Size                  char( 3 ),
               Price                 money,
               Discount              money,
               Qty                   int,
               DiscountType          char( 1 ),
               PromotionCode         varchar( 12 ),
               promotionDescription  nvarchar( 100 ) DEFAULT '',
               Amnt                  money,
               OPrice                money,
               OAmnt                 money,
               SaleType              char( 1 ),
               Line                  char( 3 ),

               [Change]              char( 1 ),
               Brand                 char( 3 ),
               Cate                  char( 2 ),
               Ptype                 char( 1 ),
               DMark                 money,
               Commision             money,
               PromotionID           varchar( 20 ),
               DiscountID            varchar( 20 ),
               DiscountBrandBit      int,
               DiscountPtyp          char( 1 ),
               GPrice                money,
               LostSales             char( 1 ),
               CumulateValue         char( 1 ),
               VoucherID             varchar( 100 ),
               BrandBit              int,
               SupplierID            varchar( 8 ),
               PantsLength           int,
               Calced                char( 1 ),
               Message               nvarchar( 100 ),
               PPrice                money,
               IsEshop               char( 1 )
            );

            INSERT INTO #CalcPromotionResult
                        (TransDate,Shop,Crid,CartID,InputTime,Seqn,ItemType,Sku,StyleCode,StyleLocalDescription,Color,Size,Price,Discount,Qty,DiscountType,PromotionCode,promotionDescription,Amnt,OPrice,OAmnt,SaleType,Line,[Change],Brand,Cate,Ptype,DMark,Commision,PromotionID,DiscountID,DiscountBrandBit,DiscountPtyp,GPrice,LostSales,CumulateValue,VoucherID,BrandBit,SupplierID,PantsLength,Calced,Message,PPrice,IsEshop)
            -- expected stored proc: MPos_Crm01_CalcPromotion @shopID, @tranDate, @crid, @cartID, @memberCard, @debug
            EXEC MPos_Crm01_CalcPromotion @shopID,@tranDate,@crid,@cartID,@memberCard,'N';
         END

      DELETE FROM a
      FROM   dbo.crsald a
      WHERE  a.sdtxdt = @tranDate AND
             a.sdshop = @shopID AND
             a.sdcrid = @crid AND
             a.sdinvo = @invoiceID

      IF @usePromotion = 'Y'
         BEGIN
            INSERT dbo.crsald

                   (sdtxdt,sdshop,sdcrid,sdinvo,sdseqn,sdtype,sdskun,sdsprc,sdtqty,sddsct,sdvata,sddscd,sdprom)
            SELECT @tranDate AS TransDate,@shopID AS Shop,@crid AS Crid,@invoiceID AS Invo,a.Seqn,a.ItemType,a.Sku,a.OPrice,a.Qty,a.OAmnt - a.Amnt,0 AS sdvata,a.DiscountID,a.PromotionID
            FROM   #CalcPromotionResult a
            WHERE  a.TransDate = @tranDate AND
                   a.Shop = @shopID AND
                   a.Crid = @crid AND
                   a.CartID = @cartID
         END
      ELSE
         BEGIN
            INSERT dbo.crsald
                   (sdtxdt,sdshop,sdcrid,sdinvo,sdseqn,sdtype,sdskun,sdsprc,sdtqty,sddsct,sdvata,sddscd,sdprom)
            SELECT @tranDate AS TransDate,@shopID AS Shop,@crid AS Crid,@invoiceID AS Invo,a.Seqn,a.ItemType,a.Sku,a.OPrice,a.Qty,a.OAmnt - a.Amnt,0 AS sdvata,a.DiscountID,'' AS PromotionID
            FROM   dbo.crcart a
            WHERE  a.TransDate = @tranDate AND
                   a.Shop = @shopID AND
                   a.Crid = @crid AND
                   a.CartID = @cartID
         END
   END TRY
   BEGIN CATCH
      INSERT @return
             (ReturnID,ReturnMessage)
      VALUES ( -5,-- ReturnID - int
               '创建CRSALD失败：' + ERROR_MESSAGE() -- ReturnMessage - varchar(256)
      );
      SELECT a.ReturnID,a.ReturnMessage
      FROM   @return a
      RETURN
   END CATCH

   -- 5. create crctdr
   BEGIN TRY
      DELETE FROM a
      FROM   dbo.crctdr A
      WHERE  A.cttxdt = @tranDate AND
             a.ctshop = @shopID AND
             a.ctcrid = @crid AND
             a.ctinvo = @invoiceID

      INSERT dbo.crctdr
             (cttxdt,ctshop,ctcrid,ctinvo,ctmakt,cttdrt,ctcrdn,ctcurr,ctlamt,ctoamt,ctexrt)
      SELECT A.TransDate,A.Shop,A.Crid,@invoiceID,@marketID,a.tdrt,a.code,a.curr,a.lamt,a.oamt,a.extr
      FROM   dbo.crcinv a
      WHERE  a.TransDate = @tranDate AND
             a.Shop = @shopID AND
             a.Crid = @crid AND

             a.CartID = @cartID
   END TRY
   BEGIN CATCH
      INSERT @return
             (ReturnID,ReturnMessage)
      VALUES ( -6,-- ReturnID - int
               '创建CRCTDR失败：' + ERROR_MESSAGE() -- ReturnMessage - varchar(256)
      );
      SELECT *
      FROM   @return
      RETURN
   END CATCH

   -- 6. create crprop
   BEGIN TRY
      DELETE FROM a
      FROM   dbo.crprop a
      WHERE  a.cptxdt = @tranDate AND
             a.cpshop = @shopID AND
             a.cpcrid = @crid AND
             a.cpinvo = @invoiceID

      INSERT dbo.crprop
             (cptxdt,cpshop,cpcrid,cpinvo,cpprop,cpvalu)
      VALUES ( @tranDate,-- cptxdt - smalldatetime
               @shopID,-- cpshop - char(5)
               @crid,-- cpcrid - char(3)
               @invoiceID,-- cpinvo - int
               'MEMBCARD',-- cpprop - varchar(10)
               @memberCard -- cpvalu - nvarchar(2000)
      )

      INSERT dbo.crprop
             (cptxdt,cpshop,cpcrid,cpinvo,cpprop,cpvalu)
      VALUES( @tranDate,-- cptxdt - smalldatetime
              @shopID,-- cpshop - char(5)
              @crid,-- cpcrid - char(3)
              @invoiceID,-- cpinvo - int
              'MEMBTYPE',-- cpprop - varchar(10)
              @memberCardType -- cpvalu - nvarchar(2000)
      )

      INSERT dbo.crprop
             (cptxdt,cpshop,cpcrid,cpinvo,cpprop,cpvalu)
      VALUES( @tranDate,-- cptxdt - smalldatetime
              @shopID,-- cpshop - char(5)
              @crid,-- cpcrid - char(3)
              @invoiceID,-- cpinvo - int
              'USEPROMO',-- cpprop - varchar(10)
              @usePromotion -- cpvalu - nvarchar(2000)
      )
   END TRY
   BEGIN CATCH
      INSERT @return
             (ReturnID,ReturnMessage)
      VALUES ( -7,-- ReturnID - int
               '创建CRPROP失败：' + ERROR_MESSAGE() -- ReturnMessage - varchar(256)
      );
      SELECT *
      FROM   @return
      RETURN
   END CATCH

   --7. 更新更表头表状态及填写累计金额
   BEGIN TRY

      DECLARE @lmIamt money --货品金额

      DECLARE @lmCamt money --支付金额
      SELECT @lmIamt = sum(CASE
                              WHEN sdtype = 'S' THEN sdtqty * sdsprc - sddsct
                              ELSE sddsct - sdtqty * sdsprc
                           END)
      FROM   crsald
      WHERE  sdshop = @shopID AND
             sdtxdt = @tranDate AND
             sdcrid = @crid AND
             sdinvo = @invoiceID

      SELECT @lmCamt = sum(ctlamt)
      FROM   crctdr
      WHERE  ctshop = @shopID AND
             cttxdt = @tranDate AND
             ctcrid = @crid AND
             ctinvo = @invoiceID

      DECLARE @lnShft int --班次
      SELECT @lnShft = dhshft
      FROM   crcdwh
      WHERE  dhtxdt = @tranDate AND
             dhshop = @shopID AND
             dhcrid = @crid AND
             dhfinv <= @invoiceID AND
             dhtinv >= @invoiceID

      IF @lnShft IS NULL
         SELECT @lnShft = dhshft
         FROM   crcdwh
         WHERE  dhtxdt = @tranDate AND
                dhshop = @shopID AND
                dhcrid = @crid AND
                rtrim(dhclrf) = ''

      IF @lmCamt IS NULL
         SET @lmCamt = 0

      IF @lmIamt IS NULL
         SET @lmIamt = 0

      --9 ti
      UPDATE a
      SET    a.shtqty = ( SELECT sum(CASE
                                        WHEN sdtype = 'S' THEN sdtqty
                                        ELSE -sdtqty
                                     END)
                          FROM   crsald
                          WHERE  sdshop = @shopID AND
                                 sdtxdt = @tranDate AND
                                 sdcrid = @crid AND
                                 sdinvo = @invoiceID ),
             a.shamnt = @lmIamt
      FROM   dbo.crsalh a
      WHERE  a.shtxdt = @tranDate AND
             a.shshop = @shopID AND
             a.shcrid = @crid AND
             a.shinvo = @invoiceID
   END TRY
   BEGIN CATCH
      INSERT @return

             (ReturnID,ReturnMessage)
      VALUES ( -8,-- ReturnID - int
               '更新CRSALH汇总失败：' + ERROR_MESSAGE() -- ReturnMessage - varchar(256)
      );
   END CATCH

   --UPDATE a SET a.shupdt='Y' FROM crsalh a WHERE a.shtxdt= @tranDate AND a.shcrid=@crid AND a.shshop = @shopID AND a.shinvo = @invoiceID
   IF @lnError < 0
      BEGIN
         DELETE FROM crsald
         WHERE  sdshop = @shopID AND
                sdtxdt = @tranDate AND
                sdcrid = @crid AND
                sdinvo = @invoiceID

         DELETE FROM crctdr
         WHERE  ctshop = @shopID AND
                cttxdt = @tranDate AND
                ctcrid = @crid AND
                ctinvo = @invoiceID

         DELETE FROM crprop
         WHERE  cpshop = @shopID AND
                cptxdt = @tranDate AND
                cpcrid = @crid AND
                cpinvo = @invoiceID

         DELETE FROM crsalh
         WHERE  shshop = @shopID AND
                shtxdt = @tranDate AND
                shcrid = @crid AND
                shinvo = @invoiceID
      END

   IF @lnError >= 0
      BEGIN
	  
         INSERT @return
                (ReturnID,ReturnMessage)
         VALUES ( 1,-- ReturnID - int
                  @invoiceID--'发票提交成功' -- ReturnMessage - varchar(256)
         );
      END

   SELECT a.ReturnID,a.ReturnMessage
   FROM   @return a 
 
