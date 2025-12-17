DROP PROCEDURE if exists dbo.MPos_Public_ChangeTrandate
GO
CREATE proc  MPos_Public_ChangeTrandate @shop CHAR(5)  
as  

declare @ldTxdt smalldatetime  

select @ldTxdt = convert(char(10), getdate(), 101)  

IF EXISTS(SELECT * FROM sysdat WHERE ssshop=@shop)
	update sysdat set sstxdt = @ldTxdt WHERE ssshop=@shop
ELSE
	INSERT sysdat(ssshop,sstxdt) VALUES(@shop,@ldTxdt)

GO