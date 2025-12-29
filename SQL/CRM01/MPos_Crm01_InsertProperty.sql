DROP PROCEDURE MPos_Crm01_InsertProperty
GO
CREATE PROCEDURE MPos_Crm01_InsertProperty
   @pdTxdt  smalldatetime,
   @pcShop  char(5),
   @pcCrid  char(3),
   @pnInvo  int,
   @pcProp  varchar(10),
   @pcValue nvarchar(MAX)
AS
   IF NOT EXISTS( SELECT *
                  FROM   crprop a
                  WHERE  a.cptxdt = @pdTxdt AND
                         a.cpshop = @pcShop AND
                         a.cpcrid = @pcCrid AND
                         a.cpinvo = @pnInvo AND
                         a.cpprop = @pcprop )
      BEGIN
         INSERT dbo.crprop
                (cptxdt,cpshop,cpcrid,cpinvo,cpprop,cpvalu)
         VALUES ( @pdTxdt,-- cptxdt - smalldatetime
                  @pcShop,-- cpshop - char(5)
                  @pcCrid,-- cpcrid - char(3)
                  @pnInvo,-- cpinvo - int
                  @pcProp,-- cpprop - varchar(10)
                  @pcValue -- cpvalu - nvarchar(2000)
         )
      END
   ELSE
      BEGIN
         UPDATE a
         SET    a.cpvalu = @pcValue
         FROM   dbo.crprop a
         WHERE  a.cptxdt = @pdTxdt AND
                a.cpshop = @pcShop AND
                a.cpinvo = @pnInvo AND
                a.cpprop = @pcProp AND
                a.cpcrid = @pcCrid
      END 
