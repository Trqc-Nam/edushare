# -*- coding: utf-8 -*-
"""
app.py — EduShare v2.0
Production-ready Streamlit app for textbook sharing management.
Database: database.db (SQLite3) — seeded by seed_data.py
"""
import sqlite3
import pandas as pd
import streamlit as st

# ── Config ─────────────────────────────────────────────────────────────────────
DB_PATH = "database.db"

st.set_page_config(
    page_title="EduShare",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ─────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #000000;
}
.main { background-color: #FFFFFF; }
.block-container { padding-top: 1.5rem; max-width: 1100px; }

/* ── Hide chrome ──────────────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Primary buttons ──────────────────────────────────────────────────── */
div[data-testid="stFormSubmitButton"] > button,
.stButton > button {
    background-color: #6C63FF;
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.6rem;
    font-weight: 600;
    font-size: 0.9rem;
    transition: background-color 0.2s, transform 0.1s;
}
div[data-testid="stFormSubmitButton"] > button:hover,
.stButton > button:hover {
    background-color: #5a52e0;
    transform: translateY(-1px);
}

/* ── Tabs ──────────────────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    background: #F8F8FB;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
[data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #555 !important;
    font-weight: 500;
}
[aria-selected="true"] {
    background-color: #6C63FF !important;
    color: #FFFFFF !important;
}

/* ── Metrics ───────────────────────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: #F8F8FB;
    border: 1px solid #ECECEC;
    border-radius: 12px;
    padding: 1rem;
}
div[data-testid="metric-container"] label {
    color: #888 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #6C63FF !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

/* ── Login card ────────────────────────────────────────────────────────── */
.login-card {
    max-width: 380px;
    margin: 8vh auto 0 auto;
    padding: 2.5rem 2rem;
    border: 1px solid #ECECEC;
    border-radius: 16px;
    background: #FFFFFF;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    text-align: center;
}
.login-card h2 { color: #6C63FF; margin-bottom: 0.25rem; }
.login-card p  { color: #888; font-size: 0.85rem; margin-bottom: 1.5rem; }

/* ── Topbar ────────────────────────────────────────────────────────────── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 0;
    border-bottom: 1px solid #ECECEC;
    margin-bottom: 1.2rem;
}
.topbar-brand { font-size: 1.3rem; font-weight: 700; color: #6C63FF; }
.topbar-user  { font-size: 0.85rem; color: #555; }

/* ── Section headers ──────────────────────────────────────────────────── */
h1, h2, h3 { color: #111; }

/* ── Dataframes ───────────────────────────────────────────────────────── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Status pills ─────────────────────────────────────────────────────── */
.pill-pending  { background:#FFF3CD; color:#856404; padding:2px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }
.pill-approved { background:#D4EDDA; color:#155724; padding:2px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }
.pill-rejected { background:#F8D7DA; color:#721C24; padding:2px 10px; border-radius:12px; font-size:0.8rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def query_df(sql: str, params: tuple = ()) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def execute_sql(sql: str, params: tuple = ()):
    with get_conn() as conn:
        conn.execute(sql, params)
        conn.commit()


def execute_many(sql: str, data: list):
    with get_conn() as conn:
        conn.executemany(sql, data)
        conn.commit()


def fetch_one(sql: str, params: tuple = ()):
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchone()


def fetch_all(sql: str, params: tuple = ()):
    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


# ══════════════════════════════════════════════════════════════════════════════
#  AUTHENTICATION
# ══════════════════════════════════════════════════════════════════════════════
def init_session():
    for key, default in [
        ("logged_in", False),
        ("username", ""),
        ("role", ""),
        ("class_id", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


def render_login():
    st.markdown(
        '<div class="login-card">'
        '<h2> EduShare</h2>'
        '<p>Đăng nhập để tiếp tục</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_l, col_form, col_r = st.columns([1, 1.2, 1])
    with col_form:
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", key="login_user")
            password = st.text_input("Mật khẩu", type="password", key="login_pass")
            submitted = st.form_submit_button("Đăng nhập", use_container_width=True)

            if submitted:
                if not username.strip() or not password.strip():
                    st.error("Vui lòng nhập đầy đủ thông tin.")
                    return

                row = fetch_one(
                    "SELECT username, role, class_id FROM users "
                    "WHERE username = ? AND password = ?",
                    (username.strip(), password.strip()),
                )
                if row:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = row[0]
                    st.session_state["role"] = row[1]
                    st.session_state["class_id"] = row[2]
                    st.rerun()
                else:
                    st.error("Sai tên đăng nhập hoặc mật khẩu.")


def render_topbar():
    col_brand, col_spacer, col_user, col_logout = st.columns([2, 4, 2, 1])
    with col_brand:
        st.markdown(
            '<span style="font-size:1.3rem; font-weight:700; color:#6C63FF;"> EduShare</span>',
            unsafe_allow_html=True,
        )
    with col_user:
        role_label = "Admin" if st.session_state["role"] == "admin" else f"GV {st.session_state['class_id']}"
        st.markdown(
            f'<span style="font-size:0.85rem; color:#555; line-height:2.4rem;">'
            f'Xin chào, <b>{st.session_state["username"]}</b> ({role_label})</span>',
            unsafe_allow_html=True,
        )
    with col_logout:
        if st.button("LOGOUT", key="btn_logout"):
            for k in ["logged_in", "username", "role", "class_id"]:
                st.session_state[k] = False if k == "logged_in" else ""
            st.rerun()

    st.markdown('<hr style="margin:0 0 1rem 0; border:none; border-top:1px solid #ECECEC;">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TEACHER DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def teacher_dashboard(class_id: str):
    st.markdown(f"### Bảng điều hành — Lớp {class_id}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Quản lý danh sách lớp",
        "Quản lý sách & Thư viện",
        "Sắp xếp chỗ ngồi",
        "Quản lý mượn trả ngoài giờ",
    ])

    # ── TAB 1: Student list ────────────────────────────────────────────────────
    with tab1:
        st.markdown("#### Danh sách học sinh")

        df_students = query_df(
            """
            SELECT s.id   AS 'ID',
                   s.name AS 'Họ tên',
                   COALESCE(GROUP_CONCAT(sb.subject, ', '), '—') AS 'Sách sở hữu'
            FROM   students s
            LEFT JOIN student_books sb ON sb.student_id = s.id
            WHERE  s.class_id = ?
            GROUP BY s.id
            ORDER BY s.id
            """,
            (class_id,),
        )
        st.dataframe(df_students, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**Thêm học sinh mới**")
        with st.form(key=f"add_student_{class_id}"):
            fc1, fc2 = st.columns([2, 1])
            new_name = fc1.text_input("Họ tên học sinh", key=f"new_name_{class_id}")
            owned_subjects = fc2.multiselect(
                "Sách sở hữu",
                ["Toán", "Văn", "Anh"],
                key=f"new_subs_{class_id}",
            )
            submitted = st.form_submit_button("Thêm học sinh")
            if submitted:
                if not new_name.strip():
                    st.error("Vui lòng nhập họ tên học sinh.")
                else:
                    with get_conn() as conn:
                        cur = conn.execute(
                            "INSERT INTO students (name, class_id) VALUES (?, ?)",
                            (new_name.strip(), class_id),
                        )
                        student_id = cur.lastrowid
                        if owned_subjects:
                            conn.executemany(
                                "INSERT INTO student_books (student_id, subject) VALUES (?, ?)",
                                [(student_id, sub) for sub in owned_subjects],
                            )
                        conn.commit()
                    st.success(f"Đã thêm: {new_name.strip()}")
                    st.rerun()

    # ── TAB 2: Book management & Library ───────────────────────────────────────
    with tab2:
        st.markdown("####Quản lý sách & Thư viện")

        personal_count_row = fetch_one(
            """
            SELECT COUNT(*) FROM student_books sb
            JOIN students s ON s.id = sb.student_id
            WHERE s.class_id = ?
            """,
            (class_id,),
        )
        personal_count = personal_count_row[0] if personal_count_row else 0

        lib_count_row = fetch_one(
            """
            SELECT COALESCE(SUM(approved_qty), 0) FROM library_requests
            WHERE class_id = ? AND status = 'APPROVED'
            """,
            (class_id,),
        )
        lib_count = lib_count_row[0] if lib_count_row else 0

        mc1, mc2 = st.columns(2)
        mc1.metric("Sách cá nhân trong lớp", personal_count)
        mc2.metric("Sách thư viện đã duyệt", lib_count)

        st.markdown("---")

        # Pending requests
        pending_df = query_df(
            """
            SELECT id AS 'Mã YC', subject AS 'Môn', req_qty AS 'SL yêu cầu',
                   COALESCE(approved_qty, 0) AS 'SL duyệt', status AS 'Trạng thái'
            FROM library_requests
            WHERE class_id = ?
            ORDER BY id DESC
            """,
            (class_id,),
        )
        if not pending_df.empty:
            st.markdown("**📋 Lịch sử yêu cầu mượn thư viện:**")
            st.dataframe(pending_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**📝 Yêu cầu mượn sách thư viện**")
        with st.form(key=f"lib_request_{class_id}"):
            rc1, rc2 = st.columns(2)
            req_subject = rc1.selectbox("Môn học", ["Toán", "Văn", "Anh"], key=f"req_sub_{class_id}")
            req_qty = rc2.number_input("Số lượng", min_value=1, max_value=50, value=1, key=f"req_qty_{class_id}")
            req_submitted = st.form_submit_button("Gửi yêu cầu")
            if req_submitted:
                execute_sql(
                    "INSERT INTO library_requests (class_id, subject, req_qty, approved_qty, status) "
                    "VALUES (?, ?, ?, 0, 'PENDING')",
                    (class_id, req_subject, req_qty),
                )
                st.success(f"Đã gửi yêu cầu mượn {req_qty} cuốn {req_subject}.")
                st.rerun()

    # ── TAB 3: SEATING ALGORITHM ───────────────────────────────────────────────
    with tab3:
        st.markdown("#### 🪑 Sắp xếp chỗ ngồi theo môn")

        seat_subject = st.selectbox(
            "Chọn môn học cần xếp chỗ",
            ["Toán", "Văn", "Anh"],
            key=f"seat_sub_{class_id}",
        )

        if st.button("Tạo sơ đồ", key=f"gen_seat_{class_id}", type="primary"):
            # 1. Students who OWN this subject
            list_has_book = fetch_all(
                """
                SELECT s.id, s.name
                FROM students s
                JOIN student_books sb ON sb.student_id = s.id
                WHERE s.class_id = ? AND sb.subject = ?
                ORDER BY s.id
                """,
                (class_id, seat_subject),
            )

            # 2. Students who do NOT own this subject
            list_no_book = fetch_all(
                """
                SELECT s.id, s.name
                FROM students s
                WHERE s.class_id = ?
                  AND s.id NOT IN (
                      SELECT sb.student_id FROM student_books sb
                      WHERE sb.subject = ?
                  )
                ORDER BY s.id
                """,
                (class_id, seat_subject),
            )

            # 3. Library books available for this subject + class
            lib_row = fetch_one(
                """
                SELECT COALESCE(SUM(approved_qty), 0)
                FROM library_requests
                WHERE class_id = ? AND subject = ? AND status = 'APPROVED'
                """,
                (class_id, seat_subject),
            )
            lib_books_available = lib_row[0] if lib_row else 0

            # 4. Pairing algorithm
            desks = []
            desk_num = 0

            has_idx = 0
            no_idx = 0

            # Phase A: Pair 1 has_book + 1 no_book
            while has_idx < len(list_has_book) and no_idx < len(list_no_book):
                desk_num += 1
                owner = list_has_book[has_idx]
                borrower = list_no_book[no_idx]
                source = f"Cá nhân (Của {owner['name']})"
                desks.append({
                    "Bàn số": desk_num,
                    "Học sinh 1": owner["name"],
                    "Học sinh 2": borrower["name"],
                    "Nguồn sách dùng chung": source,
                })
                has_idx += 1
                no_idx += 1

            # Phase B: Remaining has_book students → pair together (each has own book)
            remaining_has = list_has_book[has_idx:]
            for i in range(0, len(remaining_has), 2):
                desk_num += 1
                s1 = remaining_has[i]
                if i + 1 < len(remaining_has):
                    s2 = remaining_has[i + 1]
                    desks.append({
                        "Bàn số": desk_num,
                        "Học sinh 1": s1["name"],
                        "Học sinh 2": s2["name"],
                        "Nguồn sách dùng chung": "Cá nhân (Cả 2 đều có sách)",
                    })
                else:
                    desks.append({
                        "Bàn số": desk_num,
                        "Học sinh 1": s1["name"],
                        "Học sinh 2": "—",
                        "Nguồn sách dùng chung": "Cá nhân (Có sách)",
                    })

            # Phase C: Remaining no_book students → pair, assign library books
            remaining_no = list_no_book[no_idx:]
            for i in range(0, len(remaining_no), 2):
                desk_num += 1
                s1 = remaining_no[i]
                if i + 1 < len(remaining_no):
                    s2 = remaining_no[i + 1]
                    if lib_books_available > 0:
                        source = "Thư viện trường"
                        lib_books_available -= 1
                    else:
                        source = "THIẾU SÁCH"
                    desks.append({
                        "Bàn số": desk_num,
                        "Học sinh 1": s1["name"],
                        "Học sinh 2": s2["name"],
                        "Nguồn sách dùng chung": source,
                    })
                else:
                    # Odd student left alone
                    if lib_books_available > 0:
                        source = "Thư viện trường"
                        lib_books_available -= 1
                    else:
                        source = "THIẾU SÁCH"
                    desks.append({
                        "Bàn số": desk_num,
                        "Học sinh 1": s1["name"],
                        "Học sinh 2": "—",
                        "Nguồn sách dùng chung": source,
                    })

            # 5. Render
            if desks:
                st.markdown(f"**Kết quả xếp chỗ cho môn {seat_subject}** — "
                            f"Có sách: {len(list_has_book)}, Thiếu sách: {len(list_no_book)}, "
                            f"Sách thư viện khả dụng: {lib_row[0] if lib_row else 0}")
                st.table(pd.DataFrame(desks))

                shortage = sum(1 for d in desks if "THIẾU" in d["Nguồn sách dùng chung"])
                if shortage > 0:
                    st.error(f"Có {shortage} bàn THIẾU SÁCH! Cần yêu cầu thêm sách từ thư viện.")
                else:
                    st.success("Tất cả các bàn đều được cấp đủ sách.")
            else:
                st.info("Không có học sinh nào trong lớp.")

    # ── TAB 4: Out-of-hours loans ──────────────────────────────────────────────
    with tab4:
        st.markdown("#### Quản lý mượn trả ngoài giờ")

        st.markdown("**Ghi nhận cho mượn sách**")
        with st.form(key=f"loan_form_{class_id}"):
            lc1, lc2 = st.columns(2)
            lender_name = lc1.text_input("Người cho mượn", key=f"lender_{class_id}")
            borrower_name = lc2.text_input("Người mượn", key=f"borrower_{class_id}")
            lc3, lc4 = st.columns(2)
            loan_subject = lc3.selectbox("Môn học", ["Toán", "Văn", "Anh"], key=f"loan_sub_{class_id}")
            loan_date = lc4.date_input("Ngày mượn", key=f"loan_date_{class_id}")
            loan_submitted = st.form_submit_button("Ghi nhận")
            if loan_submitted:
                if not lender_name.strip() or not borrower_name.strip():
                    st.error("Vui lòng nhập đầy đủ tên người mượn và người cho mượn.")
                else:
                    execute_sql(
                        "INSERT INTO out_of_hours_loans "
                        "(class_id, lender_name, borrower_name, subject, loan_date, status) "
                        "VALUES (?, ?, ?, ?, ?, 'BORROWED')",
                        (class_id, lender_name.strip(), borrower_name.strip(),
                         loan_subject, str(loan_date)),
                    )
                    st.success("Đã ghi nhận mượn sách thành công.")
                    st.rerun()

        st.markdown("---")
        st.markdown("**Danh sách mượn trả**")

        loans = fetch_all(
            """
            SELECT id, lender_name, borrower_name, subject, loan_date, status
            FROM out_of_hours_loans
            WHERE class_id = ?
            ORDER BY id DESC
            """,
            (class_id,),
        )

        if loans:
            loans_df = query_df(
                """
                SELECT id AS 'Mã', lender_name AS 'Người cho mượn',
                       borrower_name AS 'Người mượn', subject AS 'Môn',
                       loan_date AS 'Ngày mượn', status AS 'Trạng thái'
                FROM out_of_hours_loans
                WHERE class_id = ?
                ORDER BY id DESC
                """,
                (class_id,),
            )
            st.dataframe(loans_df, use_container_width=True, hide_index=True)

            # Return books UI
            borrowed_loans = [ln for ln in loans if ln["status"] == "BORROWED"]
            if borrowed_loans:
                st.markdown("**Xác nhận trả sách:**")
                loan_options = {
                    f"#{ln['id']} — {ln['borrower_name']} mượn {ln['subject']} ({ln['loan_date']})": ln["id"]
                    for ln in borrowed_loans
                }
                selected_loan = st.selectbox(
                    "Chọn phiếu mượn cần trả",
                    list(loan_options.keys()),
                    key=f"return_select_{class_id}",
                )
                if st.button("Xác nhận đã trả", key=f"return_btn_{class_id}"):
                    loan_id = loan_options[selected_loan]
                    execute_sql(
                        "UPDATE out_of_hours_loans SET status = 'RETURNED' WHERE id = ?",
                        (loan_id,),
                    )
                    st.success("Đã cập nhật trạng thái: ĐÃ TRẢ")
                    st.rerun()
        else:
            st.info("Chưa có phiếu mượn nào.")


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def admin_dashboard():
    st.markdown("### 🛠️ Bảng điều hành Admin")

    tab1, tab2, tab3 = st.tabs([
        "Quản lý sách Thư viện",
        "Quản lý cho mượn",
        "Quản lý lớp & Users",
    ])

    # ── TAB 1: Inventory management ────────────────────────────────────────────
    with tab1:
        st.markdown("#### Kho sách Thư viện")

        inv_df = query_df(
            "SELECT subject AS 'Môn học', total_qty AS 'Tổng số', "
            "available_qty AS 'Còn lại' FROM library_inventory"
        )
        st.dataframe(inv_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**Cập nhật / Thêm sách**")
        with st.form(key="inv_update"):
            ic1, ic2, ic3 = st.columns(3)

            existing_subjects = query_df("SELECT subject FROM library_inventory")["subject"].tolist() if not inv_df.empty else []
            all_options = list(set(existing_subjects + ["Toán", "Văn", "Anh"]))
            all_options.sort()

            inv_subject = ic1.selectbox("Môn học", all_options, key="inv_sub")
            inv_total = ic2.number_input("Tổng số", min_value=0, max_value=500, value=20, key="inv_total")
            inv_avail = ic3.number_input("Còn lại", min_value=0, max_value=500, value=20, key="inv_avail")
            inv_submitted = st.form_submit_button("Cập nhật")
            if inv_submitted:
                existing = fetch_one(
                    "SELECT subject FROM library_inventory WHERE subject = ?",
                    (inv_subject,),
                )
                if existing:
                    execute_sql(
                        "UPDATE library_inventory SET total_qty = ?, available_qty = ? WHERE subject = ?",
                        (inv_total, inv_avail, inv_subject),
                    )
                    st.success(f"Đã cập nhật: {inv_subject}")
                else:
                    execute_sql(
                        "INSERT INTO library_inventory (subject, total_qty, available_qty) VALUES (?, ?, ?)",
                        (inv_subject, inv_total, inv_avail),
                    )
                    st.success(f"Đã thêm môn mới: {inv_subject}")
                st.rerun()

    # ── TAB 2: Approve / Reject requests ───────────────────────────────────────
    with tab2:
        st.markdown("#### Quản lý yêu cầu mượn sách")

        all_requests = query_df(
            """
            SELECT lr.id AS 'Mã YC', lr.class_id AS 'Lớp', lr.subject AS 'Môn',
                   lr.req_qty AS 'SL yêu cầu',
                   COALESCE(lr.approved_qty, 0) AS 'SL duyệt',
                   lr.status AS 'Trạng thái'
            FROM library_requests lr
            ORDER BY
                CASE lr.status WHEN 'PENDING' THEN 0 WHEN 'APPROVED' THEN 1 ELSE 2 END,
                lr.id DESC
            """
        )

        if not all_requests.empty:
            st.dataframe(all_requests, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có yêu cầu nào.")

        # Pending requests action
        pending_rows = fetch_all(
            "SELECT id, class_id, subject, req_qty FROM library_requests WHERE status = 'PENDING' ORDER BY id"
        )

        if pending_rows:
            st.markdown("---")
            st.markdown("**⚡ Duyệt / Từ chối yêu cầu**")

            options_map = {
                f"#{r['id']} — Lớp {r['class_id']} — {r['subject']} (SL: {r['req_qty']})": r
                for r in pending_rows
            }
            selected_req_label = st.selectbox(
                "Chọn yêu cầu",
                list(options_map.keys()),
                key="approve_select",
            )
            selected_req = options_map[selected_req_label]

            # Check inventory for this subject
            inv_avail_row = fetch_one(
                "SELECT available_qty FROM library_inventory WHERE subject = ?",
                (selected_req["subject"],),
            )
            max_available = inv_avail_row[0] if inv_avail_row else 0

            approve_qty = st.number_input(
                f"Số lượng duyệt (tối đa còn lại: {max_available})",
                min_value=0,
                max_value=max_available,
                value=min(selected_req["req_qty"], max_available),
                key="approve_qty",
            )

            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button("Duyệt (Approve)", key="btn_approve", type="primary"):
                    if approve_qty <= 0:
                        st.error("Số lượng duyệt phải lớn hơn 0.")
                    else:
                        with get_conn() as conn:
                            conn.execute(
                                "UPDATE library_requests SET approved_qty = ?, status = 'APPROVED' WHERE id = ?",
                                (approve_qty, selected_req["id"]),
                            )
                            conn.execute(
                                "UPDATE library_inventory SET available_qty = available_qty - ? WHERE subject = ?",
                                (approve_qty, selected_req["subject"]),
                            )
                            conn.commit()
                        st.success(f"Đã duyệt {approve_qty} cuốn {selected_req['subject']} cho lớp {selected_req['class_id']}.")
                        st.rerun()
            with ac2:
                if st.button("Từ chối (Reject)", key="btn_reject"):
                    execute_sql(
                        "UPDATE library_requests SET status = 'REJECTED' WHERE id = ?",
                        (selected_req["id"],),
                    )
                    st.success("Đã từ chối yêu cầu.")
                    st.rerun()

    # ── TAB 3: Class & User management ─────────────────────────────────────────
    with tab3:
        st.markdown("#### Quản lý lớp & Tài khoản")

        uc1, uc2 = st.columns(2)
        with uc1:
            st.markdown("**Danh sách lớp:**")
            classes_df = query_df("SELECT class_id AS 'Mã lớp', class_name AS 'Tên lớp' FROM classes")
            st.dataframe(classes_df, use_container_width=True, hide_index=True)
        with uc2:
            st.markdown("**Danh sách tài khoản:**")
            users_df = query_df(
                "SELECT id AS 'ID', username AS 'Username', role AS 'Vai trò', "
                "COALESCE(class_id, '—') AS 'Lớp' FROM users"
            )
            st.dataframe(users_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("** Tạo lớp & Tài khoản GV**")
        with st.form(key="create_class"):
            cc1, cc2 = st.columns(2)
            new_class_id = cc1.text_input("Mã lớp (VD: 7A)", key="new_cls_id")
            new_class_name = cc2.text_input("Tên lớp (VD: Lớp 7A)", key="new_cls_name")
            cc3, cc4 = st.columns(2)
            new_username = cc3.text_input("Username GV", key="new_gv_user")
            new_password = cc4.text_input("Password GV", type="password", key="new_gv_pass")
            cls_submitted = st.form_submit_button("Tạo lớp & Tài khoản")
            if cls_submitted:
                if not all([new_class_id.strip(), new_class_name.strip(),
                            new_username.strip(), new_password.strip()]):
                    st.error("Vui lòng nhập đầy đủ thông tin.")
                else:
                    existing_cls = fetch_one(
                        "SELECT class_id FROM classes WHERE class_id = ?",
                        (new_class_id.strip(),),
                    )
                    existing_usr = fetch_one(
                        "SELECT username FROM users WHERE username = ?",
                        (new_username.strip(),),
                    )
                    if existing_cls:
                        st.error(f"Mã lớp '{new_class_id.strip()}' đã tồn tại.")
                    elif existing_usr:
                        st.error(f"Username '{new_username.strip()}' đã tồn tại.")
                    else:
                        with get_conn() as conn:
                            conn.execute(
                                "INSERT INTO classes (class_id, class_name) VALUES (?, ?)",
                                (new_class_id.strip(), new_class_name.strip()),
                            )
                            conn.execute(
                                "INSERT INTO users (username, password, role, class_id) VALUES (?, ?, 'teacher', ?)",
                                (new_username.strip(), new_password.strip(), new_class_id.strip()),
                            )
                            conn.commit()
                        st.success(f"Đã tạo lớp {new_class_id.strip()} và tài khoản {new_username.strip()}.")
                        st.rerun()

        st.markdown("---")
        st.markdown("**Đổi mật khẩu**")
        with st.form(key="change_pass"):
            all_users = query_df("SELECT username FROM users ORDER BY username")
            if not all_users.empty:
                user_list = all_users["username"].tolist()
            else:
                user_list = []
            pc1, pc2 = st.columns(2)
            target_user = pc1.selectbox("Chọn tài khoản", user_list, key="pw_user")
            new_pw = pc2.text_input("Mật khẩu mới", type="password", key="new_pw")
            pw_submitted = st.form_submit_button("Đổi mật khẩu")
            if pw_submitted:
                if not new_pw.strip():
                    st.error("Vui lòng nhập mật khẩu mới.")
                else:
                    execute_sql(
                        "UPDATE users SET password = ? WHERE username = ?",
                        (new_pw.strip(), target_user),
                    )
                    st.success(f"Đã đổi mật khẩu cho {target_user}.")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════
init_session()

if not st.session_state["logged_in"]:
    render_login()
else:
    render_topbar()
    if st.session_state["role"] == "teacher":
        teacher_dashboard(st.session_state["class_id"])
    elif st.session_state["role"] == "admin":
        admin_dashboard()
    else:
        st.error("Vai trò không hợp lệ.")