DROP PROC MPos_Crm01_SaveCartPayment
go
CREATE PROC MPos_Crm01_SaveCartPayment
  @TransDate smalldatetime,
  @Shop      char(5),
  @Crid      char(3),
  @CartID    uniqueidentifier,
  @paymentType      char(1) , --支付方式
  @Code      char(20), --支付序列号（卡号、账号）
  @currency      char(3), --货币
  @localAmount      money, --本币
  @originalAmount      money, --原币
  @exchangeRate      MONEY, --汇率
  @type      INT =0, --类型1（备用）
  @ptype     char(1) = '' --类型2（备用）
  
AS
    IF EXISTS( SELECT *
               FROM   crcinv
               WHERE  TransDate = @TransDate AND
                      shop = @Shop AND
                      Crid = @Crid AND
                      CartID = @CartID AND
                      tdrt = @paymentType )
      DELETE crcinv
      WHERE  TransDate = @TransDate AND
             shop = @Shop AND
             Crid = @Crid AND
             CartID = @CartID AND
             tdrt = @paymentType

    INSERT crcinv
           (TransDate,Shop,Crid,CartID,tdrt,code,curr,lamt,oamt,[type],[ptype],extr)
    SELECT @TransDate,@Shop,@Crid,@CartID,@paymentType,@Code,@currency,@localAmount,@originalAmount,@type,@ptype,@exchangeRate

go 


