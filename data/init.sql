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
