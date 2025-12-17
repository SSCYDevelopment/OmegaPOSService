DROP PROCEDURE if EXISTS MPos_Public_CheckStyl
go
CREATE PROCEDURE MPos_Public_CheckStyl
  @pcSkun varchar(21),
  @pcMakt char(2) = '',
  @pcShop char(5) = ''
AS
SET NOCOUNT ON
    DECLARE @tskun TABLE
    (
       skskun char( 21 ),skstyl char( 15 ),skskid char( 15 ),skstid char( 11 ),skcolr char( 3 ),sksize char( 3 ),skedes nvarchar( 100 ),skldes nvarchar( 100 ),skbran char( 3 ),skcate char( 2 ),skline char( 3 ),skseas char( 1 ),skcore char( 1 ),skoprc money,sknprc money,sktype char( 1 ) DEFAULT 'N',skyear smalldatetime,skptyp char( 2 ),skdmak decimal( 5, 2 ),skcomi decimal( 5, 2 ),skbbit int
    )
    DECLARE @lcSkun varchar(15)
    DECLARE @lcTxdt smalldatetime
    DECLARE @lcTxdtStyl smalldatetime
    DECLARE @lcTxdtColr smalldatetime
    DECLARE @lcTxdtSize smalldatetime
    DECLARE @ldToday smalldatetime
    DECLARE @lcTskun varchar(15)
    DECLARE @lcMarket char(2)
    DECLARE @lnSkuLen smallint
    DECLARE @lnMinbit int
    DECLARE @lcMerge char(1)

    SET @lnMinbit = 0
    SET @lnSkuLen = len(rtrim(@pcSkun))

    SELECT @lcMerge = 'Y'

    IF EXISTS( SELECT *
               FROM   syconf,syshop
               WHERE  cnshop = syshop AND
                      cnprop = 'NOMERGE' )
      SELECT @lcMerge = 'N'

    /*
     IF @lnSkuLen IN （） 12
       BEGIN
    
    
           SELECT @lcTskun = skskun
           FROM   mfskun(nolock),mfstyl(nolock)
           WHERE  skstyl = smstyl AND
                  skcolr = substring(@pcSkun, 9, 2) AND
                  sksize = substring(@pcSkun, 11, 2) AND
                  smcode = substring(@pcSkun, 1, 8) AND
                  smcanx <> 'Y'
    
           IF rtrim(@pcMakt) <> '' AND
              @lcMerge = 'Y'
             SELECT @lcSkun = mknsku
             FROM   mfskmp(nolock)
             WHERE  @lcTskun = mkskun AND
                    mkmakt = @pcMakt
    
           IF @lcSkun IS NULL
             SELECT @lcSkun = @lcTskun
    
           INSERT @tskun
                  (skskun,skstyl,skskid,skstid,skcolr,sksize,skedes,skldes,skbran,skcate,skline,skseas,skcore,skoprc,sknprc,skyear)
           SELECT substring(@lcSkun, 1, 8)
                  + substring(@lcskun, 12, 4),smcode,@lcSkun,smstyl,substring(@lcSkun, 12, 2),substring(@lcskun, 14, 2),smedes,smldes,smbran,smcate,smline,smseas,smcore,smsprc,NULL,smyear
           FROM   mfstyl(nolock)
           WHERE  smstyl = substring(@lcSkun, 1, 11)
    
       END
     ELSE
       BEGIN
           IF @lnSkuLen = 10
             INSERT @tskun
                    (skskun,skstyl,skskid,skstid,skcolr,sksize,skedes,skldes,skbran,skcate,skline,skseas,skcore,skoprc,sknprc,skyear)
             SELECT DISTINCT '',smcode,smstyl + skcolr,smstyl,skcolr,'',smedes,smldes,smbran,smcate,smline,smseas,smcore,smsprc,NULL,smyear
             FROM   mfstyl(nolock),mfskun(nolock)
             WHERE  smcode = substring(@pcSkun, 1, 8) AND
                    smcanx <> 'Y' AND
                    smstyl = skstyl AND
                    skcolr = substring(@pcSkun, 9, 2)
           ELSE IF @lnSkuLen = 8
             INSERT @tskun
                    (skskun,skstyl,skskid,skstid,skcolr,sksize,skedes,skldes,skbran,skcate,skline,skseas,skcore,skoprc,sknprc,skyear)
             SELECT '',smcode,smstyl,smstyl,'','',smedes,smldes,smbran,smcate,smline,smseas,smcore,smsprc,NULL,smyear
             FROM   mfstyl(nolock)
             WHERE  smcode = @pcSkun AND
                    smcanx <> 'Y'
           ELSE IF @lnSkuLen = 6
             BEGIN
                 INSERT @tskun
                        (skskun,skstyl,skskid,skstid,skcolr,sksize,skedes,skldes,skbran,skcate,skline,skseas,skcore,skoprc,sknprc,skyear)
                 SELECT '',smcode,smstyl,smstyl,'','',smedes,smldes,smbran,smcate,smline,smseas,smcore,smsprc,NULL,smyear
                 FROM   mfstyl(nolock)
                 WHERE  smcode = @pcMakt + @pcSkun AND
                        smcanx <> 'Y'
    
                 IF NOT EXISTS( SELECT *
                                FROM   @tskun )
                   INSERT @tskun
                          (skskun,skstyl,skskid,skstid,skcolr,sksize,skedes,skldes,skbran,skcate,skline,skseas,skcore,skoprc,sknprc,skyear)
                   SELECT '',smcode,smstyl,smstyl,'','',smedes,smldes,smbran,smcate,smline,smseas,smcore,smsprc,NULL,smyear
                   FROM   mfstyl(nolock),mfbrnd(nolock)
                   WHERE  smcode = brstyl + @pcSkun AND
                          smcanx <> 'Y' AND
                          brstyl <= '05'
             END
       END
     */

    DECLARE @colorID varchar(3)
    DECLARE @sizeID varchar(3)
    DECLARE @styleID varchar(15)

    SELECT @styleID = a.skstyl,@colorID = a.skcolr,@sizeID = a.sksize
    FROM   dbo.mfskun a
    WHERE  a.skskun = @pcSkun

    INSERT @tskun
           (skskun,
            skstyl,
            skskid,
            skstid,
            skcolr,
            sksize,
            skedes,
            skldes,
            skbran,
            skcate,
            skline,
            skseas,
            skcore,
            skoprc,
            sknprc,
            skyear)
    SELECT @pcSkun,smcode,@pcSkun,smstyl,@colorID,@sizeID,smedes,smldes,smbran,smcate,smline,smseas,smcore,smsprc,NULL,smyear
    FROM   mfstyl(nolock)
    WHERE  smstyl = @styleID

    /*
    IF @pcMakt = ''  OR
       @pcMakt = 'ME'
      DELETE @tskun
      WHERE  NOT EXISTS( SELECT *
                         FROM   symakt,mfstmk
                         WHERE  symakt = skmakt AND
                                mfstmk.skstyl = skstid )
    ELSE
      DELETE @tskun
      WHERE  NOT EXISTS( SELECT *
                         FROM   mfstmk
                         WHERE  skmakt = @pcMakt AND
                                mfstmk.skstyl = skstid )
    */

    UPDATE @tskun
    SET    skbbit = brbitn
    FROM   mfbrnd
    WHERE  brbran = skbran

    IF ( SELECT count(*)
         FROM   @tskun ) > 1
      BEGIN
          SELECT @lnMinbit = min(skbbit)
          FROM   @tskun

          DELETE FROM @tskun
          WHERE  skbbit > @lnMinbit
      END

    IF rtrim(@pcShop) <> ''
      BEGIN
          SELECT @ldToday = CONVERT(char(10), sdtxdt, 120) + ' '
                            + RIGHT(CONVERT(char(3), 100+datepart(hh, getdate())), 2)
                            + ':'
                            + RIGHT(CONVERT(char(3), 100+datepart(mi, getdate())), 2)
                            + ':00'
          FROM   sydate(nolock)

          SELECT @lcMarket = shmakt
          FROM   mfshop
          WHERE  shshop = @pcShop

      /*
      --      IF @lcMarket = 'KR'
      --        BEGIN
      --            SELECT @lcTxdt = max(pctxdt)
      --            FROM   mfprch(nolock),@tskun
      --            WHERE  pcshop = @pcShop AND
      --                   pcstyl = skstid AND
      --                   rtrim(pccolr) = '' AND
      --                   rtrim(pcsize) = '' AND
      --                   pctxdt <= @ldToday
      
      --            IF @lcTxdt IS NOT NULL
      --              UPDATE @tskun
      --              SET    sknprc = pcsprc,
      --                     sktype = pctype,
      --                     skptyp = pcptyp,
      --                     skdmak = pcdmak,
      --                     skcomi = pccomi
      --              FROM   mfprch(nolock)
      --              WHERE  pcshop = @pcShop AND
      --                     pcstyl = skstid AND
      --                     rtrim(pccolr) = '' AND
      --                     rtrim(pcsize) = '' AND
      --                     pctxdt = @lcTxdt
      
      --            SELECT @lcTxdt = NULL
      
      --            SELECT @lcTxdt = max(pctxdt)
      --            FROM   mfprch(nolock),@tskun
      --            WHERE  pcshop = @pcShop AND
      --                   pcstyl = skstid AND
      --                   rtrim(pccolr) = skcolr AND
      --                   rtrim(pcsize) = '' AND
      --                   pctxdt <= @ldToday
      
      --            IF @lcTxdt IS NOT NULL
      --              UPDATE @tskun
      --              SET    sknprc = pcsprc,
      --                     sktype = pctype,
      --                     skptyp = pcptyp,
      --                     skdmak = pcdmak,
      --                     skcomi = pccomi
      --              FROM   mfprch(nolock)
      --              WHERE  pcshop = @pcShop AND
      --                     pcstyl = skstid AND
      --                     rtrim(pccolr) = skcolr AND
      --                     rtrim(pcsize) = '' AND
      --                     pctxdt = @lcTxdt
      
      --            SELECT @lcTxdt = NULL
      
      --            SELECT @lcTxdt = max(pctxdt)
      --            FROM   mfprch(nolock),@tskun
      --            WHERE  pcshop = @pcShop AND
      --                   pcstyl = skstid AND
      --                   rtrim(pccolr) = skcolr AND
      --                   rtrim(pcsize) = sksize AND
      --                   pctxdt <= @ldToday
      
      --            IF @lcTxdt IS NOT NULL
      --              UPDATE @tskun
      --              SET    sknprc = pcsprc,
      --                     sktype = pctype,
      --                     skptyp = pcptyp,
      --                     skdmak = pcdmak,
      --                     skcomi = pccomi
      --              FROM   mfprch(nolock)
      --              WHERE  pcshop = @pcShop AND
      --                     pcstyl = skstid AND
      --                     rtrim(pccolr) = skcolr AND
      --                     rtrim(pcsize) = sksize AND
      --                     pctxdt = @lcTxdt
      --        END
      --      ELSE
      */
          --获取价钱
          BEGIN


              SELECT @lcTxdtStyl = max(pctxdt)
              FROM   mfprch(nolock),@tskun
              WHERE  pcshop = @pcShop AND
                     pcstyl = skstid AND
                     rtrim(pccolr) = '' AND
                     rtrim(pcsize) = '' AND
                     pctxdt <= @ldToday

              IF @lcTxdtStyl IS NOT NULL
                UPDATE @tskun
                SET    sknprc = pcsprc,
                       sktype = pctype,
                       skptyp = pcptyp,
                       skdmak = pcdmak,
                       skcomi = pccomi
                FROM   mfprch(nolock)
                WHERE  pcshop = @pcShop AND
                       pcstyl = skstid AND
                       rtrim(pccolr) = '' AND
                       rtrim(pcsize) = '' AND
                       pctxdt = @lcTxdtStyl

              SELECT @lcTxdtColr = max(pctxdt)
              FROM   mfprch(nolock),@tskun
              WHERE  pcshop = @pcShop AND
                     pcstyl = skstid AND
                     rtrim(pccolr) = skcolr AND
                     rtrim(pcsize) = '' AND
                     pctxdt <= @ldToday

              IF @lcTxdtColr IS NOT NULL AND
                 ( @lcTxdtStyl IS NULL  OR
                   @lcTxdtStyl IS NOT NULL AND
                   @lcTxdtColr >= @lcTxdtStyl )
                UPDATE @tskun
                SET    sknprc = pcsprc,
                       sktype = pctype,
                       skptyp = pcptyp,
                       skdmak = pcdmak,
                       skcomi = pccomi
                FROM   mfprch(nolock)
                WHERE  pcshop = @pcShop AND
                       pcstyl = skstid AND
                       rtrim(pccolr) = skcolr AND
                       rtrim(pcsize) = '' AND
                       pctxdt = @lcTxdtColr

              SELECT @lcTxdtSize = max(pctxdt)
              FROM   mfprch(nolock),@tskun
              WHERE  pcshop = @pcShop AND
                     pcstyl = skstid AND
                     rtrim(pccolr) = skcolr AND
                     rtrim(pcsize) = sksize AND
                     pctxdt <= @ldToday

              IF @lcTxdtSize IS NOT NULL AND
                 ( @lcTxdtStyl IS NULL AND
                   @lcTxdtColr IS NULL  OR
                   @lcTxdtStyl IS NOT NULL AND
                   @lcTxdtColr IS NULL AND
                   @lcTxdtSize >= @lcTxdtStyl  OR
                   @lcTxdtStyl IS NULL AND
                   @lcTxdtColr IS NOT NULL AND
                   @lcTxdtSize >= @lcTxdtColr  OR
                   @lcTxdtStyl IS NOT NULL AND
                   @lcTxdtColr IS NOT NULL AND
                   @lcTxdtSize >= @lcTxdtStyl AND
                   @lcTxdtSize >= @lcTxdtColr )
                UPDATE @tskun
                SET    sknprc = pcsprc,
                       sktype = pctype,
                       skptyp = pcptyp,
                       skdmak = pcdmak,
                       skcomi = pccomi
                FROM   mfprch(nolock)
                WHERE  pcshop = @pcShop AND
                       pcstyl = skstid AND
                       rtrim(pccolr) = skcolr AND
                       rtrim(pcsize) = sksize AND
                       pctxdt = @lcTxdtSize
          END

          UPDATE @tskun
          SET    skoprc = pcsprc
          FROM   mfprch(nolock)
          WHERE  pcshop = @pcShop AND
                 pcstyl = skstid AND
                 rtrim(pccolr) = '' AND
                 rtrim(pcsize) = '' AND
                 pctxdt = '1980-1-1'
      END

    UPDATE @tskun
    SET    skedes = replace(skedes, '"', ''),
           skldes = replace(skldes, '"', '')

    UPDATE @tskun
    SET    skptyp = 'A'
    WHERE  skptyp = '01'

    UPDATE @tskun
    SET    skptyp = 'N'
    WHERE  skptyp IN ( '00', '02', '21' )

    IF EXISTS( SELECT *
               FROM   @tskun
               WHERE  sknprc IS NULL )
      UPDATE a
      SET    sknprc = sksprc
      FROM   @tskun AS a,mfstmk AS b
      WHERE  b.skmakt = @lcMarket AND
             b.skstyl = skstid

    SELECT a.skskun SkuBarcde,
	a.skstyl StyleID,
	a.skcolr ColorID,
	a.sksize SizeID,
	a.skedes LocalDescription,
	a.skldes EnglishDescription,
	a.skbran Brand,
	a.skcate Category,
	a.skline Line,
	a.skoprc UnitPrice,
	a.sknprc Price
    FROM   @tskun a

go 