--创建收银机号
DROP PROCEDURE MPos_Public_CreateCrid
go
CREATE PROCEDURE MPos_Public_CreateCrid
  @shopID  char(5),
  @machine varchar(50)
AS
    DECLARE @crid varchar(3)

    IF EXISTS( SELECT *
               FROM   Mfcrid
               WHERE  mcshop = @shopID AND
                      mcmach = @machine )
      BEGIN
          SELECT @crid = mccrid
          FROM   Mfcrid
          WHERE  mcshop = @shopID AND
                 mcmach = @machine

          UPDATE Mfcrid
          SET    mcdate = Getdate()
          WHERE  mcshop = @shopID AND
                 mcmach = @machine AND
                 mccrid = @crid

          SELECT @crid crid

          RETURN
      END

    DECLARE @err int

    SET @err=1

    DECLARE @count int

    SET @count=1

    WHILE( @err = 1 )
      BEGIN
          DECLARE @crids TABLE
          (
             crid int
          )

          INSERT @crids
          SELECT CONVERT(int, mccrid)
          FROM   Mfcrid(Nolock)
          WHERE  mcshop = @shopID

          IF EXISTS( SELECT *
                     FROM   @crids )
            BEGIN
                SELECT @crid = CONVERT(varchar(3), Min(crid) - 1)
                FROM   @crids
            END
          ELSE
            SET @crid='999'

          WHILE Len(@crid) < 3
            BEGIN
                SET @crid='0' + @crid
            END

          BEGIN Try
              INSERT Mfcrid
                     (mcshop,mccrid,mcmach,mcdate)
              VALUES(@shopID,@crid,@machine,Getdate())

              SET @err=0

              BREAK
          END Try
          BEGIN Catch
              SET @count=@count + 1
              SET @err=1
              SET @crid=''
              IF( @count > 50 )
                BREAK
          END Catch
      END

    SELECT @crid crid

Go 
