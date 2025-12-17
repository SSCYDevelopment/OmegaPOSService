drop PROCEDURE IF EXISTS MPos_Crm01_SaveDiscountTicket
GO
CREATE PROCEDURE MPos_Crm01_SaveDiscountTicket
  @TransDate    smalldatetime, --销售日期
  @Shop         char(5), --销售门店
  @Crid         char(3), --收银机号码
  @cartID       uniqueidentifier, --购物车ID
  @DiscountTicketID varchar(25), --折扣券ID
  @DiscountAmount money --折扣金额
AS
    IF EXISTS( SELECT *
               FROM   crdtik
               WHERE  ddtxdt = @TransDate AND
                      ddshop = @Shop AND
                      ddcrid = @Crid AND
                      ddcart = @cartID AND
                      ddtick = @DiscountTicketID )

      BEGIN
          UPDATE crdtik
          SET    ddcrid = @Crid,
                 dddsct = @DiscountAmount
          WHERE  ddtick = @DiscountTicketID
      END
    ELSE
      INSERT crdtik
             (ddtxdt,ddshop,ddcrid,ddcart,ddtick,dddsct)
      SELECT @TransDate,@Shop,@Crid,@cartID,@DiscountTicketID,@DiscountAmount
go      