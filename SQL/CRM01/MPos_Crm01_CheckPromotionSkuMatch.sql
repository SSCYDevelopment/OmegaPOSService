DROP FUNCTION IF EXISTS MPOS_Crm01_CheckPromotionSkuMatch
go
CREATE FUNCTION MPOS_Crm01_CheckPromotionSkuMatch  
(  
   @scopeID char(12),  
   @skuID   char(15),  
   @styp    char(1) = ''  
)  
returns int  
AS  
   BEGIN  
      DECLARE @result int  
  
      SELECT @result = 0  
  
      IF EXISTS( SELECT *  
                 FROM   crscop  
                 WHERE  scscop = @scopeID AND  
                        scstyl IN ( 'ANY', '' ) AND  
                        ( scstyp = ''  OR  
                          scstyp = @styp ) )  
         SET @result = 1  
  
      ELSE IF EXISTS( SELECT *  
                 FROM   crscop  
                 WHERE  scscop = @scopeID AND  
                        scstyl NOT IN ( 'ANY', '' ) AND  
                        @skuID LIKE rtrim(scstyl) + '%' AND  
                        ( scstyp = ''  OR  
                          scstyp = @styp ) )  
         SELECT @result = 1  
  
      RETURN( @result )  
   END  
GO