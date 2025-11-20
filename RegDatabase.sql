

create database mydatabase;
show tables;
select * from users;
SELECT DATABASE();
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('student','admin', 'teacher') 
);
-- Add index to speed up email lookups (used in login)
CREATE INDEX idx_email ON users(email);
SHOW INDEX FROM users;-- included--
 ALTER TABLE users-- included --
add COLUMN last_login DATETIME null  ;
select * from pakusers;
CREATE TABLE teaches (
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    PRIMARY KEY (user_id , course_id),
    FOREIGN KEY (user_id)
        REFERENCES users (user_id),
    FOREIGN KEY (course_id)
        REFERENCES courses (course_id)
);

CREATE TABLE courses (
    course_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(150) NOT NULL,
    description TEXT,
    created_by INT,-- admin do not take or teach courses they just create --
    FOREIGN KEY (created_by)
        REFERENCES users (user_id)
);
INSERT INTO courses (title, author, description)
VALUES
('Math 101', 'John Smith', 'Introduction to Mathematics'),
('Science 101', 'Jane Doe', 'Basics of Science'),
('History 101', 'Mike Ross', 'World History Overview'),
('English 101', 'Emma Johnson', 'Basic grammar, reading, and writing skills'),
('Computer Basics', 'Liam Brown', 'Introduction to computers, operating systems, and files'),
('Python Programming', 'Olivia Davis', 'Learn Python fundamentals and build small applications'),
('Web Development', 'Ethan Wilson', 'Learn HTML, CSS, and JavaScript to create web pages'),
('Database Systems', 'Sophia Martinez', 'Covers SQL, data models, and relational database design'),
('Networking Fundamentals', 'Noah Anderson', 'Learn how networks operate, including IP addressing and routing'),
('Cyber Security Basics', 'Ava Thomas', 'Introduction to security threats and safe computing practices'),
('Artificial Intelligence', 'William Garcia', 'Overview of AI concepts, machine learning, and real-world uses'),
('Data Science 101', 'Isabella Taylor', 'Data analysis, visualization, and introduction to machine learning'),
('Mobile App Development', 'James Lee', 'Create Android and iOS apps using modern frameworks');


CREATE TABLE Enrollment (
    en_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    user_id INT, -- there must be a student --
    course_id INT,
    enrollment_date DATE,
    FOREIGN KEY (user_id)
        REFERENCES users (user_id),
    FOREIGN KEY (course_id)
        REFERENCES courses (course_id),
         CONSTRAINT unique_enrollment UNIQUE(user_id,course_id)
);-- included --

SHOW INDEX FROM Enrollment;

CREATE TABLE progress (-- to track the progress of a course --
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    course_id INT,
    completion_percent INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
select u.name,c.title,p.completion_percent
from progress p
join users u on p.user_id = u.user_id
join courses c on p.course_id = c.course_id;

-----------------------------------------------------------------------------
-- Create a new table to record the activity: --
CREATE TABLE enrollment_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    course_id INT,
    action VARCHAR(50),
    log_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
-- Create a trigger that runs after an enrollment is added: --


SELECT * FROM course_summary;

----------------------------------------------------
SHOW TABLES;
USE mydatabase;
DESCRIBE courses;
DESCRIBE Enrollment;
select * from users;
SELECT * FROM courses; 
 SELECT * FROM Enrollment;
 SHOW CREATE TABLE users;
DESCRIBE users;


