/*
--**--
*  @name: mfmakt
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: 全部市场纪录
*  @parameter: mkmakt 编号
*  @parameter: mkname 编号
*  @parameter: mkcurr 货币
*  @parameter: mkecom 公司名(英文)
*  @parameter: mklcom 公司名 (长描述)
*  @parameter: mkeadd 公司地址(英文)
*  @parameter: mkladd 公司地址 (长描述)
*  @parameter: mktele Telephone no.
*  @parameter: mkfaxn Fax no.
*  @parameter: mkhttp Giordano web site
*  @parameter: mkserv Tiger web site
*  @parameter: mkdbas Database server 
*  @parameter: mkofee 运费等附加成本 JP = 0.18 
*  @parameter: mkvatx VAT
*  @parameter: mkiden ???
*  @parameter: mkshpp 店铺代码前缀
*  @parameter: mkpaym 是(Y)否有PAYMENT系统 
*  @parameter: mksubc 是(Y)否有分公司在当地,判断是否可以由收货market出SO
--**--
*/
Create Table mfmakt (mkmakt  char(2),
                     mkname  nvarchar(50),
                     mkcurr  char(3),
                     mkecom  varchar(255),
                     mklcom  nvarchar(255),
                     mkeadd  varchar(255),
                     mkladd  nvarchar(255),
                     mktele  varchar(100),
                     mkfaxn  varchar(100),
                     mkhttp  varchar(100),
                     mkserv  varchar(100),
                     mkdbas  varchar(20),
                     mkofee  decimal(9,4),   --- 运费等附加成本 JP = 0.18 
                     mkvatx  decimal(5,2),
                     mkiden  int,
                     mkshpp  varchar(2),     ---店铺名字前缀
                     mkpaym  char(1)  default 'Y',        ---是(Y)否有PAYMENT系统
                     mksubc  char(1)  default 'Y',        ---是(Y)否有分公司在当地,判断是否可以由收货market出SO
                     Primary key clustered (mkmakt))
Go

/*
--**--
*  @name: mfshop
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: 店铺 
*  @parameter: shshop 店铺代码
*  @parameter: shmakt 所属市场
*  @parameter: shedes 英文描述
*  @parameter: shldes 长描述
*  @parameter: shenam 英文
*  @parameter: shlnam 本地语言
*  @parameter: shaddr 地址
*  @parameter: shrunc 所属公司
*  @parameter: shfaxn Fax no.
*  @parameter: shmail E-mail
*  @parameter: shtele Telephone no.
*  @parameter: shpost 邮政编码
*  @parameter: shcity 所属城市
*  @parameter: shtreg 转货区域
*  @parameter: shtype 店铺类型 (A-韩国类型AD, D-Direct Shop, C-Counter, W-中国类型AD)
*  @parameter: shstyp 店铺子类型 子类型（AD 1-店，2-Outlet；Direchshop 1-店，2-Outlet；Counter 1-Without Sales Agent，2-With Sales Agent）
*  @parameter: shcent 数据中心 (Tiger AD)
*  @parameter: shware 仓库类型 (W-Warehouse, S-Shop, H-Wholesale(AD 批发 153,163), V-Virtual, P- Personal(个人批发 151))
*  @parameter: shdday 送货天数
*  @parameter: shcanx 是否已取消
--**--
*/

CREATE TABLE mfshop 
    (shshop char(5),
     shmakt char(2),
     shedes nchar(40) ,
     shldes nchar(40) ,
     shenam nchar(10) ,
     shlnam nchar(10) , 
     shaddr nchar(200),
     shrunc nchar(40),
     shfaxn char(20),
     shmail char(50),
     shtele char(20),
     shpost char(10),
     shcity char(4),
     shtreg char(5),
     shtype char(1), -- (A-韩国类型AD, D-Direct Shop, C-Counter, W-中国类型AD,  F -厂商)
     shstyp char(1) default 1, -- 子类型（AD 1-店，2-Outlet；Direchshop 1-店，2-Outlet；Counter 1-Without Sales Agent，2-With Sales Agent）
     shcent char(1),
     shware char(1), -- (W-Warehouse, S-Shop, H-Wholesale(AD 批发 153,163), V-Virtual, P- Personal(个人批发 151))
     shdday smallint default 1, --送货天数
     shcanx char(1) default'',
     primary key clustered(shshop),
     foreign key (shmakt)  references mfmakt(mkmakt))
go



/*
--**--
*  @name: mfbrnd
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: 品牌 
*  @parameter: brbran 品牌
*  @parameter: bredes 品牌(英文) 
*  @parameter: brldes 品牌(长描述)
*  @parameter: brshop 店铺代码
*  @parameter: brbitn 店铺Bit 1=M&M
*  @parameter: brstyl 品牌款式前缀 01=M&M
--**--
*/
CREATE TABLE mfbrnd
(
   brbran char( 3 ),
   bredes nchar( 20 ),
   brldes nchar( 20 ),
   brshop char( 1 ),
   brbitn int,--1=GIO 2=LAD 4=KID 8=BLS 
   brstyl char( 2 ),
   PRIMARY KEY CLUSTERED(brbran)
)
Go 
/*
--**--
*  @name: mfcate
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: Category
*  @parameter: caedes CAT(英文)
*  @parameter: caldes CAT(长描述)
*  @parameter: caline Line 下属
--**--
*/
Create Table mfcate 
(
     cacate char(2),
     caedes nchar(50),
     caldes nchar(50),
     caline char(3),
     Primary Key Clustered(cacate),
)
Go

/*
--**--
*  @name: mfline
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: 没有用
*  @parameter: 
--**--
*/
Create Table mfline 
(
      lnline char(3),
      lnedes nchar(50),
      lnldes nchar(50),
      primary key clustered(lnline),
) 
Go

/*
--**--
*  @name: mfstyl
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: Style
*  @parameter: smstyl 款式(15位)
*  @parameter: smcode 款式(15位)
*  @parameter: smedes 款式(英文)
*  @parameter: smldes 款式(长描述)
*  @parameter: smbran 品牌
*  @parameter: sccate Category
*  @parameter: smline Line
*  @parameter: smseas 季节
*  @parameter: smsprc 原始价
*  @parameter: smcore Core 1 - 创作部物料   2 - 购物包  6 -  购物券  C ，I -  货品 , smcate ='00' and (smcore='1' or smcore='2' or smcore='3' or smcore='4' or smcore='5') 不计算库存  
*  @parameter: smyear 年份
*  @parameter: smcanx 是否已取消
--**--
*/
Create Table mfstyl
    (smstyl char(15),
     smcode CHAR(15),
     smedes nchar(50),
     smldes nchar(50),
     smbran char(3),
     smcate char(2),
     smline char(3),
     smseas char(1),
     smsprc money,
     smcore char(1),  -- 1 - 创作部物料   2 - 购物包  6 -  购物券  C ，I -  货品 , smcate ='00' and (smcore='1' or smcore='2' or smcore='3' or smcore='4' or smcore='5') 不计算库存  
     smyear smalldatetime,
     smcanx char(1),
     Primary Key Clustered(smstyl),
     foreign Key (smbran) references mfbrnd(brbran),
     foreign key (smcate) references mfcate(cacate),
     foreign key (smline) references mfline(lnline))
Go
Create Index mfstyl1 on mfstyl(smcode) 
Go


/*
--**--
*  @name: mfskun
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: SKU主档案
*  @parameter: skstyl 款式
*  @parameter: skcolr 颜色
*  @parameter: sksize Size
*  @parameter: skskun SKU
--**--
*/
Create Table mfskun
    (skstyl char(15),
     skcolr char(8),
     sksize char(8),
     skskun char(21),
     primary key clustered(skskun),
     foreign key (skstyl) references mfstyl(smstyl))
Go


/*
--**--
*  @name: mftdrt
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: 付款方式
*  @parameter: tdmakt 市场
*  @parameter: tdtdrt 付款方式
*  @parameter: tdldes 付款方式英文描述
*  @parameter: tdedes 付款方式长描述
*  @parameter: tdcurr 货币
*  @parameter: tdshct Short cut
*  @parameter: tdctyp 信用卡类型，用于与读卡机联系
*  @parameter: tdtype 类型(1 - 不计算销售额; 2 - 不计算销售税; 4 - 储值卡; 8 - 银行卡（包括信用卡）; 
                           16 - Coupon; 32 - 用于退款; 64 - 需要输入卡号; 128 - 使用积分)
*  @parameter: tdcanx 是否取消
--**--
*/
Create Table mftdrt 
       (tdmakt char(2), 
        tdtdrt char(1),
        tdldes nchar(30),
        tdedes char(30),
        tdcurr char(3),
        tdshct int,
        tdtype int default 0,
        tdctyp char(2) default '',
        tdcanx char(1) default 'N',
        primary key clustered(tdmakt, tdtdrt),
        foreign key (tdmakt) references mfmakt(mkmakt))
go

CREATE TABLE dbo.crcart
(
   TransDate        smalldatetime,
   Shop             CHAR( 5 ),
   Crid             CHAR( 3 ),
   CartID           uniqueidentifier,
   InputTime        smalldatetime,
   Seqn             INT,
   ItemType         CHAR( 1 ),
   Sku              CHAR( 21 ),
   StyleCode        CHAR( 15 ),
   Color            CHAR( 3 ),
   SIZE             CHAR( 3 ),
   Price            MONEY,
   Discount         MONEY,
   Qty              INT,
   DiscountType     CHAR( 1 ),
   PromotionCode    varchar( 12 ),
   Amnt             money,
   OPrice           money,
   OAmnt            money,
   SaleType         CHAR( 1 ),
   Line             CHAR( 3 ),
   CHANGE           CHAR( 1 ) DEFAULT '',
   Brand            CHAR( 3 ),
   Cate             CHAR( 2 ),
   Ptype            CHAR( 1 ),
   DMark            money,
   Commision        money,
   PromotionID      varchar( 20 ),
   DiscountID       varchar( 20 ),
   DiscountBrandBit int,
   DiscountPtyp     CHAR( 1 ),
   GPrice           money,
   LostSales        CHAR( 1 ) DEFAULT '',
   CumulateValue    CHAR( 1 ) DEFAULT '',
   VoucherID        varchar( 100 ) DEFAULT '',
   BrandBit         int,
   SupplierID       varchar( 8 ),
   PantsLength      int DEFAULT 0,
   Calced           CHAR( 1 ) DEFAULT '',
   [Message]        nvarchar( 100 ) DEFAULT '',
   IsEshop          CHAR( 1 ) DEFAULT '',
   PRIMARY KEY CLUSTERED(TransDate, Shop, Crid, CartID, Seqn)
)

CREATE TABLE crcarh
(
   TransDate    SMALLDATETIME,
   Shop         CHAR( 5 ),
   Crid         CHAR( 3 ),
   CartID       UNIQUEIDENTIFIER,
   wwscard      CHAR( 10 ) DEFAULT '',
   salm         VARCHAR( 40 ) DEFAULT '',
   defective    CHAR( 1 ) DEFAULT '',
   usepromotion char( 1 ) DEFAULT '',
   iseshop      char( 1 ) DEFAULT '',
   CityID       int DEFAULT 0,
   DistID       int DEFAULT 0,
   Mobile       varchar( 20 ) DEFAULT '',
   ReceiverName nvarchar( 10 ) DEFAULT '',
   [Address]    nvarchar( 200 ) DEFAULT '',
   [Remark]     nvarchar( 200 ) DEFAULT '',
   [ALINUMBER]  varchar( 100 ) DEFAULT '',
   [ALICUST]    varchar( 100 ) DEFAULT '',
   [ALIETF]     varchar( 100 ) DEFAULT '',
   [ALITYPE]    char( 1 ) DEFAULT ''
   PRIMARY KEY CLUSTERED(TransDate, Shop, Crid, CartID)
)

CREATE TABLE crcinv
(
   TransDate smalldatetime,
   Shop      char( 5 ),
   Crid      char( 3 ),
   CartID    uniqueidentifier,
   tdrt      char( 1 ),
   code      char( 20 ),
   curr      char( 3 ),
   lamt      money,
   oamt      money,
   [type]    int,
   [ptype]   char( 1 ),
   extr      money,
   PRIMARY KEY CLUSTERED(TransDate, Shop, Crid, CartID, tdrt)
)

CREATE TABLE cresoh
(
   TransDate    smalldatetime,
   Shop         char( 5 ),
   Crid         char( 3 ),
   Invo         int,
   CartID       uniqueidentifier,
   CityID       int,
   DistID       int,
   Mobile       varchar( 20 ),
   ReceiverName nvarchar( 10 ),
   [Address]    nvarchar( 200 ),
   [Remark]     nvarchar( 200 ) DEFAULT '',
   Procced      char( 1 ) DEFAULT '',
   Esordn       char( 16 ) DEFAULT '',
   ProccedTime  smalldatetime DEFAULT '19800101',
   PRIMARY KEY CLUSTERED(TransDate, Shop, Crid, Invo )
)

CREATE TABLE mfcrid
(
   mcshop char( 5 ),
   mccrid char( 3 ),
   mcmach varchar( 50 ) NOT NULL,
   mcdate datetime DEFAULT GETDATE() NOT NULL,
   PRIMARY KEY(mcshop, mccrid)
) 

CREATE TABLE mfutkn
(
   [mushop] varchar( 55 ) NOT NULL,
   [muuser] nvarchar( 55 ) NOT NULL,
   [mutken] uniqueidentifier NOT NULL,
   [mucrid] char( 3 ) NOT NULL,
   [muadat] smalldatetime NOT NULL,
   [mucdat] datetime NOT NULL DEFAULT GETDATE(),
   [mumach] varchar( 140 ) NOT NULL,
   [mulkey] varchar( 30 ) NOT NULL DEFAULT '',
   CONSTRAINT [PK_mfutkn] PRIMARY KEY ( [muadat], [mucrid], [muuser], [mushop] )
); 





Create Table crsalh (shtxdt smalldatetime,
                     shshop char(5) Foreign Key (shshop) References mfshop(shshop),
                     shcrid char(3),
                     shinvo int Primary Key Clustered (shtxdt, shshop, shcrid, shinvo),
                     shtxtm smalldatetime,
                     shtqty int, 
                     shamnt money, 
                     shuser char(40),
                     shupdt char(1),
                     shvoid char(1),
                     shcust char(10),
                     shsalm char(40),
                     shiden char(12),
                     shforw char(10))
Go
/*
--**--
*  @name: crsald
*  @category: Table
*  @section: 销售
*  @type: 店铺销售
*  @purpose: 销售内容
*  @parameter: sdtxdt 销售日期
*  @parameter: sdshop 店铺
*  @parameter: sdcrid 收银机
*  @parameter: sdinvo 单据次序
*  @parameter: sdseqn 销售
*  @parameter: sdtype 卖/退 S/R 
*  @parameter: sdskun SKU
*  @parameter: sdsprc 金额
*  @parameter: sdtqty 件数
*  @parameter: sddsct 总Discount金额
*  @parameter: sdvata VAT
*  @parameter: sddscd Discount ID
*  @parameter: sdprom Promotion ID
--**--
*/

Create Table crsald (sdtxdt smalldatetime,
                     sdshop char(5),
                     sdcrid char(3),
                     sdinvo int,
                     sdseqn tinyint,
                     sdtype char(1),
                     sdskun char(21),
                     sdsprc money,
                     sdtqty int,
                     sdwght money,
                     sddsct money,
                     sdvata money,
                     sddscd char(2) default'',
                     sdprom char(12)default'',
                     Foreign key (sdtxdt, sdshop, sdcrid, sdinvo) References crsalh(shtxdt, shshop, shcrid, shinvo),
                     primary key clustered (sdtxdt, sdshop, sdcrid, sdinvo, sdseqn),
                     Foreign key (sdskun) References mfskun(skskun))
GO

/*
--**--
*  @name: crctdr
*  @category: Table
*  @section: 销售
*  @type: 店铺销售
*  @purpose: 每条销售的付款纪录
*  @parameter: cttxdt 销售日期
*  @parameter: ctshop 店铺
*  @parameter: ctcrid 收银机
*  @parameter: ctinvo 单据次序
*  @parameter: ctmakt 市场
*  @parameter: cttdrt 付款方式
*  @parameter: ctcrdn 信用卡编号
*  @parameter: ctcurr 货币
*  @parameter: ctlamt 本地货币
*  @parameter: ctoamt 原货币
*  @parameter: ctexrt 原货币兑本地货币兑换率
--**--
*/
Create Table crctdr (cttxdt smalldatetime,
                     ctshop char(5),
                     ctcrid char(3),
                     ctinvo int ,
                     ctmakt char(2),
                     cttdrt char(1),
                     ctcrdn char(20),
                     ctcurr char(3),
                     ctlamt money,
                     ctoamt money,
                     ctexrt decimal(12,6),
                     Foreign key (ctmakt, cttdrt) References mftdrt(tdmakt, tdtdrt),
                     Foreign key (cttxdt, ctshop, ctcrid, ctinvo) References crsalh(shtxdt, shshop, shcrid, shinvo),
                     Foreign key (ctmakt, ctcurr) References mfcurr(cumakt, cucurr),
                     Primary Key Clustered (cttxdt, ctshop, ctcrid, ctinvo, ctmakt, cttdrt, ctcrdn, ctcurr))
Go



/*
--**--
*  @name: mfdsct
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: Discount
*  @parameter: dscode Discount ID
*  @parameter: dsptyp P type
*  @parameter: dsbbit 适用品牌
*  @parameter: dsdesc Discount描述
*  @parameter: dsshty 店铺类型mfshop.shtype
*  @parameter: dsssty 店铺子类型mfshop.shstyp
*  @parameter: dsflag ???
--**--
*/
CREATE TABLE mfdsct
(
   dscode CHAR( 2 ) PRIMARY KEY CLUSTERED,dsptyp CHAR( 2 ) DEFAULT '',dsbbit INT,--brand
   dsdesc NVARCHAR( 100 ),dsdsct DECIMAL( 5, 2 ),dsshty CHAR( 1 ),--mfshop.shtype
   dsssty CHAR( 1 ),--mfshop.shstyp
   dsflag CHAR( 1 ),
   dsshop CHAR(5)
)


/*
--**--
*  @name: syconf
*  @category: Table
*  @section: System
*  @type: Configuration
*  @purpose: System configuration
*  @parameter: cnShop 店铺
*  @parameter: cnprop 属性
*  @parameter: cnvalu 数值
-- ECOMPANY      Company English Name
-- LCOMPANY      Company Local Name
-- EXEVERSION    Exe Version
-- SQLVERSION    Sql Version
-- EXPIRE        Expire Date
-- CURRENCY      Currency
-- VATRATE       Vat Rate                
-- TRQUDEST      TRQ Destination
-- WHRS          Warehouse
-- ONLINE        Online Mode('Y'：做DAYEND检查；'N'：不做DAYEND检查)
-- HTTP          Web Site
-- PROMOTION     Enable Promotion Function
-- WEBREG        Enable Web Register Function
-- INVOMSG       Message In Invoice
-- TDECIMAL      Tender Decimal
-- ADJUPDATE     Auto Confirm Stock Take
-- PROCDATE      Begin date For process movement with Job  
-- DWDATABASE    Database For Datawarehouse
-- PRICESHOP     Shop For Price Referrence
-- REPLBY        eg. CRSSUM
-- TARGETTYPE    Target Type in Onlinesales ('GP' ot 'SALES')
-- SKOINTVL      Auto Confirm Date For Stock In/Out
-- WHOUT         Stock Out by WH, 'F'--Confirmed by WH; 'T'--Confirmed by Shop
-- SHOUT         Stock Out by Shop, 'F'--Confirmed by Out_Shop; 'T'--Confirm by In_Shop
-- MODIRDATE     是否可以修改收货日期 'Y' - 可以修改  'N' - 不可以修改 
-- PRTNONLOCA    拣货单是否打印没货架位置的记录; Y -打印 ; N - 不打印
-- PICKORDER	  是否按字段来分开Gen Picking(在ap_whm02_mergdata,ap_whm02_genWpikn里用);枚举型 Local:按whlocal.lcloca的第一个字分单，Brand:按mfbran.brbran,Core:按mfstyl.smcore
-- PICKPRNT		  打印picking时的SortBy，枚举型 Local:按whlocal.lcloca的第一个字分单，Brand:按mfbran.brbran,Core:按mfstyl.smcore,Style：按style
-- PICKUSER      是否统计员工的执货，分单程序是否必要用 'Y' / 'N'
-- PICKTIME      是否统计员工开始执货时间和结束执货时间 ，分单程序是否必要用 'Y' / 'N'
-- PORECINTR     收海外和本地订货时，是否需要计算在途数。Y（计）/N（不计）
-- PRCHMAIL		  单价维护后是否发mail给店铺，'Y' or  'N'
-- PORECSEND     'Y'是店铺做收货，'N'是中心做收货
-- REPLOUT       一补一的时候，是否计算出货数（stock out qty.), 'Y' or 'N'
-- PRIMMARKET	  首要Market(例如在AE或QA，设置为ME)
-- ROUNDDEC      是否在小数点位去0 or 5, 'Y' or 'N'
-- REFUNDINFO    Mandatory Customer Info. when Refund or not
-- PRTTRAPRC     是否在出货上打印单价
-- CHKDAYEND     TigerPosII开机时是否检查传了dayend未 ? 'Y' : 'N'
-- CPVISIBLE     POS机上的清机、收银总结报表中是否显示COUPON的数据('Y':显示；'N'：不显示)
-- KEYSALM 		  指定 TigerPosCRM01的按回车后跳到那个控件
-- KEYVIPC
-- KEYFORW
-- KEYNTN
-- KEYSEX
-- KEYAGE
-- KEYSKUN
-- WHDSHPS       印KR送货单要多印一份的店铺
-- SEPARATEWH    是否把仓库的库存按店铺类型分开记录
-- GRCURRENCY    Group Currency for encashing purchase point
-- GWSREDEEM     GWS是否可用
-- VIPPSWTIME    VIP顾客密码错误输入次数上限
-- PURCHASEBF    在通过GWS验证积分前,检测客人N分钟前的消费积分
-- WWSSTORE      存储WWS卡的store，用于没有硬卡时，由系统分配卡号
-- DEFMEMBER     店铺默认开卡的类型和层次（6位：kind+level）
-- VOUCHERSKU    优惠购物券对应的SKU
--**--
*/
Create Table syconf(
     cnshop char(5),
     cnprop char(10),
     cnvalu nvarchar(200),
     primary key clustered (cnshop, cnprop))

GO


CREATE TABLE [dbo].[crpomh]
(
	[phshop] CHAR(5) NOT NULL , 
    [phtxnt] CHAR(8) NOT NULL, 
    [phfdat] SMALLDATETIME NOT NULL, 
    [phtdat] SMALLDATETIME NOT NULL, 
    [phvrgn] CHAR(3) NOT NULL, 
    [phcanx] CHAR NOT NULL, 
    [phvlmt] CHAR NOT NULL DEFAULT '',
    [phdesc] NVARCHAR(100) NOT NULL DEFAULT '',
    [phmdat] smalldatetime, --modify date
    [phuser] CHAR(40) NOT NULL DEFAULT '',
    PRIMARY KEY ([phshop], [phtxnt])
)

CREATE TABLE [dbo].[crpomd]
(
	[pdshop] CHAR(5) NOT NULL , 
    [pdtxnt] CHAR(8) NOT NULL, 
    [pdscop] CHAR(12) NOT NULL, 
    [pdcamt] MONEY NOT NULL, 
    [pdcqty] INT NOT NULL, 
    [pdovex] CHAR NOT NULL, 
    [pdupri] MONEY NOT NULL, 
    [pdudsc] SMALLINT NOT NULL, 
    [pdseqn] TINYINT NOT NULL, 
    [pdstyp] CHAR(1) NULL DEFAULT '', 
    CONSTRAINT [PK_crpomd] PRIMARY KEY ([pdshop], [pdtxnt], [pdscop]), 
    CONSTRAINT [FK_crpomd_crpomh] FOREIGN KEY ([pdshop], [pdtxnt]) REFERENCES [crpomh]([phshop], [phtxnt])
)

Create Table syshop (syshop char(5),
                     primary key clustered(syshop)) 
GO

/*
--**--
*  @name: mfstmk
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: 本地市场拥有的款式
*  @parameter: skstyl 款式
*  @parameter: skmakt 款式市场
*  @parameter: skenam 款式(英文)
*  @parameter: sklnam 款式(长描述)
*  @parameter: skduty 进口关税 MAL = 0.07
*  @parameter: sksprc 零售价
*  @parameter: skptyp P Type mfptyp.ptptyp
--**--
*/
Create table mfstmk
   (skstyl char(15),
    skmakt char(2),
    skenam nchar(50),
    sklnam nchar(50),
    skduty decimal(9,4),  -- 进口关税 MAL = 0.07
    sksprc money,
    skptyp char(2) default 'N',  -- mfptyp.ptptyp 
    PRIMARY KEY clustered (skstyl,skmakt),
    foreign key (skstyl) references mfstyl(smstyl))
GO


/*
--**--
*  @name: sydate
*  @category: Table
*  @section: System
*  @type: Configuration
*  @purpose: 系统日期
*  @parameter: sdtxdt 系统日期
--**--
*/
Create Table sydate (sdtxdt smalldatetime)
GO

/*
--**--
*  @name: mfprch
*  @category: Table
*  @section: Master
*  @type: Record
*  @purpose: 零售单价纪录
*  @parameter: pcshop 店铺
*  @parameter: pctxdt 生效日期
*  @parameter: pcstyl 款式
*  @parameter: pccolr 颜色
*  @parameter: pcsize Size
*  @parameter: pcsprc 零售单价
*  @parameter: pccomi Commission
*  @parameter: pcdate 修改日期
*  @parameter: pcreas 理由
*  @parameter: pctype 零售价类型 N (可以在POS上打折)  S (不可以在POS上打折)  P(为出tax accouting 促销单价)
*  @parameter: pcuser 修改用户
*  @parameter: pcptyp p Type
*  @parameter: pcdmak Discount markt
--**--
*/
Create Table mfprch
       (pcshop char(5),
        pctxdt smalldatetime,
        pcstyl char(15),
        pccolr char(2) default '  ',
        pcsize char(2) default '  ',
        pcsprc money,
        pccomi decimal(5,2),
        pcdate smalldatetime,
        pcreas nvarchar(50),
        pctype char(1), -- N (可以在POS上打折)  S (不可以在POS上打折)  P(为出tax accouting 促销单价)
        pcuser char(40),
        pcptyp char(2), -- mfptyp.ptptyp 
        pcdmak decimal(5,2),
        primary key clustered(pcshop, pcstyl, pccolr, pcsize, pctxdt),
        foreign key (pcshop) references mfshop(shshop),
        foreign key (pcstyl) references mfstyl(smstyl))
Go
Create Index mfprch1 on mfprch(pcshop, pcstyl, pctxdt, pccolr, pcsize)

Go
/*
--**--
*  @name: crcdwh
*  @category: Table
*  @section: 销售
*  @type: 店铺清机
*  @purpose: 店铺清机header
*  @parameter: dhtxdt 销售日期
*  @parameter: dhshop 店铺
*  @parameter: dhcrid 收银机
*  @parameter: dhshft 更次
*  @parameter: dhfinv 开始发票号
*  @parameter: dhtinv 结束发票号
*  @parameter: dhclrf 是否已清机
*  @parameter: dhconf 是否已确认 
*  @parameter: dhdinv Discount总发票数
*  @parameter: dhdqty Discount总件数
*  @parameter: dhdamt Discount总金额
*  @parameter: dhrinv 退货总发票数
*  @parameter: dhrqty 退货总件数
*  @parameter: dhrqmt 退货总金额
--**--
*/
Create Table crcdwh (dhtxdt smalldatetime,
                     dhshop char(5),
                     dhcrid char(3),
                     dhshft int,
                     dhfinv int,
                     dhtinv int,
                     dhclrf char(1),
                     dhconf char(1),
                     dhdinv int,
                     dhdqty int,
                     dhdamt money,
                     dhrinv int,
                     dhrqty int,
                     dhramt money,
                     Primary Key Clustered(dhtxdt, dhshop, dhcrid, dhshft),
                     Foreign Key (dhshop) References mfshop(shshop))
Go
Create Index crcdwh1 on crcdwh(dhconf, dhtxdt, dhshop,dhcrid, dhshft) 
Go

/*
--**--
*  @name: crcdwd
*  @category: Table
*  @section: 销售
*  @type: 店铺清机
*  @purpose: 店铺清机内容
*  @parameter: ddtxdt 销售日期
*  @parameter: ddshop 店铺
*  @parameter: ddcrid 收银机
*  @parameter: ddshft 更次
*  @parameter: ddmakt 市场
*  @parameter: ddtdrt 付款方式
*  @parameter: ddcurr 货币
*  @parameter: ddlamt 本地货币金额
*  @parameter: ddoamt 原货币金额
*  @parameter: ddaamt 修改金额
--**--
*/
Create Table crcdwd (ddtxdt smalldatetime,
                     ddshop char(5),
                     ddcrid char(3),
                     ddshft int ,
                     ddmakt char(2),
                     ddtdrt char(1),
                     ddcurr char(3),
                     ddlamt money,
                     ddoamt money,
                     ddaamt money,
                     primary key clustered (ddtxdt, ddshop, ddcrid, ddshft, ddtdrt, ddcurr),
                     Foreign Key (ddtxdt, ddshop, ddcrid, ddshft) References crcdwh(dhtxdt, dhshop, dhcrid, dhshft),
                     Foreign key (ddmakt,ddtdrt) References mftdrt(tdmakt,tdtdrt),
                     Foreign key (ddmakt,ddcurr) References mfcurr(cumakt,cucurr))
Go

/*
--**--
*  @name: crregn
*  @category: Table
*  @section: VIP
*  @type: 設定
*  @purpose: VIP顾客区域（顾客类型）
*  @parameter: cnregn 區域
*  @parameter: cndesc 區域描述
*  @parameter: cnauto 是否自动生成卡号(Y：自动，N：手动)
*  @parameter: cnsvip 是否向其他市场发送
*  @parameter: cnperv 有效天数(>0：卡的有效期；<0：积分的有效期)
*  @parameter: cnlocl 是否是本地卡
*  @parameter: cnbran 所属品牌
*  @parameter: cnprop 属性字段(1-保留验证字段,不计算哈希校验值；
                               2-保留验证字段，计算哈希校验值；
                               4-不能在中心开卡；
                               8-开卡时要输入发票号，验证crlevl.lvamnt；
                               16-积分兑现；
                               32-使用储值信用或积分时通过Web Service验证；
                               64-不允许先入货品再入卡号；
                               128-使用储值信用或积分时需要提供密码；
                               256-使用信用金额；
                               512-生日当月折扣；
                               1024-发送消费SMS；
                               2048-VIP消费可以开卡；
                               4096-积分抵扣不循环累计
                              )
--**--
*/
Create Table crregn (cnregn char(3),
                     cndesc nvarchar(20),
                     cnauto char(1) Default 'Y',
                     cnsvip char(1) Default 'N',
                     cnperv smallint Default 0,
                     cnlocl char(1) Default 'Y',
                     cnbran int,
                     cnprop smallint Default 0,
                     Primary Key Clustered(cnregn)
		              )
Go

/*
--**--
*  @name: cccust
*  @category: Table
*  @section: VIP
*  @type: 客戶
*  @purpose: 客戶資料(店铺)
*  @parameter: cmcust VIP ID
*  @parameter: cmregn 区域（顾客类型）
*  @parameter: cmlnam 姓
*  @parameter: cmfnam 名 
*  @parameter: cmdnam 顯示名
*  @parameter: cmborn 出生日期
*  @parameter: cmiden 验证字段
--**--
*/
CREATE TABLE cccust (
	cmcust CHAR(10),
	cmregn CHAR(3),
	cmlnam NVARCHAR(50),
	cmfnam NVARCHAR(50),
	cmdnam NVARCHAR(50),
	cmborn SMALLDATETIME,
	cmiden VARCHAR(50),
	cmsure CHAR(1) DEFAULT '2',
	cmcoup CHAR(1) DEFAULT '',
	PRIMARY KEY CLUSTERED (cmcust),
	FOREIGN KEY (cmregn) REFERENCES crregn(cnregn)
	)
GO

CREATE INDEX cccust1 ON cccust (
	cmregn,
	cmlnam,
	cmfnam,
	cmdnam,
	cmiden
	)
GO
/*
--**--
*  @name: crlevl
*  @category: Table
*  @section: VIP
*  @type: 設定
*  @purpose: 级别主表
*  @parameter: lvregn 區域（顾客类型）
*  @parameter: lvlevl 级别
*  @parameter: lvldes 描述
*  @parameter: lvdsct 默认折扣
*  @parameter: lvamnt 消费金额尺度
--**--
*/
Create Table crlevl(lvregn char(3),
                    lvlevl char(3),
                    lvldes nvarchar(50),
                    lvdsct decimal(5,2),
                    lvamnt money,
                    lvbdst decimal(5,2),
                    lvocpy decimal(5,2),
                    Primary Key Clustered(lvregn,lvlevl),
                    Foreign Key (lvregn) References crregn(cnregn)
                   )
Go



/*
--**--
*  @name: crcard
*  @category: Table
*  @section: VIP
*  @type: 客戶
*  @purpose: 卡主表（店铺）
*  @parameter: cdcard 卡号
*  @parameter: cdcust 对应的客户
*  @parameter: cddsct 应用的折扣
*  @parameter: cddate 开卡日期 
*  @parameter: cdregn 区域（顾客类型）
*  @parameter: cdlevl 级别
*  @parameter: cdcanx 是否被取消
--**--
*/
create table cccard (cdcard char(10),
                     cdcust char(10),
                     cddsct decimal(5,2),
                     cddate smalldatetime,
                     cdregn char(3),
                     cdlevl char(3),
                     cdcanx char(1)
                     Primary Key Clustered(cdcard),
                     Foreign Key (cdcust) References cccust(cmcust),
                     Foreign Key (cdregn,cdlevl) References crlevl(lvregn,lvlevl)
                    )
Go


/*
--**--
* @name: crpmct
* @category: Table
* @setion: VIP
* @type:
* @purpose: 推广活动对VIP客人的限制（店铺表）
* @parameter: pcpomo promotion ID
* @parameter: pccust 顾客号
--**--
*/
Create Table crpmct (pcpomo char(12),
                     pccust char(10),
                     Primary Key Clustered(pcpomo,pccust)
                    )
Go

/*
--**--
*  @name: crscop
*  @category: Table
*  @section: VIP
*  @type: 設定
*  @purpose: VIP促销活动适用的款式范围
*  @parameter: scscop 款式范围编号
*  @parameter: scstyl 款式
*  @parameter: scstyp 吻合类型
*/
CREATE TABLE [dbo].[crscop]
(
	[scscop] CHAR(12) NOT NULL , 
    [scstyl] VARCHAR(50) NOT NULL, 
    [scstyp] CHAR(1) NULL DEFAULT '', 
    PRIMARY KEY ([scscop], [scstyl])
)


/*
--**--
*  @name: syproc
*  @category: Table
*  @section: System
*  @type: Process
*  @purpose: 等待处理的数据
*  @parameter: prshop 店铺
*  @parameter: prtype 数据类型
*  @parameter: prtxnt 数据参数
--**--
*/
--CRSAL,CRVOD.SKADJ,SKIHI,SKIHO,SKOHI,SKOHO,SKTAK,WCOST
Create Table syproc 
    (prshop char(5),
     prtype char(5),
     prtxnt char(40),
     primary key clustered (prshop, prtype, prtxnt))
Go

/*
--**--
*  @name: crdtik

*  @category: Table
*  @section: pos
*  @type: 收银
*  @purpose: discount ticket
*  @parameter: ddtxdt 交易日期
*  @parameter: ddshop 店铺
*  @parameter: ddcrid 收银机
*  @parameter: ddcart 购物车ID
*  @parameter: ddtick 折扣券号码
*  @parameter: dddisc 折扣金额
--**--
*/

CREATE TABLE crdtik
(
   ddtxdt smalldatetime,
   ddshop char(5),
   ddcrid char(3),
   ddcart uniqueidentifier,
   ddtick varchar(25),
   dddsct money,
   PRIMARY KEY CLUSTERED(ddtxdt, ddshop, ddcrid, ddcart)
)