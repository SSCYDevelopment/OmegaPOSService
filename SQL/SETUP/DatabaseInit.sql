--初始化品牌
INSERT dbo.mfbrnd
       (brbran,
        bredes,
        brldes,
        brshop,
        brbitn,
        brstyl)
VALUES ( 'M&M',-- brbran - char(3)
         'M&M',-- bredes - nchar(20)
         'M&M巧克力',-- brldes - nchar(20)
         'M',-- brshop - char(1)
         1,-- brbitn - int
         '01' -- brstyl - char(2)
)

GO

SELECT *
FROM   MFDSCT
go
INSERT dbo.mfdsct
       (dscode,
        dsptyp,
        dsbbit,
        dsdesc,
        dsdsct,
        dsshty,
        dsssty,
        dsflag,
        dsshop)
VALUES ( 'D1',-- dscode - char(2)
         DEFAULT,-- dsptyp - char(2)
         1,-- dsbbit - int
         '95折',-- dsdesc - nvarchar(100)
         5,-- dsdsct - decimal(5, 2)
         '',-- dsshty - char(1)
         '',-- dsssty - char(1)
         'N',-- dsflag - char(1)
         'GZ86' )

INSERT dbo.mfdsct
       (dscode,
        dsptyp,
        dsbbit,
        dsdesc,
        dsdsct,
        dsshty,
        dsssty,
        dsflag,
        dsshop)
VALUES ( 'D2',-- dscode - char(2)
         DEFAULT,-- dsptyp - char(2)
         1,-- dsbbit - int
         '9折',-- dsdesc - nvarchar(100)
         10,-- dsdsct - decimal(5, 2)
         '',-- dsshty - char(1)
         '',-- dsssty - char(1)
         'N',-- dsflag - char(1)
         'GZ86' )

GO

INSERT dbo.mfshop
       (shshop,
        shmakt,
        shedes,
        shldes,
        shenam,
        shlnam,
        shaddr,
        shrunc,
        shfaxn,
        shmail,
        shtele,
        shpost,
        shcity,
        shtreg,
        shtype,
        shstyp,
        shcent,
        shware,
        shdday,
        shcanx)
VALUES ( 'GZ86',-- shshop - char(5)
         'CN',-- shmakt - char(2)
         'M&M GZ BEIJING ROAD',-- shedes - nchar(40)
         'M&M北京路广百店',-- shldes - nchar(40)
         'M&M GZ',-- shenam - nchar(10)
         'M&M广州店',-- shlnam - nchar(10)
         NULL,-- shaddr - nchar(200)
         NULL,-- shrunc - nchar(40)
         NULL,-- shfaxn - char(20)
         NULL,-- shmail - char(50)
         NULL,-- shtele - char(20)
         NULL,-- shpost - char(10)
         '广州',-- shcity - char(4)
         '',-- shtreg - char(5)
         'D',-- shtype - char(1)
         DEFAULT,-- shstyp - char(1)
         'N',-- shcent - char(1)
         'S',-- shware - char(1)
         DEFAULT,-- shdday - smallint
         DEFAULT -- shcanx - char(1)
)

GO

SELECT *
FROM   dbo.mfmakt

GO

INSERT dbo.mfmakt
       (mkmakt,
        mkname,
        mkcurr,
        mkecom,
        mklcom,
        mkeadd,
        mkladd,
        mktele,
        mkfaxn,
        mkhttp,
        mkserv,
        mkdbas,
        mkofee,
        mkvatx,
        mkiden,
        mkshpp,
        mkpaym,
        mksubc)
VALUES ( 'CN',-- mkmakt - char(2)
         '中国大陆',-- mkname - nvarchar(50)
         'RMB',-- mkcurr - char(3)
         'SANSE',-- mkecom - varchar(255)
         'SANSE',-- mklcom - nvarchar(255)
         NULL,-- mkeadd - varchar(255)
         NULL,-- mkladd - nvarchar(255)
         NULL,-- mktele - varchar(100)
         NULL,-- mkfaxn - varchar(100)
         NULL,-- mkhttp - varchar(100)
         NULL,-- mkserv - varchar(100)
         NULL,-- mkdbas - varchar(20)
         NULL,-- mkofee - decimal(9, 4)
         NULL,-- mkvatx - decimal(5, 2)
         NULL,-- mkiden - int
         NULL,-- mkshpp - varchar(2)
         DEFAULT,-- mkpaym - char(1)
         DEFAULT -- mksubc - char(1)
)

SELECT *
FROM   SYLANG

INSERT SYLANG
       (lnlang,
        lnflag,
        lndesc)
VALUES(1,
       'POS',
       'CHINESE')

GO

SELECT *
FROM   mftdrt

GO

INSERT dbo.mftdrt
       (tdmakt,
        tdtdrt,
        tdldes,
        tdedes,
        tdcurr,
        tdshct,
        tdtype,
        tdctyp,
        tdcanx)
VALUES ( 'CN',-- tdmakt - char(2)
         'C',-- tdtdrt - char(1)
         '现金',-- tdldes - nchar(30)
         'Cash',-- tdedes - char(30)
         'RMB',-- tdcurr - char(3)
         67,-- tdshct - int
         0,-- tdtype - int
         DEFAULT,-- tdctyp - char(2)
         DEFAULT -- tdcanx - char(1)
)

GO

INSERT dbo.mftdrt
       (tdmakt,
        tdtdrt,
        tdldes,
        tdedes,
        tdcurr,
        tdshct,
        tdtype,
        tdctyp,
        tdcanx)
VALUES ( 'CN',-- tdmakt - char(2)
         'G',-- tdtdrt - char(1)
         '广百POS机',-- tdldes - nchar(30)
         'GNGBI POS',-- tdedes - char(30)
         'RMB',-- tdcurr - char(3)
         71,-- tdshct - int
         0,-- tdtype - int
         DEFAULT,-- tdctyp - char(2)
         DEFAULT -- tdcanx - char(1)
)

go

SELECT *
FROM   dbo.mfcurr

go

INSERT dbo.mfcurr
       (cumakt,
        cucurr,
        culdes,
        cuedes,
        cuextr,
        cucanx)
VALUES ( 'CN',-- cumakt - char(2)
         'RMB',-- cucurr - char(3)
         '人民币',-- culdes - nchar(30)
         'RMB',-- cuedes - char(30)
         1,-- cuextr - decimal(12, 6)
         DEFAULT -- cucanx - char(1)
) 

GO

/* system configuration*/
SELECT * FROM syconf
GO
DELETE FROM syconf
go

INSERT syconf (cnshop,cnprop,cnvalu)VALUES ('GZ86','ECOMPANY',	'SANSE LTD.')
INSERT syconf (cnshop,cnprop,cnvalu)VALUES ('GZ86','LCOMPANY','盛世长运（广东）控股有限公司')
INSERT syconf (cnshop,cnprop,cnvalu)VALUES ('GZ86','VATRATE','1.13')
INSERT syconf(cnshop,cnprop,cnvalu) VALUES('GZ86','TDECIMAL','2')           


GO
/* current shop*/
SELECT * FROM syshop
go
INSERT syshop (syshop) VALUES ('GZ86')