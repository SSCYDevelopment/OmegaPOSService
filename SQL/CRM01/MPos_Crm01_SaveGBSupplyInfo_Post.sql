CREATE PROCEDURE dbo.MPos_Crm01_SaveGBSupplyInfo_Post
   @marketNo     AS varchar( 8 ),
   @postNo       AS varchar( 8 ),
   @postName     AS varchar( 64 ),
   @postType     AS varchar( 4 ),
   @czm          AS varchar( 8 ),
   @categoryNo   AS varchar( 8 ),
   @categoryName AS varchar( 64 ),
   @posName      AS varchar( 64 ),
   @taxRate      AS int
AS
   BEGIN
      IF EXISTS ( SELECT *
                  FROM   gbpost(NOLOCK)
                  WHERE  mktnum = @marketNo AND
                         pstnum = @postNo )
         BEGIN
            UPDATE a
            SET    a.pstnam = @postName,
                   a.psttyp = @postType,
                   a.czmcod = @czm,
                   a.catnum = @categoryNo,
                   a.catnam = @categoryName,
                   a.posnam = @posName,
                   a.txrate = @taxRate
            FROM   gbpost
            WHERE  mktnum = @marketNo AND
                   pstnum = @postNo
         END
      ELSE
         BEGIN
            INSERT dbo.gbpost
                   (mktnum,pstnum,pstnam,psttyp,czmcod,catnum,catnam,posnam,txrate)
            VALUES ( @marketNo,@postNo,@postName,@postType,@czm,@categoryNo,@categoryName,@posName,@taxRate )
         END
   END 
 
