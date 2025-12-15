DROP PROCEDURE MPos_Sync_SavePrice
GO
CREATE PROCEDURE MPos_Sync_SavePrice
   @shopID    varchar(10),
   @styleID   varchar(15),
   @price     smallmoney,
   @fromDate  smalldatetime,
   @toDate    smalldatetime,
   @reason    nvarchar(255),
   @priceType int
AS
   SET NOCOUNT ON;

   DECLARE @rtn TABLE
   (
       returnID      int,
       returnMessage varchar( 256 )
   )

   IF EXISTS ( SELECT *
               FROM   mfprch a
               WHERE  a.pcshop = @shopID AND
                      a.pcshop = @shopID AND
                      a.pctxdt = @fromDate AND
                      a.pcdate = @toDate AND
                      a.pcstyl = @styleID )
      BEGIN
         UPDATE a
         SET    a.pcsprc = @price,
                a.pcreas = @reason,
                a.pctype = @priceType
         FROM   mfprch(NOLOCK) a
         WHERE  a.pcshop = @shopID AND
                a.pctxdt = @fromDate AND
                a.pcdate = @toDate AND
                a.pcstyl = @styleID

         INSERT @rtn
                (returnID,returnMessage)
         VALUES ( 1,-- returnID - int
                  '更新成功' -- returnMessage - varchar(256)
         );
      END
   ELSE
      BEGIN
         INSERT dbo.mfprch
                (pcshop,pcstyl,pcsprc,pctxdt,pcdate,pcreas,pctype)
         VALUES ( @shopID,-- pcshop - char(10)
                  @styleID,-- pcstyl - char(15)
                  @price,-- pcsprc - money
                  @fromDate,-- pctxdt - smalldatetime
                  @toDate,-- pcdate - smalldatetime
                  @reason,-- pcreas - nchar(100)
                  @priceType -- pctype - int
         )

         INSERT @rtn
                (returnID,returnMessage)
         VALUES ( 1,-- returnID - int
                  '新增成功' -- returnMessage - varchar(256)
         );
      END

   SELECT *
   FROM   @rtn 
 
