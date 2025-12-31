CREATE PROCEDURE dbo.MPos_Crm01_SaveGBSupplyInfo_Cashier
   @postNo      AS varchar( 8 ),
   @cashierNo   AS varchar( 16 ),
   @cashierName AS varchar( 64 )
AS
   BEGIN
      IF EXISTS ( SELECT *
                  FROM   gbcshr(NOLOCK)
                  WHERE  pstnum = @postNo AND
                         cshnum = @cashierNo )
         BEGIN
            UPDATE a
            SET    a.cshnam = @cashierName
            FROM   gbcshr
            WHERE  pstnum = @postNo AND
                   cshnum = @cashierNo
         END
      ELSE
         BEGIN
            INSERT dbo.gbcshr
                   (pstnum,cshnum,cshnam)
            VALUES ( @postNo,@cashierNo,@cashierName )
         END
   END 
 
