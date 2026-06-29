/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.14-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: awim
-- ------------------------------------------------------
-- Server version	10.11.14-MariaDB-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bright_star_catalogue`
--

DROP TABLE IF EXISTS `bright_star_catalogue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bright_star_catalogue` (
  `HarvardRevised` int(11) NOT NULL,
  `ReadableName` varchar(100) DEFAULT NULL,
  `RA` double DEFAULT NULL,
  `Declination` double DEFAULT NULL,
  `Distance` float DEFAULT NULL,
  `VisualMagnitude` double DEFAULT NULL,
  `MagRankAll` int(5) DEFAULT NULL,
  `ConstellationFullName` varchar(100) DEFAULT NULL,
  `ConstellationAbbreviation` varchar(10) DEFAULT NULL,
  `MagRankConstellation` int(5) DEFAULT NULL,
  `GreekLetter` varchar(50) DEFAULT NULL,
  `GreekLetterSort` int(11) DEFAULT NULL,
  `FullNameText` varchar(50) DEFAULT NULL,
  `SAO` int(11) DEFAULT NULL,
  PRIMARY KEY (`HarvardRevised`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bsc_remarks`
--

DROP TABLE IF EXISTS `bsc_remarks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bsc_remarks` (
  `HR` int(11) DEFAULT NULL,
  `Count` varchar(50) DEFAULT NULL,
  `Category` varchar(50) DEFAULT NULL,
  `Remark` varchar(128) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cache_astrodata`
--

DROP TABLE IF EXISTS `cache_astrodata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cache_astrodata` (
  `SchemaVersion` smallint(6) NOT NULL,
  `LocationID` int(11) NOT NULL,
  `CacheType` enum('sunmoon_details','astrodata') NOT NULL,
  `ChunkStartUTC` datetime NOT NULL,
  `StepSeconds` smallint(6) NOT NULL,
  `MomentsCount` int(11) NOT NULL,
  `CachedData` longtext DEFAULT NULL,
  `MomentCreated` datetime NOT NULL DEFAULT current_timestamp(),
  `CacheNote` text DEFAULT NULL,
  PRIMARY KEY (`LocationID`,`CacheType`,`ChunkStartUTC`,`SchemaVersion`),
  CONSTRAINT `cache_astrodata_locations_FK` FOREIGN KEY (`LocationID`) REFERENCES `locations` (`loc_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cache_daily_events`
--

DROP TABLE IF EXISTS `cache_daily_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cache_daily_events` (
  `LocationID` int(11) DEFAULT NULL COMMENT 'NULL for fullmoon and newmoon event types',
  `EventType` enum('midnight','sunrise','sunset','bmat','bmnt','bmct','noon','eect','eent','eeat','riseplus6deg','setminus6deg','fullmoon','newmoon','moonrise','moonset') NOT NULL,
  `MomentEvent` datetime NOT NULL,
  `EventBody` enum('sun','moon') DEFAULT NULL,
  `EventAzimuth` float DEFAULT NULL,
  `EventArtifae` float DEFAULT NULL,
  `EventMoonPhaseAngle` float DEFAULT NULL COMMENT 'NULL for all but fullmoon and newmoon event types',
  `event_id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`event_id`),
  KEY `cache_daily_events_LocationID_IDX` (`LocationID`,`EventType`,`MomentEvent`) USING BTREE,
  CONSTRAINT `cache_daily_events_locations_FK` FOREIGN KEY (`LocationID`) REFERENCES `locations` (`loc_id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25717 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `locations`
--

DROP TABLE IF EXISTS `locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `locations` (
  `LocationName` varchar(255) DEFAULT NULL,
  `LocationType` enum('town_square','auto_cluster') NOT NULL,
  `CenterLatitude` double DEFAULT NULL,
  `CenterLongitude` double DEFAULT NULL,
  `loc_id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`loc_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `photos_awim`
--

DROP TABLE IF EXISTS `photos_awim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `photos_awim` (
  `CamFilename` varchar(100) DEFAULT NULL,
  `Artifae` float DEFAULT NULL,
  `AzRefObjName` varchar(100) DEFAULT NULL,
  `AzRefObjGuessAz` float DEFAULT NULL,
  `RefTripodDirectionMoved` varchar(100) DEFAULT NULL,
  `RefTripod1` float DEFAULT NULL,
  `RefTripod2` float DEFAULT NULL,
  `LocationID` int(11) DEFAULT NULL,
  `DistanceFromCenter` float DEFAULT NULL COMMENT 'in meters',
  `SiteName` varchar(100) DEFAULT NULL,
  `PointName` varchar(100) DEFAULT NULL,
  `CamTimeError` int(11) DEFAULT NULL,
  `TZOffset` float DEFAULT NULL,
  `MomentCapture` datetime DEFAULT NULL,
  `MomentDB` datetime DEFAULT current_timestamp(),
  `Basename` varchar(100) DEFAULT NULL,
  `Description` text DEFAULT NULL,
  `Orientation` varchar(100) DEFAULT NULL,
  `Tilt` float DEFAULT 0,
  `Latitude` double DEFAULT NULL,
  `Longitude` double DEFAULT NULL,
  `TerrainElevation` float DEFAULT NULL,
  `PhotoAGL` float DEFAULT NULL,
  `PhotoMSL` float DEFAULT NULL,
  `PhotoAGLDescription` text DEFAULT NULL,
  `AzSource` varchar(100) DEFAULT NULL,
  `AzRefObjAzType` varchar(100) DEFAULT NULL,
  `AzRefObjLatLongPt1` varchar(100) DEFAULT NULL,
  `AzRefObjLatLongPt2` varchar(100) DEFAULT NULL,
  `AzRefObjOrientation` float DEFAULT NULL,
  `AzRefObjAdjAz` float DEFAULT NULL,
  `RefArt` float DEFAULT NULL,
  `RefAltDiff` float DEFAULT NULL,
  `ArtSource` varchar(100) DEFAULT NULL,
  `RefCelestialObj` varchar(100) DEFAULT NULL,
  `RefPixelXY` varchar(100) DEFAULT NULL,
  `Azimuth` float DEFAULT NULL,
  `awimTag` text DEFAULT NULL,
  `photo_id` int(11) NOT NULL AUTO_INCREMENT,
  `Tags` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'JSON array format per ChatGPT suggestion',
  PRIMARY KEY (`photo_id`),
  KEY `photos_awim_locations_FK` (`LocationID`),
  CONSTRAINT `photos_awim_locations_FK` FOREIGN KEY (`LocationID`) REFERENCES `locations` (`loc_id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `photos_groups`
--

DROP TABLE IF EXISTS `photos_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `photos_groups` (
  `GroupName` varchar(256) DEFAULT NULL,
  `GroupSlug` varchar(100) DEFAULT NULL,
  `GroupType` enum('clock','batch','glockenspiel') DEFAULT NULL,
  `group_id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `photos_groups_join`
--

DROP TABLE IF EXISTS `photos_groups_join`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `photos_groups_join` (
  `GroupID` int(11) NOT NULL,
  `PhotoID` int(11) NOT NULL,
  `cpr_id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`cpr_id`),
  UNIQUE KEY `photo_grouping_unique` (`GroupID`,`PhotoID`)
) ENGINE=InnoDB AUTO_INCREMENT=204 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `shoot_recommended`
--

DROP TABLE IF EXISTS `shoot_recommended`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `shoot_recommended` (
  `PhotoName` varchar(100) NOT NULL,
  `Description` varchar(4096) DEFAULT NULL,
  PRIMARY KEY (`PhotoName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-28 23:39:30
