drop PROCEDURE if EXISTS MPos_Crm01_SaveMemberCard;
GO
create PROCEDURE MPos_Crm01_SaveMemberCard
(
    @MemberType    char(3),
    @memberCard   char(10),
    @memberLevel char(3) = ''
)
AS


if not exists(select * from cccard where cdcard = @memberCard)
    begin
        if @memberLevel = ''
            select @memberLevel = min(lvlevl) from crlevl where lvregn = @MemberType

        declare @discount money
        select @discount = lvdsct from crlevl where lvregn = @MemberType and lvlevl = @memberLevel

        insert cccard(cdcard, cdcust, cddsct,cddate,cdregn, cdlevl,cdcanx)
            values(@memberCard, '',@discount,getdate(),@MemberType,@memberLevel,'N')
    END

go


--exec MPos_Crm01_SaveMemberCard 'GBM','049000212',''

