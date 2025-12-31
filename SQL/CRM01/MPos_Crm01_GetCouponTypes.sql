CREATE PROCEDURE MPos_Crm01_GetCouponTypes
   @lcMakt char(2)
AS
   SET NOCOUNT ON

   SELECT a.tdtdrt DiscountID,a.tdldes DiscountTypeDesc,a.tdtype DiscountType
   FROM   dbo.mftdrt(NOLOCK) a
   WHERE  a.tdmakt = @lcMakt 
 
