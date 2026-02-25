# LibraryOS – Test Cases Documentation
# SEN4002 PORT1 – Testing & Maintenance

## Test Environment
- OS: Windows 10/11
- Python: 3.10+
- MySQL: 8.0
- Date of Testing: 2025

---

## MODULE 1: Authentication

| TC ID | Test Case | Input | Expected Output | Status |
|---|---|---|---|---|
| TC-01 | Valid login | admin / admin123 | Dashboard loads | PASS |
| TC-02 | Wrong password | admin / wrongpass | Error message shown | PASS |
| TC-03 | Empty username | (blank) / admin123 | Warning: fill all fields | PASS |
| TC-04 | Empty password | admin / (blank) | Warning: fill all fields | PASS |
| TC-05 | SQL injection attempt | admin' OR '1'='1 | Login rejected | PASS |

---

## MODULE 2: Book Management

| TC ID | Test Case | Input | Expected Output | Status |
|---|---|---|---|---|
| TC-06 | Add valid book | ISBN, Title, Author filled | Book appears in list | PASS |
| TC-07 | Add duplicate ISBN | Existing ISBN | DB unique constraint error | PASS |
| TC-08 | Add book with missing required fields | Empty title | Validation warning | PASS |
| TC-09 | Edit book title | Select book, change title | Updated in list | PASS |
| TC-10 | Remove book | Select and confirm | Book removed from list | PASS |
| TC-11 | Remove without selection | No row selected | Warning message | PASS |
| TC-12 | Add book with large copies | Copies = 100 | Saves correctly | PASS |

---

## MODULE 3: Member Management

| TC ID | Test Case | Input | Expected Output | Status |
|---|---|---|---|---|
| TC-13 | Register valid member | All fields filled | Member appears in list | PASS |
| TC-14 | Duplicate email | Existing email | DB constraint error | PASS |
| TC-15 | Missing required fields | Empty name | Validation warning | PASS |
| TC-16 | Suspend member | Change status to Suspended | Row shown in red | PASS |
| TC-17 | Edit member phone | Change phone number | Updated in DB | PASS |
| TC-18 | Remove member | Select and confirm | Member removed | PASS |

---

## MODULE 4: Borrow & Return

| TC ID | Test Case | Input | Expected Output | Status |
|---|---|---|---|---|
| TC-19 | Issue book to active member | Select book + member | Record created, available decremented | PASS |
| TC-20 | Issue unavailable book | Book with 0 available | Not shown in dropdown | PASS |
| TC-21 | Issue to suspended member | Suspended member | Not shown in dropdown | PASS |
| TC-22 | Return borrowed book | Select record, confirm | Status = Returned, available incremented | PASS |
| TC-23 | Return already returned | Already returned record | Info: already returned | PASS |
| TC-24 | Overdue detection | due_date < today | Status auto-updated to Overdue | PASS |
| TC-25 | Default due date | Issue book | Due date = today + 14 days | PASS |

---

## MODULE 5: Search

| TC ID | Test Case | Input | Expected Output | Status |
|---|---|---|---|---|
| TC-26 | Search by title | "mockingbird" | Matching books shown | PASS |
| TC-27 | Search by author | "Orwell" | Matching books shown | PASS |
| TC-28 | Search by ISBN | "978-0-06" | Matching books shown | PASS |
| TC-29 | Search by genre | "Fiction" | Matching books shown | PASS |
| TC-30 | Search with no results | "xyz123abc" | "No books found" info | PASS |
| TC-31 | Empty search | (blank) | No results shown | PASS |
| TC-32 | Case-insensitive search | "ORWELL" | Returns results same as "orwell" | PASS |

---

## MODULE 6: Dashboard

| TC ID | Test Case | Expected Output | Status |
|---|---|---|---|
| TC-33 | Total books count | Matches books table count | PASS |
| TC-34 | Members count | Matches members table count | PASS |
| TC-35 | Borrowed count | Shows active borrowings | PASS |
| TC-36 | Overdue count | Shows overdue records | PASS |
| TC-37 | Recent borrowings table | Last 10 records shown | PASS |

---

## Summary

| Module | Total Tests | Passed | Failed |
|---|---|---|---|
| Authentication | 5 | 5 | 0 |
| Book Management | 7 | 7 | 0 |
| Member Management | 6 | 6 | 0 |
| Borrow & Return | 7 | 7 | 0 |
| Search | 7 | 7 | 0 |
| Dashboard | 5 | 5 | 0 |
| **TOTAL** | **37** | **37** | **0** |

---

## Maintenance Notes

- **Overdue Update**: Runs automatically on every visit to Borrow/Return tab
- **Password Security**: SHA-256 hashing used — passwords never stored in plain text
- **Foreign Keys**: Enabled to maintain data integrity across tables
- **Future Maintenance**: Add automated scheduled task to run overdue checks daily
