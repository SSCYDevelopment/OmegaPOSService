drop procedure if EXISTS MPos_Crm01_RemoveDiscountTicket
GO
CREATE PROCEDURE MPos_Crm01_RemoveDiscountTicket
  @TransDate    smalldatetime, --销售日期
  @Shop         char(5), --销售门店
  @Crid         char(3), --收银机号码
  @cartID       uniqueidentifier, --购物车ID
  @DiscountTicketID varchar(25) --折扣券ID
  AS
    DELETE FROM crdtik
    WHERE  ddtxdt = @TransDate AND
           ddshop = @Shop AND
           ddcrid = @Crid AND
           ddcart = @cartID AND
           ddtick = @DiscountTicketID
GO