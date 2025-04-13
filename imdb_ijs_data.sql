CREATE DATABASE IF NOT EXISTS `imdb_ijs`;

USE `imdb_ijs`;

DROP TABLE IF EXISTS `movies_genres`;
CREATE TABLE `movies_genres` (
  `movie_id` INT,
  `genre` VARCHAR(61)
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/imdb_ijs_csv/movies_genres.csv'
INTO TABLE `movies_genres`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `directors_genres`;
CREATE TABLE `directors_genres` (
  `director_id` INT,
  `genre` VARCHAR(61),
  `prob` FLOAT
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/imdb_ijs_csv/directors_genres.csv'
INTO TABLE `directors_genres`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `movies_directors`;
CREATE TABLE `movies_directors` (
  `director_id` INT,
  `movie_id` INT
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/imdb_ijs_csv/movies_directors.csv'
INTO TABLE `movies_directors`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `actors`;
CREATE TABLE `actors` (
  `id` INT,
  `first_name` VARCHAR(80),
  `last_name` VARCHAR(80),
  `gender` VARCHAR(51)
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/imdb_ijs_csv/actors.csv'
INTO TABLE `actors`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `actor_id` INT,
  `movie_id` INT,
  `role` VARCHAR(80)
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/imdb_ijs_csv/roles.csv'
INTO TABLE `roles`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `directors`;
CREATE TABLE `directors` (
  `id` INT,
  `first_name` VARCHAR(80),
  `last_name` VARCHAR(76)
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/imdb_ijs_csv/directors.csv'
INTO TABLE `directors`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

DROP TABLE IF EXISTS `movies`;
CREATE TABLE `movies` (
  `id` INT,
  `name` VARCHAR(150),
  `year` INT,
  `rank` FLOAT
);

LOAD DATA LOCAL INFILE '/home/rahul/usc/spring25/551/project/nli_db_queries/imdb_ijs_csv/movies.csv'
INTO TABLE `movies`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

