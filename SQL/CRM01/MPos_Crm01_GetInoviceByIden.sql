--WARNING! ERRORS ENCOUNTERED DURING SQL PARSING!
DROP PROCEDURE  MPos_Crm01_GetInoviceByIden
GO

CREATE PROCEDURE MPos_Crm01_GetInoviceByIden @shopID NVARCHAR(12),
    @iden CHAR(12)
AS
DECLARE @tranDate SMALLDATETIME
DECLARE @crid CHAR(3)
DECLARE @invo INT

SELECT @tranDate = a.shtxdt,
    @crid = shcrid,
    @invo = shinvo
FROM crsalh a
WHERE a.shshop = @shopID
    AND a.shiden = @iden

SELECT shshop ShopID,
    shtxdt TranDate,
    shcrid Crid,
    shinvo invoiceID,
    shcust CustomerID,
    shupdt [Update],
    a.shuser Cashier,
    a.shvoid Void,
    a.shtxtm EnterTime,
    a.shsalm SalesAssociate,
    a.shiden Iden,
    a.shamnt TotalAmount,
    a.shtqty TotalQty
FROM crsalh a
WHERE a.shshop = @shopID
    AND a.shtxdt = @tranDate
    AND a.shcrid = @crid
    AND a.shinvo = @invo

select x.*, isnull(rtrim(y.phdesc),'') PromotionDescription  from(
SELECT 
    rtrim(a.sdskun) Barcode,
    b.skstyl StyleCode,
    rtrim(c.smldes) StyleLocalDescription,
    RTRIM(c.smedes) StyleEnglishDescription,
    b.skcolr Color,
    b.sksize [Size],
    (sdtqty * sdsprc - sddsct)/ a.sdtqty  Price,
    a.sdsprc UnitPrice,
    (sdtqty * sdsprc - sddsct) Amount,
    a.sdtqty* a.sdsprc  UnitPriceAmount,
    1 - a.sddsct/ (a.sdtqty* a.sdsprc) DiscountRate,
    a.sddsct TotalDiscountAmount,
    a.sdtqty Qty,
    a.sddscd DiscountType,
    a.sdprom PromotionCode        
FROM crsald a, mfskun b, mfstyl c
WHERE a.sdshop = @shopID
    AND a.sdtxdt = @tranDate
    AND a.sdcrid = @crid
    AND a.sdinvo = @invo
    AND a.sdskun = b.skskun
    and b.skstyl = c.smstyl
) as x left join crpomh(nolock) y on x.PromotionCode=y.phtxnt



SELECT 
    a.cttdrt [PaymentType],
    B.tdldes [PaymentDescription],
    a.ctcurr [Currency],
    a.ctlamt [LocalAmount],
    a.ctoamt [originalAmount],
    a.ctexrt [exchangeRate]
    
FROM crctdr a, mftdrt B
WHERE a.ctshop = @shopID
    AND a.cttxdt = @tranDate
    AND a.ctcrid = @crid
    AND a.ctinvo = @invo
    AND a.cttdrt = b.tdtdrt
    AND a.ctmakt = b.tdmakt

SELECT a.cpprop [Property],
    a.cpvalu [Value]
FROM crprop a
WHERE a.cpshop = @shopID
    AND a.cptxdt = @tranDate
    AND a.cpcrid = @crid
    AND a.cpinvo = @invo
GO


