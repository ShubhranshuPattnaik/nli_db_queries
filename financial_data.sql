CREATE DATABASE IF NOT EXISTS `financial`;

USE `financial`;

DROP TABLE IF EXISTS `client`;
CREATE TABLE `client` (
  `client_id` INT,
  `gender` VARCHAR(51),
  `birth_date` DATE,
  `district_id` INT
);

LOAD DATA LOCAL INFILE '/Users/shubhranshupattnaik/Desktop/551/project_551/financial_csv/client.csv'
INTO TABLE `client`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `trans`;
CREATE TABLE `trans` (
  `trans_id` INT,
  `account_id` INT,
  `date` DATE,
  `type` VARCHAR(56),
  `operation` VARCHAR(64),
  `amount` INT,
  `balance` INT,
  `k_symbol` VARCHAR(61),
  `bank` VARCHAR(53),
  `account` FLOAT
);

LOAD DATA LOCAL INFILE '/Users/shubhranshupattnaik/Desktop/551/project_551/financial_csv/trans.csv'
INTO TABLE `trans`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `district`;
CREATE TABLE `district` (
  `district_id` INT,
  `A2` VARCHAR(69),
  `A3` VARCHAR(65),
  `A4` INT,
  `A5` INT,
  `A6` INT,
  `A7` INT,
  `A8` INT,
  `A9` INT,
  `A10` FLOAT,
  `A11` INT,
  `A12` FLOAT,
  `A13` FLOAT,
  `A14` INT,
  `A15` FLOAT,
  `A16` INT
);

LOAD DATA LOCAL INFILE '/Users/shubhranshupattnaik/Desktop/551/project_551/financial_csv/district.csv'
INTO TABLE `district`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `account`;
CREATE TABLE `account` (
  `account_id` INT,
  `district_id` INT,
  `frequency` VARCHAR(68),
  `date` DATE
);

LOAD DATA LOCAL INFILE '/Users/shubhranshupattnaik/Desktop/551/project_551/financial_csv/account.csv'
INTO TABLE `account`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `card`;
CREATE TABLE `card` (
  `card_id` INT,
  `disp_id` INT,
  `type` VARCHAR(57),
  `issued` DATE
);

LOAD DATA LOCAL INFILE '/Users/shubhranshupattnaik/Desktop/551/project_551/financial_csv/card.csv'
INTO TABLE `card`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `loan`;
CREATE TABLE `loan` (
  `loan_id` INT,
  `account_id` INT,
  `date` DATE,
  `amount` INT,
  `duration` INT,
  `payments` FLOAT,
  `status` VARCHAR(51)
);

LOAD DATA LOCAL INFILE '/Users/shubhranshupattnaik/Desktop/551/project_551/financial_csv/loan.csv'
INTO TABLE `loan`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `order`;
CREATE TABLE `order` (
  `order_id` INT,
  `account_id` INT,
  `bank_to` VARCHAR(52),
  `account_to` INT,
  `amount` FLOAT,
  `k_symbol` VARCHAR(58)
);

LOAD DATA LOCAL INFILE '/Users/shubhranshupattnaik/Desktop/551/project_551/financial_csv/order.csv'
INTO TABLE `order`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `disp`;
CREATE TABLE `disp` (
  `disp_id` INT,
  `client_id` INT,
  `account_id` INT,
  `type` VARCHAR(59)
);

LOAD DATA LOCAL INFILE '/Users/shubhranshupattnaik/Desktop/551/project_551/financial_csv/disp.csv'
INTO TABLE `disp`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

