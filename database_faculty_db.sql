CREATE DATABASE faculty_db;

USE faculty_db;

CREATE TABLE faculty (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  title VARCHAR(100),
  department VARCHAR(100),
  email VARCHAR(100),
  phone VARCHAR(50),
  bio TEXT,
  photo VARCHAR(255)
);
CREATE TABLE admin_users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL -- store hashed passwords!
);
INSERT INTO admin_users (username, password)
VALUES ('admin', 'admin123');
select * from admin_users;
select * from faculty;



