CREATE DATABASE IF NOT EXISTS `CORA`;

USE `CORA`;

DROP TABLE IF EXISTS `content`;
CREATE TABLE `content` (
  `paper_id` INT,
  `word_cited_id` VARCHAR(58)
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/CORA_csv/content.csv'
INTO TABLE `content`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `cites`;
CREATE TABLE `cites` (
  `cited_paper_id` INT,
  `citing_paper_id` INT
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/CORA_csv/cites.csv'
INTO TABLE `cites`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `paper`;
CREATE TABLE `paper` (
  `paper_id` INT,
  `class_label` VARCHAR(72)
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/CORA_csv/paper.csv'
INTO TABLE `paper`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

