CREATE PROCEDURE dbo.MPos_Crm01_SaveGBSupplyInfo_Market
   @storeNo    AS varchar( 8 ),
   @storeName  AS varchar( 64 ),
   @marketNo   AS varchar( 8 ),
   @marketName AS varchar( 64 )
AS
   BEGIN
      IF EXISTS ( SELECT *
                  FROM   gbmrkt(NOLOCK)
                  WHERE  strnum = @storeNo AND
                         mktnum = @marketNo )
         BEGIN
            UPDATE a
            SET    a.strnam = @storeName,
                   a.mktnam = @marketName
            FROM   gbmrkt
            WHERE  strnum = @storeNo AND
                   mktnum = @marketNo
         END
      ELSE
         BEGIN
            INSERT dbo.gbmrkt
                   (strnum,strnam,mktnum,mktnam)
            VALUES ( @storeNo,@storeName,@marketNo,@marketName )
         END
   END 
 
