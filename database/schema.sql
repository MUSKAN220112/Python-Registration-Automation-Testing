CREATE DATABASE IF NOT EXISTS registration_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE registration_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(80) NOT NULL,
  last_name VARCHAR(80) NOT NULL,
  email VARCHAR(254) NOT NULL UNIQUE,
  mobile_number VARCHAR(20) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  gender VARCHAR(20) NOT NULL,
  date_of_birth DATE NOT NULL,
  address VARCHAR(500) NOT NULL,
  country VARCHAR(80) NOT NULL,
  state VARCHAR(80) NOT NULL,
  city VARCHAR(80) NOT NULL,
  postal_code VARCHAR(20) NOT NULL,
  terms_accepted BOOLEAN NOT NULL DEFAULT FALSE
);
