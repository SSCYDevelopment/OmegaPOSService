DROP PROCEDURE MPos_Sync_SaveStyle
GO
CREATE PROCEDURE MPos_Sync_SaveStyle @styleID VARCHAR(15), @localName nVARCHAR(100), @englishName nVARCHAR(100), @brand VARCHAR(15), @unitPrice SMALLMONEY
AS
DECLARE @rtn TABLE(returnID INT, returnMessage VARCHAR(256))

IF NOT EXISTS(SELECT * FROM dbo.mfstyl(NOLOCK) a WHERE a.smstyl = @styleID)
	BEGIN
		INSERT dbo.mfstyl
		(
		    smstyl,
		    smcode,
		    smedes,
		    smldes,
		    smbran,
		    smcate,
		    smline,
		    smseas,
		    smsprc,
		    smcore,
		    smyear,
		    smcanx
		)
		VALUES
		(   @styleID,   -- smstyl - char(15)
		    @styleID, -- smcode - char(8)
		    @englishName, -- smedes - nchar(50)
		    @localName, -- smldes - nchar(50)
		    @brand, -- smbran - char(3)
		    '00', -- smcate - char(2)
		    '000', -- smline - char(3)
		    NULL, -- smseas - char(1)
		    @unitPrice, -- smsprc - money
		    NULL, -- smcore - char(1)
		    NULL, -- smyear - smalldatetime
		    ''  -- smcanx - char(1)
		    )
	END
ELSE
	BEGIN
		UPDATE a SET a.smsprc=@unitPrice, a.smldes=@localName, a.smedes=@englishName, a.smbran = @brand FROM dbo.mfstyl(NOLOCK) a WHERE a.smstyl = @styleID
    END
	
	INSERT @rtn
       (returnID,
        returnMessage)
	VALUES ( 1,-- returnID - int
			 '成功' -- returnMessage - varchar(256)


);