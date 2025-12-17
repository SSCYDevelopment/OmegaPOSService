DROP PROC MPos_Crm01_SaveCartInfo

GO

CREATE PROC MPos_Crm01_SaveCartInfo
  @TransDate    smalldatetime, --销售日期
  @Shop         char(5), --销售门店
  @Crid         char(3), --收银机号码
  @CartID       uniqueidentifier, --购物车ID
  @memberCard      char(10), --会员卡号
  @SalesAssociate         varchar(40),
  @isEshop      char(1) = '',
  @CityID       int = 0,
  @DistID       int = 0,
  @Mobile       varchar(20)='',
  @ReceiverName nvarchar(10) = '',
  @Address      nvarchar(200) = '',
  @Remark       nvarchar(200) = ''
AS
    IF EXISTS( SELECT *
               FROM   crcarh
               WHERE  transdate = @TransDate AND
                      shop = @Shop AND
                      crid = @Crid AND
                      cartid = @CartID )
      UPDATE crcarh
      SET    wwscard = @memberCard,
             salm = @SalesAssociate,
             iseshop = @iseshop,
             CityID = @CityID,
             DistID = @DistID,
             Mobile = @Mobile,
             ReceiverName = @ReceiverName,
             [Address] = @Address,
             [Remark] = @Remark
      WHERE  transdate = @TransDate AND
             shop = @Shop AND
             crid = @Crid AND
             cartid = @CartID
    ELSE
      INSERT crcarh
             (TransDate,shop,crid,cartid,wwscard,salm,iseshop,CityID,DistID,Mobile,ReceiverName,[Address],[Remark])
      SELECT @TransDate,@Shop,@Crid,@CartID,@memberCard,@SalesAssociate,@iseshop,@CityID,@DistID,@Mobile,@ReceiverName,@Address,@Remark

go 
