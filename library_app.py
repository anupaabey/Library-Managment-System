import tkinter as tk
from tkinter import ttk, messagebox, font
import mysql.connector
from mysql.connector import Error
import datetime
import hashlib
import re

# ─────────────────────────────────────────────
#  COLOUR PALETTE & THEME
# ─────────────────────────────────────────────
BG_DARK      = "#0F1923"
BG_CARD      = "#162030"
BG_SIDEBAR   = "#0A1218"
ACCENT       = "#00D4AA"
ACCENT_DARK  = "#00A882"
TEXT_PRIMARY = "#E8F0F7"
TEXT_MUTED   = "#6B8BA4"
TEXT_LIGHT   = "#A8C0D0"
DANGER       = "#FF4757"
WARNING      = "#FFA502"
SUCCESS      = "#2ED573"
BORDER       = "#1E3045"
ROW_ODD      = "#131E2B"
ROW_EVEN     = "#0F1923"

# ─────────────────────────────────────────────
#  DATABASE MANAGER
# ─────────────────────────────────────────────
class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",        # ← change to your MySQL password
                database="library_db"
            )
            self.create_tables()
        except Error as e:
            messagebox.showerror("Database Error",
                f"Could not connect to MySQL.\n\n{e}\n\n"
                "Please ensure MySQL is running and update credentials in library_app.py")

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                isbn        VARCHAR(20)  UNIQUE NOT NULL,
                title       VARCHAR(200) NOT NULL,
                author      VARCHAR(100) NOT NULL,
                genre       VARCHAR(50),
                year        INT,
                copies      INT DEFAULT 1,
                available   INT DEFAULT 1,
                added_date  DATE DEFAULT (CURDATE())
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                member_id    VARCHAR(20) UNIQUE NOT NULL,
                name         VARCHAR(100) NOT NULL,
                email        VARCHAR(100) UNIQUE NOT NULL,
                phone        VARCHAR(20),
                joined_date  DATE DEFAULT (CURDATE()),
                status       ENUM('Active','Suspended') DEFAULT 'Active'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrowings (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                book_id       INT NOT NULL,
                member_id     INT NOT NULL,
                borrow_date   DATE DEFAULT (CURDATE()),
                due_date      DATE,
                return_date   DATE,
                status        ENUM('Borrowed','Returned','Overdue') DEFAULT 'Borrowed',
                FOREIGN KEY (book_id)   REFERENCES books(id),
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id       INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(64) NOT NULL
            )
        """)
        # Default admin: admin / admin123
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
            INSERT IGNORE INTO admins (username, password) VALUES (%s, %s)
        """, ("admin", pw))
        self.connection.commit()
        cursor.close()

    def execute(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Error as e:
            messagebox.showerror("DB Error", str(e))
            return None

    def fetchall(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
            return []

    def fetchone(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            return None


# ─────────────────────────────────────────────
#  LOGIN WINDOW
# ─────────────────────────────────────────────
class LoginWindow:
    def __init__(self, root, db, on_success):
        self.root = root
        self.db   = db
        self.on_success = on_success
        self.build_ui()

    def build_ui(self):
        self.frame = tk.Frame(self.root, bg=BG_DARK)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo area
        tk.Label(self.frame, text="📚", font=("Segoe UI Emoji", 52),
                 bg=BG_DARK, fg=ACCENT).pack(pady=(0, 5))
        tk.Label(self.frame, text="LibraryOS", font=("Georgia", 30, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack()
        tk.Label(self.frame, text="Management System",
                 font=("Courier New", 11), bg=BG_DARK, fg=TEXT_MUTED).pack(pady=(0, 30))

        card = tk.Frame(self.frame, bg=BG_CARD, padx=40, pady=35,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack()

        tk.Label(card, text="Admin Login", font=("Georgia", 16, "bold"),
                 bg=BG_CARD, fg=TEXT_PRIMARY).pack(pady=(0, 20))

        tk.Label(card, text="USERNAME", font=("Courier New", 9),
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        self.user_entry = self._input(card)
        self.user_entry.pack(fill="x", pady=(3, 12))

        tk.Label(card, text="PASSWORD", font=("Courier New", 9),
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        self.pass_entry = self._input(card, show="●")
        self.pass_entry.pack(fill="x", pady=(3, 20))

        btn = tk.Button(card, text="LOGIN  →",
                        font=("Courier New", 11, "bold"),
                        bg=ACCENT, fg=BG_DARK, bd=0, pady=10,
                        activebackground=ACCENT_DARK, cursor="hand2",
                        command=self.login)
        btn.pack(fill="x")

        self.root.bind("<Return>", lambda e: self.login())

    def _input(self, parent, show=""):
        e = tk.Entry(parent, font=("Courier New", 12),
                     bg=BG_DARK, fg=TEXT_PRIMARY, bd=0,
                     insertbackground=ACCENT,
                     highlightbackground=BORDER,
                     highlightthickness=1,
                     show=show)
        e.configure(width=28)
        return e

    def login(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()
        if not u or not p:
            messagebox.showwarning("Login", "Please enter username and password.")
            return
        pw_hash = hashlib.sha256(p.encode()).hexdigest()
        row = self.db.fetchone(
            "SELECT id FROM admins WHERE username=%s AND password=%s", (u, pw_hash))
        if row:
            self.frame.destroy()
            self.on_success()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class LibraryApp:
    def __init__(self, root, db):
        self.root    = root
        self.db      = db
        self.current = None
        self.build_layout()
        self.show_dashboard()

    # ── Layout skeleton ──────────────────────
    def build_layout(self):
        self.root.configure(bg=BG_DARK)

        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Main area
        self.main = tk.Frame(self.root, bg=BG_DARK)
        self.main.pack(side="left", fill="both", expand=True)

        self._build_sidebar()

    def _build_sidebar(self):
        # Branding
        brand = tk.Frame(self.sidebar, bg=BG_SIDEBAR, pady=20)
        brand.pack(fill="x")
        tk.Label(brand, text="📚 LibraryOS",
                 font=("Georgia", 15, "bold"),
                 bg=BG_SIDEBAR, fg=ACCENT).pack()
        tk.Label(brand, text="v1.0  •  Admin Panel",
                 font=("Courier New", 8),
                 bg=BG_SIDEBAR, fg=TEXT_MUTED).pack()

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=15)

        # Nav items
        nav = [
            ("🏠", "Dashboard",    self.show_dashboard),
            ("📖", "Books",        self.show_books),
            ("👥", "Members",      self.show_members),
            ("🔄", "Borrow/Return",self.show_borrowings),
            ("🔍", "Search",       self.show_search),
        ]
        self.nav_buttons = []
        for icon, label, cmd in nav:
            btn = tk.Button(
                self.sidebar,
                text=f"  {icon}  {label}",
                font=("Segoe UI", 11),
                bg=BG_SIDEBAR, fg=TEXT_LIGHT,
                activebackground=BG_CARD,
                activeforeground=ACCENT,
                bd=0, anchor="w", padx=10, pady=12,
                cursor="hand2",
                command=cmd
            )
            btn.pack(fill="x")
            self.nav_buttons.append((btn, label))

        # Bottom: logout
        tk.Frame(self.sidebar, bg=BG_SIDEBAR).pack(expand=True, fill="y")
        tk.Button(self.sidebar, text="  ⏻  Logout",
                  font=("Segoe UI", 10),
                  bg=BG_SIDEBAR, fg=DANGER,
                  activebackground=BG_CARD, bd=0,
                  anchor="w", padx=10, pady=10,
                  cursor="hand2",
                  command=self.logout).pack(fill="x")

    def _highlight_nav(self, active_label):
        for btn, label in self.nav_buttons:
            if label == active_label:
                btn.configure(bg=BG_CARD, fg=ACCENT)
            else:
                btn.configure(bg=BG_SIDEBAR, fg=TEXT_LIGHT)

    def _clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _page_header(self, title, subtitle=""):
        hdr = tk.Frame(self.main, bg=BG_DARK, pady=20, padx=30)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, font=("Georgia", 22, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w")
        if subtitle:
            tk.Label(hdr, text=subtitle, font=("Segoe UI", 10),
                     bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w")
        tk.Frame(self.main, bg=ACCENT, height=2).pack(fill="x", padx=30)

    # ── Treeview helper ──────────────────────
    def _make_tree(self, parent, columns, heights=300):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=BG_CARD,
                        foreground=TEXT_PRIMARY,
                        rowheight=28,
                        fieldbackground=BG_CARD,
                        borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Custom.Treeview.Heading",
                        background=BG_SIDEBAR,
                        foreground=ACCENT,
                        font=("Courier New", 9, "bold"),
                        borderwidth=0)
        style.map("Custom.Treeview",
                  background=[("selected", ACCENT_DARK)],
                  foreground=[("selected", BG_DARK)])

        frame = tk.Frame(parent, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=30, pady=10)

        tree = ttk.Treeview(frame, columns=columns, show="headings",
                            style="Custom.Treeview")
        vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        return tree

    def _accent_btn(self, parent, text, cmd, color=ACCENT):
        return tk.Button(parent, text=text,
                         font=("Courier New", 10, "bold"),
                         bg=color, fg=BG_DARK, bd=0,
                         padx=15, pady=7, cursor="hand2",
                         activebackground=ACCENT_DARK,
                         command=cmd)

    # ══════════════════════════════════════════
    #  DASHBOARD
    # ══════════════════════════════════════════
    def show_dashboard(self):
        self._clear_main()
        self._highlight_nav("Dashboard")
        self._page_header("Dashboard", "Library at a glance")

        stats_frame = tk.Frame(self.main, bg=BG_DARK, pady=20, padx=30)
        stats_frame.pack(fill="x")

        stats = [
            ("Total Books",    self._count("SELECT COUNT(*) FROM books"),           "📖", ACCENT),
            ("Members",        self._count("SELECT COUNT(*) FROM members"),          "👥", "#3498DB"),
            ("Borrowed",       self._count("SELECT COUNT(*) FROM borrowings WHERE status='Borrowed'"), "🔄", WARNING),
            ("Overdue",        self._count("SELECT COUNT(*) FROM borrowings WHERE status='Overdue'"),  "⚠️", DANGER),
        ]
        for i, (label, val, icon, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=BG_CARD, padx=20, pady=18,
                            highlightbackground=color, highlightthickness=1)
            card.grid(row=0, column=i, padx=10, sticky="ew")
            stats_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=icon, font=("Segoe UI Emoji", 22),
                     bg=BG_CARD).pack(anchor="w")
            tk.Label(card, text=str(val), font=("Georgia", 28, "bold"),
                     bg=BG_CARD, fg=color).pack(anchor="w")
            tk.Label(card, text=label, font=("Segoe UI", 10),
                     bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")

        # Recent activity
        tk.Label(self.main, text="Recent Borrowings",
                 font=("Georgia", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY,
                 padx=30).pack(anchor="w", pady=(15, 0))

        cols = ("Book Title", "Member", "Borrow Date", "Due Date", "Status")
        tree = self._make_tree(self.main, cols)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        rows = self.db.fetchall("""
            SELECT b.title, m.name, br.borrow_date, br.due_date, br.status
            FROM borrowings br
            JOIN books b   ON br.book_id   = b.id
            JOIN members m ON br.member_id = m.id
            ORDER BY br.borrow_date DESC LIMIT 10
        """)
        for row in rows:
            tag = "overdue" if row[4] == "Overdue" else ("returned" if row[4] == "Returned" else "")
            tree.insert("", "end", values=row, tags=(tag,))
        tree.tag_configure("overdue",  foreground=DANGER)
        tree.tag_configure("returned", foreground=SUCCESS)

    def _count(self, query):
        r = self.db.fetchone(query)
        return r[0] if r else 0

    # ══════════════════════════════════════════
    #  BOOKS
    # ══════════════════════════════════════════
    def show_books(self):
        self._clear_main()
        self._highlight_nav("Books")
        self._page_header("Book Catalogue", "Manage your library collection")

        btn_bar = tk.Frame(self.main, bg=BG_DARK, padx=30, pady=10)
        btn_bar.pack(fill="x")
        self._accent_btn(btn_bar, "+ Add Book",    self.add_book_dialog).pack(side="left", padx=(0,8))
        self._accent_btn(btn_bar, "✎ Edit",        self.edit_book_dialog, "#3498DB").pack(side="left", padx=(0,8))
        self._accent_btn(btn_bar, "✕ Remove",      self.remove_book, DANGER).pack(side="left")

        cols = ("ID", "ISBN", "Title", "Author", "Genre", "Year", "Copies", "Available")
        self.book_tree = self._make_tree(self.main, cols)
        widths = [40, 120, 220, 150, 100, 60, 60, 70]
        for col, w in zip(cols, widths):
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=w, anchor="center" if col not in ("Title","Author") else "w")

        self._load_books()

    def _load_books(self, search=""):
        for row in self.book_tree.get_children():
            self.book_tree.delete(row)
        if search:
            rows = self.db.fetchall("""
                SELECT id,isbn,title,author,genre,year,copies,available
                FROM books WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s
            """, (f"%{search}%",)*3)
        else:
            rows = self.db.fetchall(
                "SELECT id,isbn,title,author,genre,year,copies,available FROM books ORDER BY title")
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.book_tree.insert("", "end", values=row, tags=(tag,))
        self.book_tree.tag_configure("even", background=ROW_EVEN)
        self.book_tree.tag_configure("odd",  background=ROW_ODD)

    def add_book_dialog(self):
        self._book_form("Add New Book", None)

    def edit_book_dialog(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showwarning("Edit", "Please select a book.")
            return
        vals = self.book_tree.item(sel[0])["values"]
        self._book_form("Edit Book", vals)

    def _book_form(self, title, prefill):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG_DARK)
        win.geometry("420x480")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=title, font=("Georgia", 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY, pady=15).pack()

        fields = ["ISBN", "Title", "Author", "Genre", "Year", "Total Copies"]
        entries = {}
        for f in fields:
            tk.Label(win, text=f.upper(), font=("Courier New", 9),
                     bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", padx=30)
            e = tk.Entry(win, font=("Segoe UI", 11),
                         bg=BG_CARD, fg=TEXT_PRIMARY, bd=0,
                         insertbackground=ACCENT,
                         highlightbackground=BORDER, highlightthickness=1)
            e.pack(fill="x", padx=30, pady=(2, 10), ipady=5)
            entries[f] = e

        if prefill:
            vals = prefill
            entries["ISBN"].insert(0, vals[1])
            entries["Title"].insert(0, vals[2])
            entries["Author"].insert(0, vals[3])
            entries["Genre"].insert(0, vals[4] or "")
            entries["Year"].insert(0, vals[5] or "")
            entries["Total Copies"].insert(0, vals[6])

        def save():
            isbn   = entries["ISBN"].get().strip()
            title_ = entries["Title"].get().strip()
            author = entries["Author"].get().strip()
            genre  = entries["Genre"].get().strip()
            year   = entries["Year"].get().strip()
            copies = entries["Total Copies"].get().strip()
            if not all([isbn, title_, author]):
                messagebox.showwarning("Validation", "ISBN, Title and Author are required.")
                return
            if prefill:
                self.db.execute("""
                    UPDATE books SET isbn=%s,title=%s,author=%s,genre=%s,year=%s,copies=%s
                    WHERE id=%s
                """, (isbn, title_, author, genre or None, year or None, copies or 1, prefill[0]))
            else:
                self.db.execute("""
                    INSERT INTO books (isbn,title,author,genre,year,copies,available)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (isbn, title_, author, genre or None, year or None, copies or 1, copies or 1))
            win.destroy()
            self._load_books()

        self._accent_btn(win, "💾  Save Book", save).pack(pady=10)

    def remove_book(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showwarning("Remove", "Please select a book.")
            return
        vals = self.book_tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Remove '{vals[2]}'?"):
            self.db.execute("DELETE FROM books WHERE id=%s", (vals[0],))
            self._load_books()

    # ══════════════════════════════════════════
    #  MEMBERS
    # ══════════════════════════════════════════
    def show_members(self):
        self._clear_main()
        self._highlight_nav("Members")
        self._page_header("Members", "Registered library members")

        btn_bar = tk.Frame(self.main, bg=BG_DARK, padx=30, pady=10)
        btn_bar.pack(fill="x")
        self._accent_btn(btn_bar, "+ Register Member", self.add_member_dialog).pack(side="left", padx=(0,8))
        self._accent_btn(btn_bar, "✎ Edit", self.edit_member_dialog, "#3498DB").pack(side="left", padx=(0,8))
        self._accent_btn(btn_bar, "✕ Remove", self.remove_member, DANGER).pack(side="left")

        cols = ("ID", "Member ID", "Name", "Email", "Phone", "Joined", "Status")
        self.member_tree = self._make_tree(self.main, cols)
        widths = [40, 100, 160, 180, 110, 100, 80]
        for col, w in zip(cols, widths):
            self.member_tree.heading(col, text=col)
            self.member_tree.column(col, width=w)

        self._load_members()

    def _load_members(self):
        for row in self.member_tree.get_children():
            self.member_tree.delete(row)
        rows = self.db.fetchall(
            "SELECT id,member_id,name,email,phone,joined_date,status FROM members ORDER BY name")
        for i, row in enumerate(rows):
            tag = "suspended" if row[6] == "Suspended" else ("even" if i % 2 == 0 else "odd")
            self.member_tree.insert("", "end", values=row, tags=(tag,))
        self.member_tree.tag_configure("even",      background=ROW_EVEN)
        self.member_tree.tag_configure("odd",       background=ROW_ODD)
        self.member_tree.tag_configure("suspended", foreground=DANGER)

    def add_member_dialog(self):
        self._member_form("Register Member", None)

    def edit_member_dialog(self):
        sel = self.member_tree.selection()
        if not sel:
            messagebox.showwarning("Edit", "Please select a member.")
            return
        self._member_form("Edit Member", self.member_tree.item(sel[0])["values"])

    def _member_form(self, title, prefill):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG_DARK)
        win.geometry("400x450")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=title, font=("Georgia", 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY, pady=15).pack()

        fields = ["Member ID", "Full Name", "Email", "Phone"]
        entries = {}
        for f in fields:
            tk.Label(win, text=f.upper(), font=("Courier New", 9),
                     bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", padx=30)
            e = tk.Entry(win, font=("Segoe UI", 11),
                         bg=BG_CARD, fg=TEXT_PRIMARY, bd=0,
                         insertbackground=ACCENT,
                         highlightbackground=BORDER, highlightthickness=1)
            e.pack(fill="x", padx=30, pady=(2, 10), ipady=5)
            entries[f] = e

        # Status dropdown
        tk.Label(win, text="STATUS", font=("Courier New", 9),
                 bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", padx=30)
        status_var = tk.StringVar(value="Active")
        status_cb = ttk.Combobox(win, textvariable=status_var,
                                 values=["Active", "Suspended"],
                                 state="readonly", font=("Segoe UI", 11))
        status_cb.pack(fill="x", padx=30, pady=(2, 10))

        if prefill:
            entries["Member ID"].insert(0, prefill[1])
            entries["Full Name"].insert(0, prefill[2])
            entries["Email"].insert(0, prefill[3])
            entries["Phone"].insert(0, prefill[4] or "")
            status_var.set(prefill[6])

        def save():
            mid   = entries["Member ID"].get().strip()
            name  = entries["Full Name"].get().strip()
            email = entries["Email"].get().strip()
            phone = entries["Phone"].get().strip()
            if not all([mid, name, email]):
                messagebox.showwarning("Validation", "Member ID, Name and Email are required.")
                return
            if prefill:
                self.db.execute("""
                    UPDATE members SET member_id=%s,name=%s,email=%s,phone=%s,status=%s
                    WHERE id=%s
                """, (mid, name, email, phone or None, status_var.get(), prefill[0]))
            else:
                self.db.execute("""
                    INSERT INTO members (member_id,name,email,phone,status)
                    VALUES (%s,%s,%s,%s,%s)
                """, (mid, name, email, phone or None, status_var.get()))
            win.destroy()
            self._load_members()

        self._accent_btn(win, "💾  Save Member", save).pack(pady=10)

    def remove_member(self):
        sel = self.member_tree.selection()
        if not sel:
            messagebox.showwarning("Remove", "Please select a member.")
            return
        vals = self.member_tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Remove member '{vals[2]}'?"):
            self.db.execute("DELETE FROM members WHERE id=%s", (vals[0],))
            self._load_members()

    # ══════════════════════════════════════════
    #  BORROW / RETURN
    # ══════════════════════════════════════════
    def show_borrowings(self):
        self._clear_main()
        self._highlight_nav("Borrow/Return")
        self._page_header("Borrow & Return", "Track book loans")

        btn_bar = tk.Frame(self.main, bg=BG_DARK, padx=30, pady=10)
        btn_bar.pack(fill="x")
        self._accent_btn(btn_bar, "📤  Issue Book", self.issue_book_dialog).pack(side="left", padx=(0,8))
        self._accent_btn(btn_bar, "📥  Return Book", self.return_book, "#2ED573").pack(side="left", padx=(0,8))
        self._accent_btn(btn_bar, "🔄  Refresh",    self._load_borrowings, TEXT_MUTED).pack(side="left")

        cols = ("ID", "Book Title", "Member", "Borrow Date", "Due Date", "Return Date", "Status")
        self.borrow_tree = self._make_tree(self.main, cols)
        widths = [40, 200, 150, 100, 100, 100, 80]
        for col, w in zip(cols, widths):
            self.borrow_tree.heading(col, text=col)
            self.borrow_tree.column(col, width=w)

        self._load_borrowings()

    def _load_borrowings(self):
        # Update overdue status
        self.db.execute("""
            UPDATE borrowings SET status='Overdue'
            WHERE status='Borrowed' AND due_date < CURDATE()
        """)
        for row in self.borrow_tree.get_children():
            self.borrow_tree.delete(row)
        rows = self.db.fetchall("""
            SELECT br.id, b.title, m.name,
                   br.borrow_date, br.due_date, br.return_date, br.status
            FROM borrowings br
            JOIN books b   ON br.book_id   = b.id
            JOIN members m ON br.member_id = m.id
            ORDER BY br.borrow_date DESC
        """)
        for row in rows:
            tag = {"Overdue":"overdue","Returned":"returned"}.get(row[6], "")
            self.borrow_tree.insert("", "end", values=row, tags=(tag,))
        self.borrow_tree.tag_configure("overdue",  foreground=DANGER)
        self.borrow_tree.tag_configure("returned", foreground=SUCCESS)

    def issue_book_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Issue Book")
        win.configure(bg=BG_DARK)
        win.geometry("420x360")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Issue Book", font=("Georgia", 16, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY, pady=15).pack()

        # Book selector
        tk.Label(win, text="SELECT BOOK", font=("Courier New", 9),
                 bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", padx=30)
        books = self.db.fetchall("SELECT id, title FROM books WHERE available > 0")
        book_options = [f"{b[0]} – {b[1]}" for b in books]
        book_var = tk.StringVar()
        book_cb = ttk.Combobox(win, textvariable=book_var,
                               values=book_options, state="readonly",
                               font=("Segoe UI", 10), width=45)
        book_cb.pack(fill="x", padx=30, pady=(3,12))

        # Member selector
        tk.Label(win, text="SELECT MEMBER", font=("Courier New", 9),
                 bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", padx=30)
        members = self.db.fetchall("SELECT id, name FROM members WHERE status='Active'")
        mem_options = [f"{m[0]} – {m[1]}" for m in members]
        mem_var = tk.StringVar()
        mem_cb = ttk.Combobox(win, textvariable=mem_var,
                              values=mem_options, state="readonly",
                              font=("Segoe UI", 10), width=45)
        mem_cb.pack(fill="x", padx=30, pady=(3,12))

        # Due date
        tk.Label(win, text="DUE DATE (YYYY-MM-DD)", font=("Courier New", 9),
                 bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", padx=30)
        default_due = (datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        due_entry = tk.Entry(win, font=("Segoe UI", 11),
                             bg=BG_CARD, fg=TEXT_PRIMARY, bd=0,
                             insertbackground=ACCENT,
                             highlightbackground=BORDER, highlightthickness=1)
        due_entry.insert(0, default_due)
        due_entry.pack(fill="x", padx=30, pady=(3,15), ipady=5)

        def issue():
            if not book_var.get() or not mem_var.get():
                messagebox.showwarning("Issue", "Please select a book and member.")
                return
            book_id = int(book_var.get().split(" – ")[0])
            mem_id  = int(mem_var.get().split(" – ")[0])
            due     = due_entry.get().strip()
            self.db.execute("""
                INSERT INTO borrowings (book_id, member_id, due_date, status)
                VALUES (%s, %s, %s, 'Borrowed')
            """, (book_id, mem_id, due))
            self.db.execute("UPDATE books SET available = available - 1 WHERE id=%s", (book_id,))
            win.destroy()
            self._load_borrowings()
            messagebox.showinfo("Issued", "Book issued successfully!")

        self._accent_btn(win, "📤  Issue Book", issue).pack(pady=5)

    def return_book(self):
        sel = self.borrow_tree.selection()
        if not sel:
            messagebox.showwarning("Return", "Please select a borrowing record.")
            return
        vals = self.borrow_tree.item(sel[0])["values"]
        if vals[6] == "Returned":
            messagebox.showinfo("Return", "This book has already been returned.")
            return
        if messagebox.askyesno("Confirm", f"Return '{vals[1]}' from {vals[2]}?"):
            self.db.execute("""
                UPDATE borrowings SET status='Returned', return_date=CURDATE()
                WHERE id=%s
            """, (vals[0],))
            # Get book_id and increment available
            row = self.db.fetchone("SELECT book_id FROM borrowings WHERE id=%s", (vals[0],))
            if row:
                self.db.execute("UPDATE books SET available = available + 1 WHERE id=%s", (row[0],))
            self._load_borrowings()
            messagebox.showinfo("Returned", "Book returned successfully!")

    # ══════════════════════════════════════════
    #  SEARCH
    # ══════════════════════════════════════════
    def show_search(self):
        self._clear_main()
        self._highlight_nav("Search")
        self._page_header("Search", "Find books and members")

        search_frame = tk.Frame(self.main, bg=BG_DARK, padx=30, pady=15)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="Search Books",
                 font=("Georgia", 13, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=(0,5))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=("Segoe UI", 12),
                                bg=BG_CARD, fg=TEXT_PRIMARY, bd=0,
                                insertbackground=ACCENT,
                                highlightbackground=BORDER, highlightthickness=1,
                                width=40)
        search_entry.grid(row=1, column=0, ipady=6, padx=(0,10))
        self._accent_btn(search_frame, "🔍  Search",
                         lambda: self._do_search()).grid(row=1, column=1)

        cols = ("ID", "ISBN", "Title", "Author", "Genre", "Year", "Available")
        self.search_tree = self._make_tree(self.main, cols)
        for col in cols:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=130)

    def _do_search(self):
        q = self.search_var.get().strip()
        for row in self.search_tree.get_children():
            self.search_tree.delete(row)
        if not q:
            return
        rows = self.db.fetchall("""
            SELECT id,isbn,title,author,genre,year,available
            FROM books WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s OR genre LIKE %s
        """, (f"%{q}%",)*4)
        for row in rows:
            self.search_tree.insert("", "end", values=row)
        if not rows:
            messagebox.showinfo("Search", "No books found matching your query.")

    # ── Logout ───────────────────────────────
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            for w in self.root.winfo_children():
                w.destroy()
            app_start(self.root, self.db)


# ─────────────────────────────────────────────
#  BOOTSTRAP
# ─────────────────────────────────────────────
def app_start(root, db):
    LoginWindow(root, db, lambda: LibraryApp(root, db))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("LibraryOS – Management System")
    root.geometry("1150x720")
    root.minsize(1000, 620)
    root.configure(bg=BG_DARK)

    db = DatabaseManager()
    app_start(root, db)
    root.mainloop()
