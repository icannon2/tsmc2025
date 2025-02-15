CREATE TABLE Companies_raw (
    CompanyName VARCHAR(255),
    Country VARCHAR(255)
);

INSERT INTO Companies_raw (CompanyName, Country) VALUES ('AMD', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Cirrus Logic', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('TSMC', 'Taiwan');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Microchip', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Intel', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Samsung', 'South Korea');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Texas Instruments', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Google', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Himax', 'Taiwan');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('STM', 'Switzerland');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Broadcom', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Marvell', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Nvidia', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Qorvo', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Western Digital', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Amkor', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('KLA', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Microsoft', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('ON Semi', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Qualcomm', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Amazon', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Apple', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Applied Material', 'USA');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Baidu', 'China');
INSERT INTO Companies_raw (CompanyName, Country) VALUES ('Tencent', 'China');

CREATE TABLE FIN_Data_csv AS 
SELECT * FROM read_csv('FIN_Data.csv');
CREATE TABLE FIN_Data_raw AS
SELECT
    f.CALENDAR_YEAR as CalendarYear,
    f."Company Name" as CompanyName,
    c.Country,
    f.CALENDAR_QTR as CalendarQuarter,
    SUM(CASE WHEN f.Index = 'Cost of Goods Sold' THEN f.USD_Value ELSE NULL END) AS CostOfGoodsSold,
    SUM(CASE WHEN f.Index = 'Operating Expense' THEN f.USD_Value ELSE NULL END) AS OperatingExpense,
    SUM(CASE WHEN f.Index = 'Operating Income' THEN f.USD_Value ELSE NULL END) AS OperatingIncome,
    SUM(CASE WHEN f.Index = 'Revenue' THEN f.USD_Value ELSE NULL END) AS Revenue,
    SUM(CASE WHEN f.Index = 'Tax Expense' THEN f.USD_Value ELSE NULL END) AS TaxExpense,
    SUM(CASE WHEN f.Index = 'Total Asset' THEN f.USD_Value ELSE NULL END) AS TotalAsset
FROM
    FIN_Data_csv f
LEFT JOIN
    Companies_raw c ON f."Company Name" = c.CompanyName
GROUP BY
    f.CALENDAR_YEAR,
    f."Company Name",
    c.Country,
    f.CALENDAR_QTR;

CREATE TABLE TRANSCRIPT_Data_csv AS 
SELECT * FROM  read_csv('TRANSCRIPT_Data.csv');
CREATE TABLE Transcript_File_raw(
  size INTEGER, filename VARCHAR, content VARCHAR
);
INSERT INTO Transcript_File_raw
SELECT 
  size, 
  parse_path(filename) as filename, 
  content 
FROM 
  read_text('Transcript File/*.txt');

CREATE TABLE TRANSCRIPT_Data_raw AS
SELECT
    TDR."Company Name" AS CompanyName,
    TDR.CALENDAR_YEAR as CalendarYear,
    TDR.CALENDAR_QTR as CalendarQuarter,
    CR.Country,
    TFR.filename,
    TFR.content
FROM
    TRANSCRIPT_Data_csv TDR
JOIN
    Companies_raw CR ON TDR."Company Name" = CR.CompanyName
JOIN
    Transcript_File_raw TFR ON TFR.filename LIKE CONCAT('%', TDR.Transcript_Filename, '%');

CREATE TABLE FIN_Data_Derived_raw AS
SELECT
    CalendarYear,
    CompanyName,
    Country,
    CalendarQuarter,
    "Revenue",
    "CostOfGoodsSold",
    "OperatingExpense",
    "OperatingIncome",
    "TaxExpense",
    "TotalAsset",
    ("Revenue" - "CostofGoodsSold") AS GrossProfit,
    CASE
        WHEN "Revenue" = 0 THEN NULL
        ELSE ("Revenue" - "CostOfGoodsSold") / "Revenue" * 100
    END AS GrossProfitMargin,
    CASE
        WHEN "Revenue" = 0 THEN NULL
        ELSE "OperatingIncome" / "Revenue" * 100
    END AS OperatingProfitMargin,
    ("OperatingIncome" - "TaxExpense") AS NetIncomeBeforeTax,
    CASE
        WHEN "Revenue" = 0 THEN NULL
        ELSE ("OperatingIncome" - "TaxExpense") / "Revenue" * 100
    END AS NetProfitMarginBeforeTax,
    CASE
        WHEN "OperatingIncome" = 0 THEN NULL
        ELSE ("TaxExpense" / "OperatingIncome") * 100
    END AS EffectiveTaxRate,
    CASE
        WHEN "TotalAsset" = 0 THEN NULL
        ELSE ("OperatingIncome" - "TaxExpense") / "TotalAsset" * 100
    END AS ReturnOnAssets
FROM
    FIN_Data_raw;

CREATE TABLE Exchange_Rate_raw 
AS
SELECT
    CALENDAR_YEAR as CalendarYear,
    CALENDAR_QTR as CalendarQuarter,
    Local_Currency as LocalCurrency,
    SUM(USD_Value) / SUM(Local_Value) AS ExchangeRate
FROM
    FIN_Data_csv
GROUP BY
    CALENDAR_YEAR,
    Local_Currency,
    CALENDAR_QTR;

CREATE TABLE Fiscal_Data_raw AS
SELECT DISTINCT
    "Company Name" as CompanyName,
    CALENDAR_YEAR as CalenderYear,
    CALENDAR_QTR as CalenderQuarter,
    COALESCE(
        TRY_CAST(REGEXP_EXTRACT(Transcript_Filename, ' Q[1-4] (\d{4})', 1) AS BIGINT),
        CALENDAR_YEAR
    ) AS FiscalYear,
    REGEXP_EXTRACT(Transcript_Filename, ' (Q[1-4]) ', 1) AS FiscalQuarter
FROM TRANSCRIPT_Data_csv;