DROP PROCEDURE if exists MPOS_Crm01_CalcCompaign
GO
CREATE PROCEDURE MPOS_Crm01_CalcCompaign
   @shopID          char(5),
   @transactionDate smalldatetime,
   @crid            char(3),
   @cartID          uniqueidentifier,
   @memberCard      char(10) = '',
   @debug           char(1) = 'N'
AS
   DECLARE @memberRegion char(3)

   SET @memberRegion = ''

   IF (rtrim(@memberCard) <> '')
      BEGIN
         SELECT @memberRegion = cdregn
         FROM   cccard(NOLOCK)
         WHERE  cdcard = @memberCard

         IF @memberRegion IS NULL
            SET @memberRegion = ''
      END

   IF @memberCard IS NULL
      SET @memberCard = ''

   DECLARE @memberCustID char(10)

   IF (rtrim(@memberCard) <> '')
      SELECT @memberCustID = cdcust
      FROM   cccard(NOLOCK)
      WHERE  cdcard = @memberCard

   IF @memberCustID IS NULL
      SET @memberCustID = ''

   DECLARE @sysDate smalldatetime

   SELECT @sysDate = sstxdt
   FROM   sysdat
   WHERE  ssshop = @shopID

   DECLARE @Items TABLE
   (
       Itskun char( 21 ),
       ItStyl char( 15 ),
       Itsequ smallint,
       Itnseq smallint IDENTITY,
       Itpric money,
       Itnpri money,
       Itprom char( 12 ),
       Itbuse char( 1 ),
       Itupri money,
       Itudsc int,
       Itquty int,
       Ituqty int DEFAULT 0,
       Ittype char( 1 ),
       Itpsty char( 15 ) DEFAULT '',
       PRIMARY KEY CLUSTERED (Itnseq)
   )

   CREATE TABLE #crcart
   (
      [TransDate]             smalldatetime,
      [Shop]                  char( 5 ),
      [Crid]                  char( 3 ),
      [CartID]                uniqueidentifier,
      [InputTime]             smalldatetime,
      [Seqn]                  int,
      [ItemType]              char( 1 ),
      [Sku]                   char( 21 ),
      [StyleCode]             char( 15 ),
      [StyleLocalDescription] nvarchar( 100 ),
      [Color]                 char( 3 ),
      [Size]                  char( 3 ),
      [Price]                 money,
      [Discount]              money,


      [Qty]                   int,
      [DiscountType]          char( 1 ),
      [PromotionCode]         varchar( 12 ),
      [PromotionDescription]  nvarchar( 100 ) DEFAULT '',
      [Amnt]                  money,
      [OPrice]                money,
      [OAmnt]                 money,
      [SaleType]              char( 1 ),
      [Line]                  char( 3 ),
      [Change]                char( 1 ) DEFAULT '',
      [Brand]                 char( 3 ),
      [Cate]                  char( 2 ),
      [Ptype]                 char( 1 ),
      [DMark]                 money,
      [Commision]             money,
      [PromotionID]           varchar( 20 ),
      [DiscountID]            varchar( 20 ),
      [DiscountBrandBit]      int,
      [DiscountPtyp]          char( 1 ),
      [GPrice]                money,
      [LostSales]             char( 1 ) DEFAULT '',
      [CumulateValue]         char( 1 ) DEFAULT '',
      [VoucherID]             varchar( 100 ) DEFAULT '',
      [BrandBit]              int,
      [SupplierID]            varchar( 8 ),
      [PantsLength]           int DEFAULT 0,
      [Calced]                char( 1 ) DEFAULT '',
      [Message]               nvarchar( 100 ) DEFAULT '',
      [PPrice]                money DEFAULT 0,
      [IsEshop]               char( 1 ) DEFAULT '',
      [Salm]                  varchar( 20 ) DEFAULT ''
   )

   ----放入备算表                                                                            
   INSERT @Items
          (Itskun,ItStyl,Itsequ,Itpric,Itnpri,Itprom,Itbuse,Itupri,Itudsc,Itquty,Ittype,Itpsty)
   SELECT Sku,a.StyleCode,Seqn,Oprice,Price,'','N',0,0,Qty,PType,StyleCode
   FROM   crcart(NOLOCK) a
   WHERE  CartID = @cartID AND
          ItemType = 'S'

   ----计算promotion                                                                              
   DECLARE @phtxnt char(8)

   DECLARE @phtype int

   DECLARE @phfdat smalldatetime

   DECLARE @phtdat smalldatetime



   DECLARE @phtime smallint

   DECLARE @pdcamt money

   DECLARE @pdcqty int

   DECLARE @pdovex char(1)

   DECLARE @pdscop varchar(15)

   DECLARE @pdupri money

   DECLARE @pdudsc int

   DECLARE @lnMinSequ int

   DECLARE @lnMatchQty int

   DECLARE @lnSelectedAmt money

   DECLARE @lnSelectedQty int

   DECLARE @lnPromoBeforeQty int

   DECLARE @lnPromoAfterQty int

   DECLARE @lcSuccess char(1)

   DECLARE @lnItemQty int

   DECLARE @lnItemUQty int

   DECLARE @lnItemCQty int

   CREATE TABLE #tpomh
   (
      tphtxnt char( 16 ),
      PRIMARY KEY CLUSTERED (tphtxnt)
   )

   INSERT #tpomh
          (tphtxnt)
   SELECT phtxnt
   FROM   crpomh(NOLOCK)
   WHERE  phshop = @shopID AND
          (phvrgn = ''  OR
           phvrgn = @memberRegion) AND
          phcanx <> 'Y' AND
          phfdat <= @sysDate AND
          @sysDate <= phtdat
   ORDER  BY Phtxnt DESC

   --去除只有会员限定的促销活动
   DELETE FROM #tpomh
   FROM   crpomh(NOLOCK)
   WHERE  phshop = @shopID AND
          phtxnt = tphtxnt AND
          phvlmt = 'Y' AND
          @memberCard = ''

   --去除只有指定某会员限定的促销活动
   DELETE FROM #tpomh
   FROM   crpomh(NOLOCK)
   WHERE  phshop = @shopID AND
          phtxnt = tphtxnt AND
          phvlmt = 'Y' AND
          NOT EXISTS ( SELECT *
                       FROM   crpmct(NOLOCK)
                       WHERE  pcpomo = phtxnt AND
                              pccust = @memberCustID )

   IF (@debug = 'Y')
      SELECT tphtxnt
      FROM   #tpomh
      ORDER  BY tphtxnt DESC

   DECLARE Cur_pomh CURSOR FOR
      SELECT tphtxnt
      FROM   #tpomh
      ORDER  BY tphtxnt DESC

   OPEN Cur_pomh

   FETCH NEXT FROM Cur_pomh INTO @phtxnt

   WHILE (@@FETCH_STATUS <> -1)
      BEGIN
         IF (@@FETCH_STATUS <> -2)
            BEGIN
               IF @debug = 'Y'
                  BEGIN
                     SELECT @phtxnt
                  END

               SELECT @lnPromoBeforeQty = 0,@lnPromoAfterQty = -1



               WHILE (@lnPromoBeforeQty <> @lnPromoAfterQty)
                  BEGIN
                     PRINT 'before after'

                     PRINT @lnPromoBeforeQty

                     PRINT @lnPromoAfterQty

                     SELECT @lnPromoBeforeQty = Sum(Itquty)
                     FROM   @Items
                     WHERE  Itbuse = 'Y'

                     IF @lnPromoBeforeQty IS NULL
                        SELECT @lnPromoBeforeQty = 0

                     SELECT @lcSuccess = 'Y'

                     DECLARE Cur_pomd CURSOR FOR
                        SELECT pdscop,pdcamt,pdcqty,pdovex,pdupri,pdudsc
                        FROM   crpomd(NOLOCK)
                        WHERE  pdshop = @shopID AND
                               Pdtxnt = @phtxnt
                        ORDER  BY Pdtxnt DESC,Pdseqn

                     OPEN Cur_pomd

                     FETCH NEXT FROM Cur_pomd INTO @pdscop,
                                                   @pdcamt,
                                                   @pdcqty,
                                                   @pdovex,
                                                   @pdupri,
                                                   @pdudsc

                     WHILE (@@FETCH_STATUS <> -1)
                        BEGIN
                           IF (@@FETCH_STATUS <> -2)
                              BEGIN
                                 SELECT @lnSelectedAmt = 0

                                 SELECT @lnSelectedQty = 0

                                 IF (@debug = 'Y')
                                    BEGIN
                                       SELECT *
                                       FROM   @Items
                                       WHERE  Dbo.MPOS_CRM01_CheckPromotionSkuMatch(@pdscop, itskun, ItStyl, Ittype) = 1 AND
                                              Itquty > Ituqty AND
                                              Itbuse <> 'Y'


                                    END

                                 SELECT @lnMinSequ = Min(Itnseq)
                                 FROM   @Items
                                 WHERE  Dbo.MPOS_CRM01_CheckPromotionSkuMatch(@pdscop, itskun, ItStyl, Ittype) = 1 AND
                                        Itquty > Ituqty AND
                                        Itbuse <> 'Y'

                                 WHILE (@lnMinSequ IS NOT NULL)
                                    BEGIN
                                       IF NOT (@pdovex = 'E' AND
                                               @lnSelectedAmt >= @pdcamt AND
                                               @lnSelectedQty >= @pdcqty)
                                          BEGIN
                                             SELECT @lnItemQty = 0

                                             SELECT @lnItemUQty = 0

                                             SELECT @lnItemQty = Itquty,@lnItemUQty = Ituqty
                                             FROM   @Items
                                             WHERE  Itnseq = @lnMinSequ

                                             IF (@lnItemQty >= @lnItemUQty + @pdcqty)
                                                UPDATE @Items
                                                SET    Itprom = @phtxnt,
                                                       Itupri = @pdupri,
                                                       Itudsc = @pdudsc,
                                                       Ituqty = Ituqty + (CASE
                                                                             WHEN @pdcqty = 0 THEN 1
                                                                             ELSE @pdcqty
                                                                          END),
                                                       Itbuse = 'M'
                                                WHERE  Itnseq = @lnMinSequ


                                             ELSE
                                                UPDATE @Items
                                                SET    Itprom = @phtxnt,
                                                       Itupri = @pdupri,
                                                       Itudsc = @pdudsc,
                                                       Ituqty = @lnItemQty,
                                                       Itbuse = 'M'
                                                WHERE  Itnseq = @lnMinSequ

                                             SELECT @lnSelectedAmt = @lnSelectedAmt + Itnpri * Ituqty,@lnSelectedQty = @lnSelectedQty + Ituqty
                                             FROM   @Items
                                             WHERE  Itnseq = @lnMinSequ

                                             IF (@debug = 'Y')
                                                BEGIN
                                                   SELECT *
                                                   FROM   @Items
                                                   WHERE  Dbo.MPOS_CRM01_CheckPromotionSkuMatch(@pdscop, itskun, itstyl, Ittype) = 1 AND
                                                          Itquty > Ituqty AND
                                                          Itbuse <> 'Y'
                                                END

                                             SELECT @lnMinSequ = Min(Itnseq)
                                             FROM   @Items
                                             WHERE  Dbo.MPOS_CRM01_CheckPromotionSkuMatch(@pdscop, itskun, itstyl, Ittype) = 1 AND
                                                    Itquty > Ituqty AND
                                                    Itbuse <> 'Y'
                                          END
                                       ELSE
                                          SELECT @lnMinSequ = NULL

                                    END


                                 IF @debug = 'Y'
                                    BEGIN
                                       PRINT '@lnSelectedAmt:'

                                       PRINT CONVERT(varchar, @lnSelectedAmt)

                                       PRINT '@pdcamt:'

                                       PRINT CONVERT(varchar, @pdcamt)
                                    END

                                 IF NOT (@lnSelectedAmt >= @pdcamt AND
                                         @lnSelectedQty >= @pdcqty)
                                    BEGIN
                                       SELECT @lcSuccess = 'N'

                                       BREAK
                                    END
                              END

                           FETCH NEXT FROM Cur_pomd INTO @pdscop,
                                                         @pdcamt,
                                                         @pdcqty,
                                                         @pdovex,
                                                         @pdupri,
                                                         @pdudsc
                        END

                     CLOSE Cur_pomd

                     DEALLOCATE Cur_pomd

                     IF @lcSuccess = 'Y'
                        BEGIN
                           DECLARE @lnMaxSeqn int

                           INSERT @Items
                                  (Itskun,Itsequ,Itpric,Itnpri,Itprom,Itbuse,Itupri,Itudsc,Itquty,Ittype,Itpsty)
                           SELECT Itskun,Itsequ,Itpric,Itnpri,'','N',0,0,(Itquty - Ituqty),Ittype,Itpsty
                           FROM   @Items
                           WHERE  Itbuse = 'M' AND
                                  (Itquty - Ituqty) > 0

                           UPDATE @Items
                           SET    Itnpri = (CASE
                                               WHEN Itudsc <> 0 THEN Itnpri * (100 - Itudsc) / 100


                                               ELSE Itupri
                                            END),
                                  Itbuse = 'Y',
                                  Itquty = Ituqty
                           WHERE  Itprom = @phtxnt AND
                                  Itbuse = 'M'
                        END
                     ELSE
                        --@lcSuccess = 'N'                                                               
                        BEGIN
                           UPDATE @Items
                           SET    Itprom = '',
                                  Itbuse = 'N',
                                  Itupri = 0,
                                  Itudsc = 0,
                                  Ituqty = 0
                           WHERE  Itprom = @phtxnt AND
                                  Itbuse = 'M'
                        END

                     SELECT @lnPromoAfterQty = Sum(Itquty)
                     FROM   @Items
                     WHERE  Itbuse = 'Y'

                     IF @lnPromoAfterQty IS NULL
                        SELECT @lnPromoAfterQty = 0

                     IF @debug = 'Y'
                        SELECT *
                        FROM   @Items
                  END --while (@lnPromoBeforeQty <> @lnPromoAfterQty)                     
            END

         FETCH NEXT FROM Cur_pomh INTO @phtxnt
      END

   CLOSE Cur_pomh

   DEALLOCATE Cur_pomh

   IF @debug = 'Y'
      BEGIN
         PRINT '@item'

         SELECT *
         FROM   @Items
      END

   INSERT #crcart
          (ItemType,Seqn,Sku,PPrice,Qty,PromotionID)
   SELECT 'S',Itsequ,Itskun,Avg(itnpri),sum(Itquty),Itprom
   FROM   @Items
   GROUP  BY Itsequ,Itskun,Itprom,Ittype,Itprom

   IF @debug = 'Y'
      BEGIN
         PRINT '@item'

         SELECT *
         FROM   @Items

         SELECT *
         FROM   #crcart
      END

   UPDATE a
   SET    a.InputTime = b.InputTime,


          a.StyleCode = b.StyleCode,
          a.Color = b.Color,
          a.Size = b.Size,
          a.Price = b.Price,
          a.Discount = b.Discount,
          a.DiscountType = b.DiscountType,
          a.OPrice = b.OPrice,
          a.OAmnt = b.OAmnt,
          a.Amnt = b.Amnt,
          a.SaleType = b.SaleType,
          a.Line = b.Line,
          a.Change = b.Change,
          a.Brand = b.Brand,
          a.Cate = b.Cate,
          a.Ptype = b.Ptype,
          a.DMark = b.DMark,
          a.Commision = b.Commision,
          a.DiscountID = b.DiscountID,
          a.PromotionCode = b.PromotionCode,
          a.DiscountBrandBit = b.DiscountBrandBit,
          a.DiscountPtyp = b.DiscountPtyp,
          a.GPrice = b.GPrice,
          a.LostSales = b.LostSales,
          a.CumulateValue = b.CumulateValue,
          a.VoucherID = b.VoucherID,
          a.BrandBit = b.BrandBit,
          a.SupplierID = b.SupplierID,
          a.PantsLength = b.PantsLength,
          a.Calced = b.Calced,
          a.Message = b.Message,
          a.IsEshop = b.IsEshop,
		  a.Salm = b.Salm
   FROM   #crcart a,
          crcart b
   WHERE  a.Seqn = b.Seqn AND
          a.sku = b.sku AND
          b.CartID = @cartID

   UPDATE #crcart
   SET    Price = PPrice,
          Amnt = PPrice * Qty,
          Discount = 0,
          DiscountID = '',
          DiscountType = '',
          DiscountPtyp = ''
   WHERE  Change <> 'Y' AND
          PromotionID <> ''

   INSERT #crcart
          ([InputTime],[seqn],[ItemType],[Sku],[StyleCode],[Color],[Size],[Price],[Discount],[Qty],[DiscountType],[PromotionCode],[Amnt],[OPrice],[OAmnt],[SaleType],[Line],[Change],[Brand],[Cate],[Ptype],[DMark],[Commision],[PromotionID],[DiscountID],[DiscountBrandBit],[DiscountPtyp],[GPrice],[LostSales],[CumulateValue],[VoucherID],[BrandBit],[SupplierID],[PantsLength],[Calced],[Message],[IsEshop],[Salm])
   SELECT [InputTime],[seqn],[ItemType],[Sku],[StyleCode],[Color],[Size],[Price],[Discount],[Qty],[DiscountType],[PromotionCode],[Amnt],[OPrice],[OAmnt],[SaleType],[Line],[Change],[Brand],[Cate],[Ptype],[DMark],[Commision],[PromotionID],[DiscountID],[DiscountBrandBit],[DiscountPtyp],[GPrice],[LostSales],[CumulateValue],[VoucherID],[BrandBit],[SupplierID],[PantsLength],[Calced],[Message],[IsEshop],[Salm]


   FROM   crcart
   WHERE  TransDate = @transactionDate AND
          Shop = @shopID AND
          crid = @crid AND
          CartID = @cartID AND
          ItemType <> 'S'

   UPDATE #crcart
   SET    [TransDate] = @transactionDate,
          [Shop] = @shopID,
          [Crid] = @crid,
          [CartID] = @cartID

   UPDATE a
   SET    a.PromotionDescription = b.phdesc
   FROM   #crcart a,
          crpomh(NOLOCK) b
   WHERE  a.PromotionID = b.phtxnt

   UPDATE a
   SET    a.StyleLocalDescription = b.smldes
   FROM   #crcart a,
          mfstyl(NOLOCK) b
   WHERE  a.StyleCode = b.smcode

   SELECT *
   FROM   #crcart 
 
 
