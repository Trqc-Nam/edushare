import sqlite3
import random
import os

DB_NAME = 'database.db'

def create_and_seed_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. CREATE TABLES
    cursor.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, role TEXT, class_id TEXT);
        CREATE TABLE classes (class_id TEXT PRIMARY KEY, class_name TEXT);
        CREATE TABLE students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, class_id TEXT);
        CREATE TABLE student_books (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, subject TEXT);
        CREATE TABLE library_inventory (subject TEXT PRIMARY KEY, total_qty INTEGER, available_qty INTEGER);
        CREATE TABLE library_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, class_id TEXT, subject TEXT, req_qty INTEGER, approved_qty INTEGER, status TEXT);
        CREATE TABLE out_of_hours_loans (id INTEGER PRIMARY KEY AUTOINCREMENT, class_id TEXT, lender_name TEXT, borrower_name TEXT, subject TEXT, loan_date TEXT, status TEXT);
    """)

    # 2. SEED USERS & CLASSES & INVENTORY
    cursor.executescript("""
        INSERT INTO classes (class_id, class_name) VALUES ('6A', 'Lớp 6A'), ('6B', 'Lớp 6B');
        INSERT INTO users (username, password, role, class_id) VALUES 
            ('admin', 'admin', 'admin', NULL), 
            ('gv6a', 'gv6a', 'teacher', '6A'), 
            ('gv6b', 'gv6b', 'teacher', '6B');
        INSERT INTO library_inventory (subject, total_qty, available_qty) VALUES 
            ('Toán', 20, 20), ('Văn', 20, 20), ('Anh', 20, 20);
    """)

    # 3. SEED 40 STUDENTS (20 FOR 6A, 20 FOR 6B)
    first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng"]
    middle_names = ["Văn", "Thị", "Hoàng", "Minh", "Ngọc", "Gia", "Thanh", "Đức", "Bảo"]
    last_names = ["An", "Bình", "Cường", "Dũng", "Em", "Phong", "Giang", "Hải", "Linh", "Khoa", "Trang", "Vy", "Hân", "Phúc", "Tuấn"]

    subjects = ['Toán', 'Văn', 'Anh']
    
    student_books_data = []
    
    # Tạo 20 học sinh cho 6A
    for i in range(1, 21):
        name = f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}"
        cursor.execute("INSERT INTO students (name, class_id) VALUES (?, ?)", (name, '6A'))
        student_id = cursor.lastrowid
        # Random 0 đến 3 cuốn sách cá nhân cho mỗi em
        owned_subjects = random.sample(subjects, random.randint(0, 3))
        for sub in owned_subjects:
            student_books_data.append((student_id, sub))

    # Tạo 20 học sinh cho 6B
    for i in range(1, 21):
        name = f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}"
        cursor.execute("INSERT INTO students (name, class_id) VALUES (?, ?)", (name, '6B'))
        student_id = cursor.lastrowid
        owned_subjects = random.sample(subjects, random.randint(0, 3))
        for sub in owned_subjects:
            student_books_data.append((student_id, sub))

    # Nạp dữ liệu sách cá nhân
    cursor.executemany("INSERT INTO student_books (student_id, subject) VALUES (?, ?)", student_books_data)

    conn.commit()
    conn.close()
    print(f"[+] Tạo DB thành công! Đã tạo 2 lớp, mỗi lớp 20 học sinh với dữ liệu sách ngẫu nhiên.")

if __name__ == "__main__":
    create_and_seed_db()