CREATE DATABASE stockdetails;

USE stockdetails;

CREATE TABLE record(
	artno numeric(10),
    compname varchar(20),
    price numeric(20),
    profitperc varchar(10),
    quantity numeric(20)
);
SELECT * FROM record;
