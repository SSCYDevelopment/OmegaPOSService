DROP PROC MPos_Crm01_Update
go
CREATE PROCEDURE MPos_Crm01_Update
  @shopID      char(5),
  @TransDate      smalldatetime,
  @crid      char(3),
  @invoiceID      int,
  @discountAmount   money=0,
  @redeemAmount money=0, --预留
  @redeemQuantity smallint=0 --预留
AS
    DECLARE @lmCamt money
    DECLARE @lmIamt money --货品总金额
    DECLARE @lnShft int
    DECLARE @lcMakt char(2)
    DECLARE @lnVatr decimal(5, 2)
    DECLARE @lnDEC smallint
    DECLARE @lcCard char(10)
    DECLARE @lcKind char(3)
    DECLARE @lcIden char(10)
    DECLARE @lmEdcr money
    DECLARE @lmEdpt money
    DECLARE @lnOdds smallint
    DECLARE @lnFixc smallint
    DECLARE @lnCurc smallint
    DECLARE @lcPomo varchar(12)
    DECLARE @lcMeed char(1)
    DECLARE @lnDInv int
    DECLARE @lnDQty int
    DECLARE @lnDamt money
    DECLARE @lnRInv int
    DECLARE @lnRQty int
    DECLARE @lnRAmt money
    DECLARE @lnTqty int
    DECLARE @lnTAmt money
    DECLARE @lnError int
    DECLARE @lcPara char(40)

    SELECT @lcPara = CONVERT(char(8), @TransDate, 112) + '  ' + @shopID
                     + @crid + CONVERT(char(5), @invoiceID)

    --计算能抵扣货款的coupon      
    DECLARE @lnXCouponSum money
    DECLARE @lnXCrsaldSum money
    DECLARE @lnXShareSum money
    DECLARE @lnXCrsaldMaxAmntSeqn int
    DECLARE @lnXCrsaldMaxAmnt money
    DECLARE @tctdr TABLE
    (
       tttdrt char( 1 ),
       ttcurr char( 3 ),
       ttlamt money,
       ttoamt money
    )

    SELECT @lcMakt = shmakt
    FROM   mfshop(nolock)
    WHERE  shshop = @shopID

    SELECT @lnVatr = CONVERT(decimal(5, 2), cnvalu)
    FROM   syconf
    WHERE  cnshop = @shopID AND
           rtrim(cnprop) = 'VATRATE'


    SELECT @lnDEC = CASE
                      WHEN cnvalu = '' THEN 2
                      ELSE CONVERT(smallint, cnvalu)
                    END
    FROM   syconf
    WHERE  cnshop = @shopID AND
           rtrim(cnprop) = 'TDECIMAL'

    --获取货品总金额
    SELECT @lmIamt = sum(CASE
                           WHEN sdtype = 'S' THEN sdtqty * sdsprc - sddsct
                           ELSE sddsct - sdtqty * sdsprc
                         END)
    FROM   crsald
    WHERE  sdshop = @shopID AND
           sdtxdt = @TransDate AND
           sdcrid = @crid AND
           sdinvo = @invoiceID

    --获取支付方式总金额
    SELECT @lmCamt = sum(ctlamt)
    FROM   crctdr
    WHERE  ctshop = @shopID AND
           cttxdt = @TransDate AND
           ctcrid = @crid AND
           ctinvo = @invoiceID

    --获取当前更次
    SELECT @lnShft = dhshft
    FROM   crcdwh
    WHERE  dhtxdt = @TransDate AND
           dhshop = @shopID AND
           dhcrid = @crid AND
           dhfinv <= @invoiceID AND
           dhtinv >= @invoiceID
    --若未获取到更次，则取当天第一笔交易的更次
    IF @lnShft IS NULL
      SELECT @lnShft = dhshft
      FROM   crcdwh
      WHERE  dhtxdt = @TransDate AND
             dhshop = @shopID AND
             dhcrid = @crid AND
             rtrim(dhclrf) = ''

    IF @lmCamt IS NULL
      SET @lmCamt = 0

    SET @lmCamt = @lmCamt + @discountAmount
    SET @lcMeed = 'N'

    IF @lmCamt = @lmIamt  OR
       floor(@lmCamt) = floor(@lmIamt)  OR
       ceiling(@lmCamt) = ceiling(@lmIamt)  OR
       floor(@lmCamt) = ceiling(@lmIamt)  OR
       ceiling(@lmCamt) = floor(@lmIamt)  OR
       round(@lmCamt, @lnDEC, abs(@lnDEC)) = round(@lmIamt, @lnDEC, abs(@lnDEC))
      BEGIN
          SET xact_abort ON

          BEGIN TRANSACTION

          --计算能抵扣货款的coupon
          SELECT @lnXCouponSum = sum(ctlamt)
          FROM   crctdr,mftdrt
          WHERE  cttdrt = tdtdrt AND
                 ctmakt = tdmakt AND
                 ctshop = @shopID AND
                 cttxdt = @TransDate AND
                 ctcrid = @crid AND
                 ctinvo = @invoiceID AND
                 tdtype&1 = 1

          IF @lnXCouponSum IS NULL
            SET @lnXCouponSum = 0

          SET @lnXCouponSum = @lnXCouponSum + @discountAmount

          IF @lnXCouponSum > 0
            BEGIN
                SELECT @lnXCrsaldSum = sum(sdsprc * sdtqty - sddsct)
                FROM   crsald
                WHERE  sdshop = @shopID AND
                       sdtxdt = @TransDate AND
                       sdcrid = @crid AND
                       sdinvo = @invoiceID AND
                       sdtype = 'S'

                SELECT @lnXShareSum = sum(floor(( ( sdsprc * sdtqty - sddsct ) / @lnXCrsaldSum ) * @lnXCouponSum))
                FROM   crsald
                WHERE  sdshop = @shopID AND
                       sdtxdt = @TransDate AND
                       sdcrid = @crid AND
                       sdinvo = @invoiceID AND
                       sdtype = 'S'

                UPDATE crsald
                SET    sddsct = sddsct
                                + floor(((sdsprc*sdtqty-sddsct)/@lnXCrsaldSum) * @lnXCouponSum)
                WHERE  sdshop = @shopID AND
                       sdtxdt = @TransDate AND
                       sdcrid = @crid AND
                       sdinvo = @invoiceID AND
                       sdtype = 'S'

                IF @lnXShareSum <> @lnXCouponSum
                  BEGIN
                      SELECT @lnXCrsaldMaxAmnt = max(sdsprc * sdtqty - sddsct)
                      FROM   crsald
                      WHERE  sdshop = @shopID AND
                             sdtxdt = @TransDate AND
                             sdcrid = @crid AND
                             sdinvo = @invoiceID AND
                             sdtype = 'S'

                      SELECT @lnXCrsaldMaxAmntSeqn = sdseqn
                      FROM   crsald
                      WHERE  sdshop = @shopID AND
                             sdtxdt = @TransDate AND
                             sdcrid = @crid AND
                             sdinvo = @invoiceID AND
                             sdtype = 'S' AND
                             ( sdsprc * sdtqty - sddsct ) = @lnXCrsaldMaxAmnt

                      UPDATE crsald
                      SET    sddsct = sddsct + ( @lnXCouponSum - @lnXShareSum )
                      WHERE  sdshop = @shopID AND
                             sdtxdt = @TransDate AND
                             sdcrid = @crid AND
                             sdinvo = @invoiceID AND
                             sdtype = 'S' AND
                             sdseqn = @lnXCrsaldMaxAmntSeqn
                  END

                IF @lnVatr > 0
                  UPDATE crsald
                  SET    sdvata = ( sdsprc * sdtqty - sddsct ) * @lnVatr / ( 1 + @lnVatr )
                  WHERE  sdshop = @shopID AND
                         sdtxdt = @TransDate AND
                         sdcrid = @crid AND
                         sdinvo = @invoiceID
            /*      
                           delete from crctdr      
                              from mftdrt      
                              where ctshop=@pcShop and cttxdt=@pdTxdt and ctcrid=@pcCrid and ctinvo=@pnInvo and    
                                    ctmakt=@lcMakt and ctmakt=tdmakt and cttdrt=tdtdrt and tdtype & 1 = 1   
            */
                --????????  

            END

          IF @lnVatr < 0
            UPDATE crsald
            SET    sdvata = ( sdsprc * sdtqty - sddsct ) * ( 0 - @lnVatr ),
                   sdsprc = sdsprc * ( 1 - @lnVatr ),
                   sddsct = sddsct * ( 1 - @lnVatr )
            WHERE  sdshop = @shopID AND
                   sdtxdt = @TransDate AND
                   sdcrid = @crid AND
                   sdinvo = @invoiceID

          SELECT @lnTqty = sum(CASE
                                 WHEN sdtype = 'S' THEN sdtqty
                                 ELSE -sdtqty
                               END),@lnTamt = sum(CASE
                                                    WHEN sdtype = 'S' THEN sdsprc * sdtqty - sddsct
                                                    ELSE -sdsprc * sdtqty + sddsct
                                                  END),@lnRqty = sum(CASE
                                                                       WHEN sdtype = 'R' THEN sdtqty
                                                                       ELSE 0
                                                                     END),@lnRamt = sum(CASE
                                                                                          WHEN sdtype = 'R' THEN sdsprc * sdtqty - sddsct
                                                                                          ELSE 0
                                                                                        END),@lnDqty = sum(CASE sddsct
                                                                                                             WHEN 0 THEN 0
                                                                                                             ELSE
                                                                                                               CASE sdtype
                                                                                                                 WHEN 'S' THEN sdtqty
                                                                                                                 ELSE -sdtqty
                                                                                                               END
                                                                                                           END),@lnDamt = sum(CASE sddsct
                                                                                                                                WHEN 0 THEN 0
                                                                                                                                ELSE
                                                                                                                                  CASE sdtype
                                                                                                                                    WHEN 'S' THEN sddsct
                                                                                                                                    ELSE -sddsct
                                                                                                                                  END
                                                                                                                              END)
          FROM   crsald
          WHERE  sdshop = @shopID AND
                 sdtxdt = @TransDate AND
                 sdcrid = @crid AND
                 sdinvo = @invoiceID

          SELECT @lnDinv = 0,@lnRinv = 0

          IF @lnRqty > 0
            SELECT @lnRInv = 1
          ELSE
            SELECT @lnRinv = 0

          IF @lnDamt <> 0 AND
             @lnTamt <> 0
            SELECT @lnDinv = 1
          ELSE
            SELECT @lnDinv = 0,@lnDamt = 0,@lnDqty = 0

          INSERT @tctdr
                 (tttdrt,ttcurr,ttlamt,ttoamt)
          SELECT cttdrt,ctcurr,ctlamt=sum(ctlamt),ctoamt=sum(ctoamt)
          FROM   crctdr
          WHERE  cttxdt = @TransDate AND
                 ctshop = @shopID AND
                 ctcrid = @crid AND
                 ctinvo = @invoiceID
          GROUP  BY cttdrt,ctcurr

          IF NOT EXISTS( SELECT *
                         FROM   syproc
                         WHERE  prshop = @shopID AND
                                prtype = 'CRSAL' AND
                                prtxnt = @lcpara )
            INSERT syproc
                   (prshop,prtype,prtxnt)
            VALUES (@shopID,'CRSAL',@lcpara)

          UPDATE crcdwh
          SET    dhdinv = dhdinv + @lnDinv,
                 dhdqty = dhdqty + @lnDqty,
                 dhdamt = dhdamt + @lnDamt,
                 dhrinv = dhrinv + @lnRinv,
                 dhrqty = dhrqty + @lnRqty,
                 dhramt = dhramt + @lnramt
          WHERE  dhtxdt = @TransDate AND
                 dhshop = @shopID AND
                 dhcrid = @crid AND
                 dhshft = @lnShft

          UPDATE crcdwd
          SET    ddlamt = ddlamt + ttlamt,
                 ddoamt = ddoamt + ttoamt
          FROM   @tctdr
          WHERE  ddtxdt = @TransDate AND
                 ddshop = @shopID AND
                 ddcrid = @crid AND
                 ddshft = @lnShft AND
                 ddtdrt = tttdrt AND
                 ddcurr = ttcurr

          INSERT crcdwd
                 (ddtxdt,ddshop,ddcrid,ddshft,ddmakt,ddtdrt,ddcurr,ddlamt,ddoamt,ddaamt)
          SELECT @TransDate,@shopID,@crid,@lnShft,@lcMakt,tttdrt,ttcurr,ttlamt,ttoamt,0
          FROM   @tctdr
          WHERE  NOT EXISTS( SELECT *
                             FROM   crcdwd
                             WHERE  ddtxdt = @TransDate AND
                                    ddshop = @shopID AND
                                    ddcrid = @crid AND
                                    ddshft = @lnShft AND
                                    ddtdrt = tttdrt AND
                                    ddcurr = ttcurr )

          IF @discountAmount <> 0
            BEGIN
                DECLARE @lcDiscAmt nvarchar(200)

                SET @lcDiscAmt = CONVERT(nvarchar(200), @discountAmount)
                --记录发票的折扣金额
                EXEC MPos_Crm01_InsertProperty @TransDate,@shopID,@crid,@invoiceID,'INVDISCAMT',@lcDiscAmt
            END

       --    IF @redeemAmount <> 0
       --      BEGIN
       --          DECLARE @lcRedeemAmt nvarchar(200)

       --          SET @lcRedeemAmt = CONVERT(nvarchar(200), @redeemAmount)
       --          --记录积分兑换金额
       --          EXEC MPos_Crm01_InsertProperty @TransDate,@shopID,@crid,@invoiceID,'REDEEMAMT',@lcRedeemAmt
       --      END

       --    IF @redeemQuantity <> 0
       --      BEGIN
       --          DECLARE @lcRedeemQty nvarchar(200)

       --          --记录积分兑换数量
       --          SET @lcRedeemQty = CONVERT(nvarchar(200), @redeemQuantity)
       --          EXEC MPos_Crm01_InsertProperty @TransDate,@shopID,@crid,@invoiceID,'REDEEMQTY',@lcRedeemQty
       --      END

       --    IF len(@promotionID) > 0
       --      BEGIN
       --          EXEC MPos_Crm01_InsertProperty @TransDate,@shopID,@crid,@invoiceID,'NOSTORHIST',@promotionID
       --      END

          UPDATE crsalh
          SET    shtqty = @lnTqty,
                 shamnt = @lnTamt,
                 shupdt = 'Y'
          WHERE  shtxdt = @TransDate AND
                 shshop = @shopID AND
                 shcrid = @crid AND
                 shinvo = @invoiceID

       --    EXEC MPos_crm01_jimai @shopID,@TransDate,@crid,@invoiceID

          SELECT @lcCard = rtrim(shcust)
          FROM   crsalh
          WHERE  shtxdt = @TransDate AND
                 shshop = @shopID AND
                 shcrid = @crid AND
                 shinvo = @invoiceID

       --暂时不实现积分兑换功能 MIKE 2025-12-16
       --    IF len(@lcCard) > 0
       --      BEGIN
       --          SELECT @lcKind = cdregn
       --          FROM   cccard
       --          WHERE  cdcard = @lcCard

       --          SELECT @lcIden = max(cmiden)
       --          FROM   crmeed
       --          WHERE  cmshop = @pcShop AND
       --                 cmfdat <= @pdTxdt AND
       --                 cmtdat >= @pdTxdt AND
       --                 charindex(@lcKind, cmkind) > 0 AND
       --                 cmcanx <> 'Y'

       --          IF NOT @lcIden IS NULL
       --            BEGIN
       --                SELECT @lcPomo = cmpomo
       --                FROM   crmeed
       --                WHERE  cmshop = @pcShop AND
       --                       cmiden = @lcIden

       --                IF len(@lcPomo) = 0
       --                  SET @lcMeed = 'Y'
       --                ELSE IF EXISTS( SELECT *
       --                           FROM   crsald
       --                           WHERE  sdtxdt = @pdTxdt AND
       --                                  sdshop = @pcShop AND
       --                                  sdcrid = @pcCrid AND
       --                                  sdinvo = @pnInvo AND
       --                                  sdprom = @lcPomo )
       --                  SET @lcMeed = 'Y'

       --                IF @lcMeed = 'Y'
       --                  BEGIN
       --                      UPDATE crmeed
       --                      SET    cmfixc = CASE cmfixc
       --                                        WHEN 0 THEN floor(cmodds * rand() + 1)
       --                                        ELSE cmfixc
       --                                      END,
       --                             cmcurc = cmcurc + 1
       --                      WHERE  cmshop = @pcShop AND
       --                             cmiden = @lcIden

       --                      SELECT @lmEdcr = cmedcr,@lmEdpt = cmedpt,@lnOdds = cmodds,@lnFixc = cmfixc,@lnCurc = cmcurc
       --                      FROM   crmeed
       --                      WHERE  cmshop = @pcShop AND
       --                             cmiden = @lcIden

       --                      IF @lnFixc = @lnCurc
       --                        BEGIN
       --                            IF @lmEdcr <> 0
       --                              BEGIN
       --                                  DECLARE @lcMeedCredit nvarchar(200)

       --                                  SET @lcMeedCredit = CONVERT(nvarchar(200), @lmEdcr)

       --                                  EXEC MPos_Crm01_InsertProperty @pdTxdt,@pcShop,@pcCrid,@pnInvo,'MEEDCREDIT',@lcMeedCredit
       --                              END

       --                            IF @lmEdpt <> 0
       --                              BEGIN
       --                                  DECLARE @lcMeedPoint nvarchar(200)

       --                                  SET @lcMeedPoint = CONVERT(nvarchar(200), @lmEdpt)

       --                                  EXEC MPos_Crm01_InsertProperty @pdTxdt,@pcShop,@pcCrid,@pnInvo,'MEEDPOINT',@lcMeedPoint
       --                              END
       --                        END

       --                      IF @lnOdds <= @lnCurc
       --                        UPDATE crmeed
       --                        SET    cmfixc = floor(cmodds * rand() + 1),
       --                               cmcurc = 0
       --                        WHERE  cmshop = @pcShop AND
       --                               cmiden = @lcIden
       --                  END
       --            END
       --      --exec taskp_syproc_Sale    
       --      END

          COMMIT TRANSACTION

       --    IF EXISTS( SELECT *
       --               FROM   crctdr
       --               WHERE  cttxdt = @pdTxdt AND
       --                      ctshop = @pcShop AND
       --                      ctcrid = @pcCrid AND
       --                      ctinvo = @pnInvo AND
       --                      cttdrt = 'C' AND
       --                      ctlamt > 0 )
       --      BEGIN
       --          --select @pcShop = 'CCL69'
       --          IF NOT EXISTS( SELECT *
       --                         FROM   sydraw
       --                         WHERE  sdshop = @pcShop )
       --            INSERT sydraw
       --                   (sdshop,sdstat)
       --            VALUES(@pcShop,'')
       --          ELSE
       --            UPDATE sydraw
       --            SET    sdstat = ''
       --            WHERE  sdshop = @pcShop
       --      END

          SELECT @lnError = 0
      END
    ELSE
      SELECT @lnError = 1

    IF @lnError = 1
      BEGIN
          DELETE FROM crsald
          WHERE  sdshop = @shopID AND
                 sdtxdt = @TransDate AND
                 sdcrid = @crid AND
                 sdinvo = @invoiceID

          DELETE FROM crctdr
          WHERE  ctshop = @shopID AND
                 cttxdt = @TransDate AND
                 ctcrid = @crid AND
                 ctinvo = @invoiceID

          DELETE FROM crprop
          WHERE  cpshop = @shopID AND
                 cptxdt = @TransDate AND
                 cpcrid = @crid AND
                 cpinvo = @invoiceID

          DELETE FROM crsalh
          WHERE  shshop = @shopID AND
                 shtxdt = @TransDate AND
                 shcrid = @crid AND
                 shinvo = @invoiceID
      END

    SELECT @lnError

go 
