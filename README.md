# 📚 LibraryOS – Library Management System

A professional desktop-based Library Management System built with **Python (Tkinter)** and **MySQL**, developed as part of the SEN4002 Software Design & Development module at Cardiff Metropolitan University (ICBT Campus).

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🔐 Admin Login | Secure SHA-256 hashed password authentication |
| 📖 Book Management | Add, edit, remove and view all books with availability tracking |
| 👥 Member Registration | Register, edit and manage library members |
| 🔄 Borrow & Return | Issue books to members, track due dates, process returns |
| ⚠️ Overdue Detection | Automatically flags overdue books |
| 🔍 Search | Search books by title, author, ISBN or genre |
| 📊 Dashboard | Live statistics – total books, members, borrowed, overdue |

---

## 🛠️ Tech Stack

- **Language:** Python 3.8+
- **GUI Framework:** Tkinter (built-in)
- **Database:** MySQL 8.0+
- **Connector:** mysql-connector-python
- **IDE Recommended:** VS Code / PyCharm

---

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0+
- pip (Python package manager)

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/library-management-system.git
cd library-management-system
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup MySQL Database
```bash
mysql -u root -p < setup_db.sql
```

### 4. Configure database credentials
Open `library_app.py` and update the connection settings (around line 40):
```python
self.connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_MYSQL_PASSWORD",  # ← update this
    database="library_db"
)
```

### 5. Run the application
```bash
python library_app.py
```

---

## 🔑 Default Login

| Username | Password |
|---|---|
| admin | admin123 |

---

## 📁 Project Structure

```
library-management-system/
│
├── library_app.py       # Main application (all modules)
├── setup_db.sql         # Database setup + sample data
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 🗄️ Database Schema

### `books`
| Column | Type | Description |
|---|---|---|
| id | INT PK | Auto-increment ID |
| isbn | VARCHAR(20) | Unique ISBN |
| title | VARCHAR(200) | Book title |
| author | VARCHAR(100) | Author name |
| genre | VARCHAR(50) | Genre |
| year | INT | Publication year |
| copies | INT | Total copies |
| available | INT | Currently available |

### `members`
| Column | Type | Description |
|---|---|---|
| id | INT PK | Auto-increment ID |
| member_id | VARCHAR(20) | Unique member code |
| name | VARCHAR(100) | Full name |
| email | VARCHAR(100) | Email (unique) |
| phone | VARCHAR(20) | Phone number |
| status | ENUM | Active / Suspended |

### `borrowings`
| Column | Type | Description |
|---|---|---|
| id | INT PK | Auto-increment ID |
| book_id | INT FK | References books |
| member_id | INT FK | References members |
| borrow_date | DATE | Date issued |
| due_date | DATE | Return deadline |
| return_date | DATE | Actual return date |
| status | ENUM | Borrowed/Returned/Overdue |

### `admins`
| Column | Type | Description |
|---|---|---|
| id | INT PK | Auto-increment ID |
| username | VARCHAR(50) | Login username |
| password | VARCHAR(64) | SHA-256 hashed |

---

## 📸 Screenshots

*(Add screenshots of your running application here)*

---

## 🧪 Testing

Manual test cases are documented in the project report. Key areas tested:
- Login authentication (valid/invalid credentials)
- Book CRUD operations
- Member registration validation
- Borrow/Return workflow
- Overdue detection logic
- Search functionality

---

## 👤 Author

- **Student ID:** CL/BSCSE-CMU/09/12  
- **Module:** SEN4002 – Software Design & Development  
- **Institution:** Cardiff Metropolitan University / ICBT Campus  
- **Year:** 2025/26

---

## 📄 License

This project is submitted for academic assessment purposes only.
