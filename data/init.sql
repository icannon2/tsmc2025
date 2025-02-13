CREATE TABLE FIN_Data_raw AS 
SELECT * FROM  read_csv('FIN_Data.csv');
CREATE TABLE TRANSCRIPT_Data_raw AS 
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