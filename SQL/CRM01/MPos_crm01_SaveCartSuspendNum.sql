CREATE PROC MPos_crm01_SaveCartSuspendNum
   @TransDate  smalldatetime,
   @Shop       char(5),
   @Crid       char(3),
   @CartID     uniqueidentifier,
   @SuspendNum varchar(50)
AS
   IF EXISTS( SELECT *
              FROM   crcarh
              WHERE  transdate = @TransDate AND
                     shop = @Shop AND
                     crid = @Crid AND
                     cartid = @CartID )
      UPDATE crcarh
      SET    SuspendNum = @SuspendNum
      WHERE  transdate = @TransDate AND
             shop = @Shop AND
             crid = @Crid AND
             cartid = @CartID
   ELSE
      INSERT crcarh
             (TransDate,shop,crid,cartid,SuspendNum)
      SELECT @TransDate,@Shop,@Crid,@CartID,@SuspendNum 
 
