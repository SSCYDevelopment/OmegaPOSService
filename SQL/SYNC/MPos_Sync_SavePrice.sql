DROP PROCEDURE MPos_Sync_SavePrice
GO

CREATE PROCEDURE MPos_Sync_SavePrice @shopID VARCHAR(10),
	@styleID VARCHAR(15),
	@price SMALLMONEY,
	@fromDate SMALLDATETIME,
	@toDate SMALLDATETIME,
	@reason NVARCHAR(255),
	@priceType INT
AS
IF EXISTS (
		SELECT *
		FROM mfprch a
		WHERE a.pcshop = @shopID
			AND a.pcshop = @shopID
			AND a.pctxdt = @fromDate
			AND a.pcdate = @toDate
			AND a.pcstyl = @styleID
		)
BEGIN
	UPDATE a
	SET a.pcsprc = @price,
		a.pcreas = @reason,
		a.pctype = @priceType
	FROM mfprch(NOLOCK) a
	WHERE a.pcshop = @shopID
		AND a.pctxdt = @fromDate
		AND a.pcdate = @toDate
		AND a.pcstyl = @styleID
END
ELSE
BEGIN
	INSERT dbo.mfprch (
		pcshop,
		pcstyl,
		pcsprc,
		pctxdt,
		pcdate,
		pcreas,
		pctype
		)
	VALUES (
		@shopID, -- pcshop - char(10)
		@styleID, -- pcstyl - char(15)
		@price, -- pcsprc - money
		@fromDate, -- pctxdt - smalldatetime
		@toDate, -- pcdate - smalldatetime
		@reason, -- pcreas - nchar(100)
		@priceType -- pctype - int
		)
END
GO


