DROP PROCEDURE MPos_Sync_SaveSku
GO
CREATE PROCEDURE MPos_Sync_SaveSku @barcode VARCHAR(50), @styleID VARCHAR(15), @colorID CHAR(3), @sizeID CHAR(3)
AS
DECLARE @rtn TABLE(returnID INT, returnMessage VARCHAR(256))

IF NOT EXISTS(SELECT * FROM mfskun a WHERE a.skskun = @barcode)
	BEGIN
		INSERT dbo.mfskun
		(
		    skstyl,
		    skcolr,
		    sksize,
		    skskun
		)
		VALUES
		(   @styleID, -- skstyl - char(15)
		    @colorID, -- skcolr - char(3)
		    @sizeID, -- sksize - char(3)
		    @barcode    -- skskun - char(21)
		    )
		
		INSERT @rtn
		(
			returnID,
			returnMessage
		)
		VALUES
		(   1,   -- returnID - int
			'成功' -- returnMessage - varchar(256)
			);
	END
		BEGIN
		INSERT @rtn
		(
			returnID,
			returnMessage
		)
		VALUES
		(   0,   -- returnID - int
			'已经存在' -- returnMessage - varchar(256)
			);

        END
        

	