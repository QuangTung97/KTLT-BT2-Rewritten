CREATE SCHEMA IF NOT EXISTS `MONITOR` DEFAULT CHARACTER SET utf8
COLLATE utf8_general_ci;
USE `MONITOR`;

CREATE TABLE IF NOT EXISTS `MONITOR`.`SERVER` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`NAME` VARCHAR(45) NULL,
	PRIMARY KEY (`id`),
	INDEX `NAME_IDX` (`NAME` ASC))
ENGINE = InnoDB ;


CREATE TABLE IF NOT EXISTS `MONITOR`.`USER` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`UID` INT NULL,
	`NAME` VARCHAR(45) NULL,
	`SERVER` VARCHAR(45) NULL,
	PRIMARY KEY (id) ,
	UNIQUE INDEX `USER_IDX` (`UID` ASC, `NAME` ASC),
	INDEX `SERVER_FK_IDX` (`SERVER` ASC),
	CONSTRAINT `USER_SERVER_FK`
		FOREIGN KEY (`SERVER`)
		REFERENCES `MONITOR`.`SERVER` (`NAME`)
	ON DELETE CASCADE
	ON UPDATE CASCADE)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `MONITOR`.`JOB` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`PID` INT NULL,
	`UID` INT NULL,
	`START_TIME` DATETIME NULL,
	`CMD_NAME` VARCHAR(45) NULL,
	`COMMAND` LONGTEXT NULL,
	`SERVER` VARCHAR(45) NULL,
	PRIMARY KEY (`id`) ,
	UNIQUE INDEX `P_IDX` (`PID` ASC, `UID` ASC, `START_TIME` ASC) ,
	INDEX `UID_FK_IDX` (`UID` ASC),
	INDEX `SERVER_FK_IDX` (`SERVER` ASC),
	CONSTRAINT `JOB_UID_FK`
		FOREIGN KEY (`UID`)
		REFERENCES `MONITOR`.`USER` (`UID`)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	CONSTRAINT `JOB_SERVER_FK`
		FOREIGN KEY (`SERVER`)
		REFERENCES `MONITOR`.`SERVER` (`NAME`)
		ON DELETE CASCADE
		ON UPDATE CASCADE)
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `MONITOR`.`jSAMPLE` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`PID` INT NULL,
	`UID` INT NULL,
	`START_TIME` DATETIME NULL,
	`RUN_TIME` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
	`CPU` DECIMAL(6, 3) NULL,
	`RAM` DECIMAL(6, 3) NULL,
	`RAM_RSS` INT NULL,
	`RAM_VMS` INT NULL,
	`DISK_IN` INT NULL,
	`DISK_OUT` INT NULL,
	PRIMARY KEY (`id`),
	CONSTRAINT `P_FK`
		FOREIGN KEY (`PID`, `UID` , `START_TIME`)
		REFERENCES `MONITOR`.`JOB` (`PID`, `UID`, `START_TIME`)
		ON DELETE CASCADE
		ON UPDATE CASCADE)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `MONITOR`.`sSAMPLE` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`NAME` VARCHAR(45) NULL,
	`TIMESTAMP` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
	`CPU` DECIMAL(6, 3) NULL,
	`RAM` DECIMAL(6, 3) NULL,
	`RAM_AVAILABLE` INT NULL,
	`RAM_CACHED` INT NULL,
	`RAM_TOTAL` INT NULL,
	`DISK_IN` INT NULL,
	`DISK_OUT` INT NULL,
	PRIMARY KEY (`id`) ,
	INDEX `SERVER_FK_IDX` (`NAME` ASC),
	CONSTRAINT `sSAMPLE_SERVER_FK`
		FOREIGN KEY (`NAME`)
		REFERENCES `MONITOR`.`SERVER` (`NAME`)
		ON DELETE CASCADE
		ON UPDATE CASCADE)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `MONITOR`.`PREDICTION` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`UID` INT NOT NULL,
	USER_NAME VARCHAR(45), 
	LAST_USED_SERVER VARCHAR(45),
	LAST_LOGIN DATETIME, 
	AVG_CPU DECIMAL(6, 3),
	MAX_CPU DECIMAL(6, 3),
	AVG_RAM DECIMAL(6, 3),
	MAX_RAM DECIMAL(6, 3),
	PRIMARY KEY (`id`),
	INDEX `PREDICTION_FK_IDX` (`UID` ASC),
	CONSTRAINT `PREDICTION_USER_FK`
		FOREIGN KEY (`UID`)
		REFERENCES `MONITOR`.`USER` (`UID`)
		ON DELETE CASCADE
		ON UPDATE CASCADE)
ENGINE = InnoDB;
