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
-- Table structure for table `DELETE_shoot_site_azrefs`
--

DROP TABLE IF EXISTS `DELETE_shoot_site_azrefs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `DELETE_shoot_site_azrefs` (
  `SiteName` varchar(100) DEFAULT NULL,
  `ObjName` varchar(100) DEFAULT NULL,
  `ObjAzType` varchar(100) DEFAULT NULL,
  `LatLongPt1` varchar(100) DEFAULT NULL,
  `LatLongPt2` varchar(100) DEFAULT NULL,
  `ObjAz` int(11) DEFAULT NULL,
  `ssaid` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`ssaid`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  `BatchID` varchar(100) NOT NULL DEFAULT 'batchnameYYYYMMDD',
  `SiteName` varchar(100) DEFAULT NULL,
  `PointName` varchar(100) DEFAULT NULL,
  `Tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'JSON array format per ChatGPT suggestion',
  `CamTimeError` int(11) DEFAULT NULL,
  `TZOffset` float DEFAULT NULL,
  `MomentCapture` datetime DEFAULT NULL,
  `MomentDB` datetime DEFAULT curtime(),
  `Basename` varchar(100) DEFAULT NULL,
  `Description` text DEFAULT NULL,
  `Orientation` varchar(100) DEFAULT NULL,
  `Tilt` float DEFAULT 0,
  `LatLong` varchar(100) DEFAULT NULL,
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
  `awimTag` longtext DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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

-- Dump completed on 2026-02-04  9:43:44
