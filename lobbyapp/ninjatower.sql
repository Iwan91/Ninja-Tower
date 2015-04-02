-- phpMyAdmin SQL Dump
-- version 3.5.8.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Czas wygenerowania: 02 Kwi 2015, 15:00
-- Wersja serwera: 5.5.32
-- Wersja PHP: 5.4.17

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Baza danych: `ninjatower`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `players`
--

CREATE TABLE IF NOT EXISTS `players` (
  `pid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `login` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Zrzut danych tabeli `players`
--

INSERT INTO `players` (`pid`, `login`, `password`) VALUES
(1, 'root', 'root'),
(2, 'toor', 'toor'),
(3, 'enemy1', 'enemy1'),
(4, 'enemy2', 'enemy2');

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `players_heroes`
--

CREATE TABLE IF NOT EXISTS `players_heroes` (
  `pid` int(10) unsigned NOT NULL,
  `heroes` text NOT NULL COMMENT 'comma separated'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Zrzut danych tabeli `players_heroes`
--

INSERT INTO `players_heroes` (`pid`, `heroes`) VALUES
(1, 'Temari,Ayatsuri'),
(2, 'Temari,Ayatsuri'),
(3, 'Temari,Ayatsuri'),
(4, 'Temari,Ayatsuri');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
