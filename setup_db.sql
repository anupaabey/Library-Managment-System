-- Run this in MySQL before launching the app
-- mysql -u root -p < setup_db.sql

CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- Tables are auto-created by the app on first run.
-- Default admin credentials:
--   Username: admin
--   Password: admin123

-- Optional: seed some sample data
INSERT IGNORE INTO books (isbn, title, author, genre, year, copies, available) VALUES
('978-0-06-112008-4', 'To Kill a Mockingbird', 'Harper Lee',      'Fiction',   1960, 3, 3),
('978-0-7432-7356-5', '1984',                  'George Orwell',   'Dystopian', 1949, 2, 2),
('978-0-7432-7357-2', 'The Great Gatsby',      'F. Scott Fitzgerald','Classic',1925, 2, 2),
('978-0-14-028329-7', 'Of Mice and Men',       'John Steinbeck',  'Fiction',   1937, 2, 2),
('978-0-06-093546-9', 'To Kill a Mockingbird', 'Harper Lee',      'Fiction',   1960, 1, 1);

INSERT IGNORE INTO members (member_id, name, email, phone, status) VALUES
('MEM001', 'Alice Johnson', 'alice@email.com',   '0771234567', 'Active'),
('MEM002', 'Bob Smith',     'bob@email.com',     '0777654321', 'Active'),
('MEM003', 'Carol White',   'carol@email.com',   '0779876543', 'Active');
