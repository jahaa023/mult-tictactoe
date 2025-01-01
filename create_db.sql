-- SQL file for creating database and necessary tables

CREATE DATABASE IF NOT EXISTS tictactoe;

USE tictactoe;

-- Users table

CREATE TABLE IF NOT EXISTS users (
    user_id varchar(16) NOT NULL,
    username varchar(30) NOT NULL,
    password varchar(32) NOT NULL,
    PRIMARY KEY(user_id)
);