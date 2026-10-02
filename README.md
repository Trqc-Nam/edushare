# EduShare

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![SQLite](https://img.shields.io/badge/SQLite-Native-green.svg)



🔗 **[TRẢI NGHIỆM LIVE DEMO TẠI ĐÂY](https://edushare-ghgt9petwv2t3qgvc5i7ws.streamlit.app/)**

## 1. Giới thiệu dự án
EduShare là giải pháp kỹ thuật nhằm giải quyết tình trạng thiếu hụt sách giáo khoa tạm thời trong 2-4 tuần đầu năm học. Thay vì photo lậu vi phạm Luật Sở hữu trí tuệ, hệ thống số hóa quy trình quản lý, ghép cặp và luân chuyển sách vật lý có sẵn từ thư viện và cá nhân học sinh. 

Dự án áp dụng tư duy tối ưu hóa tài nguyên hữu hạn và Thỏa mãn ràng buộc để tự động hóa sơ đồ chỗ ngồi, đảm bảo 100% học sinh có sách theo dõi bài giảng

## 2. Tính năng cốt lõi
Hệ thống phân quyền Auth với 2 nhóm người dùng:
* **Admin (Thủ thư):** Quản lý tổng kho sách thư viện, xét duyệt (Approve/Reject) các yêu cầu cấp phát sách từ giáo viên.
* **Giáo viên chủ nhiệm:** 
  * Quản lý sĩ số và sách cá nhân của lớp.
  * Thuật toán tự động xếp sơ đồ bàn đôi: Ưu tiên ghép 1 học sinh có sách cá nhân với 1 học sinh không có sách. Sau đó tự động trích xuất sách thư viện đã được duyệt để ghép cho các bạn còn lại.
  * Quản lý mượn/trả sách về nhà ngoài giờ.

## 3. Tài khoản Demo (Dành cho Ban Giám khảo)
Truy cập vào Live Demo và sử dụng các tài khoản sau để trải nghiệm:
* **Quyền Admin (Thủ thư):** Username: `admin` | Password: `admin`
* **Quyền Giáo viên 6A:** Username: `gv6a` | Password: `gv6a`
* **Quyền Giáo viên 6B:** Username: `gv6b` | Password: `gv6b`

## 4. Hướng dẫn cài đặt và chạy Local
Nếu Ban Giám khảo muốn chạy mã nguồn trên máy cá nhân:

```bash
# 1. Clone kho lưu trữ
git clone https://github.com/Trqc-Nam/edushare.git
cd edushare

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Khởi tạo Cơ sở dữ liệu và Dữ liệu mẫu (Bắt buộc chạy lần đầu)
python seed_data.py

# 4. Khởi chạy ứng dụng
streamlit run app.py
