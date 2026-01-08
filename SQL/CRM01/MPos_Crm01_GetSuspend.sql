DROP PROC MPos_crm01_GetSuspend

GO

CREATE PROC MPos_crm01_GetSuspend
  @TransDate smalldatetime,
  @Shop      char(5),
  @Crid      char(3)
AS
    SET NOCOUNT ON;
    
    CREATE TABLE #t
    (
       tcardID  varchar( 36 ),
       ttime    smalldatetime,
       tqty     int,
       tamt     money,
       twwscard char( 10 ) DEFAULT '',
       tsalm    varchar( 40 ) DEFAULT '',
       PRIMARY KEY CLUSTERED(tcardID)
    )

    INSERT #t
           (tcardID,ttime,tqty,tamt)
    SELECT crcart.cartid,max(InputTime),sum(CASE
                                              WHEN ItemType = 'S' THEN qty
                                              ELSE 0 - qty
                                            END),sum(CASE
                                                       WHEN ItemType = 'S' THEN Amnt
                                                       ELSE 0 - Amnt
                                                     END)
    FROM   crcart(nolock),crcarh(nolock)
    WHERE  crcart.transdate = @TransDate AND
           crcart.shop = @Shop AND
           crcart.crid = @Crid AND
           crcart.TransDate = crcarh.TransDate AND
           crcart.shop = crcarh.Shop AND
           crcart.Crid = crcarh.Crid AND
           crcart.CartID = crcarh.CartID
    GROUP  BY crcart.CartID

    UPDATE #t
    SET    twwscard = wwscard,
           tsalm = salm
    FROM   crcarh
    WHERE  cartid = tcardID

    SELECT a.tcardID CartID,
           a.ttime [SuspendTime],
           a.tqty [Qty],
           a.tamt [Amount],
           a.twwscard [MemberCard],
           a.tsalm [SalesAssociate]
    FROM   #t a
    ORDER  BY ttime DESC

go 
