USE mydatabase;
SELECT DATABASE();
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user'
);
-- Add index to speed up email lookups (used in login)
CREATE INDEX idx_email ON users(email);
SHOW INDEX FROM users;
DESCRIBE users;
CREATE VIEW pakusers AS
SELECT name,email
from users;
select * from pakusers;
ALTER TABLE users AUTO_INCREMENT = 1;

CREATE TABLE courses(
    course_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT ,
    title    VARCHAR(200) NOT NULL,
    author   VARCHAR (150) NOT NULL ,
	description  TEXT
);
INSERT INTO courses (title, author, description)
      VALUES 
           ('Math 101', 'John Smith', 'Introduction to Mathematics'),
            ('Science 101', 'Jane Doe', 'Basics of Science'),
             ('History 101', 'Mike Ross', 'World History Overview');

CREATE TABLE  Enrollment(
en_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  user_id INT,
    course_id INT,
    enrollment_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)

);
INSERT INTO  Enrollment (user_id, course_id, enrollment_date)
VALUES 
       (17,3,'2025-9-19'),
       (1, 1, '2025-09-18'),   
	   (2, 2, '2025-09-18');

ALTER TABLE Enrollment ADD CONSTRAINT unique_enrollment UNIQUE(user_id,course_id);
SHOW INDEX FROM Enrollment;
select u.name as username ,c.title as course_title ,e.enrollment_date as enrollment_date
from Enrollment e
join users u on e.user_id = u.user_id
join courses c on e.course_id = c.course_id;
SELECT 
    u.name, c.course_id, c.title, c.author, e.enrollment_date
FROM
    Enrollment e
        JOIN
    courses c ON e.course_id = c.course_id;
 ALTER TABLE users
ADD COLUMN last_login DATETIME NULL;
DELIMITER //
CREATE PROCEDURE checkuser(
    IN userid INT,
    OUT existFlag VARCHAR(10)
)
BEGIN 
    DECLARE usercount INT;
    SELECT COUNT(*) INTO usercount FROM users WHERE user_id = userid;

    IF usercount > 0 THEN
        SET existFlag = 'yes';
    ELSE
        SET existFlag = 'no';
    END IF;
END //

DROP PROCEDURE IF EXISTS checkENROLLED;

DELIMITER //

CREATE PROCEDURE checkENROLLED(
    IN p_userid INT,
    OUT existFlag VARCHAR(10)
)
BEGIN
    DECLARE enrolled_count INT;

    SELECT COUNT(*) INTO enrolled_count
    FROM users
    WHERE user_id = p_userid;

    IF enrolled_count > 0 THEN
        SET existFlag = 'YES';
    ELSE
        SET existFlag = 'NO';
    END IF;
END //

DELIMITER ;
CALL checkENROLLED(14,@exists);
SELECT @exists;

----------------------------------------------------
SHOW TABLES;
DESCRIBE courses;
DESCRIBE Enrollment;
select * from users;
SELECT * FROM courses; 
 SELECT * FROM Enrollment;
