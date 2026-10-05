# Nền Tảng Thẩm Định & Đối Chuẩn Bất Động Sản Phục Vụ Xếp Hạng Tín Dụng Trái Phiếu
**Hành lang kinh tế trọng điểm:** TP.HCM (Vùng ven) – Long An – Tây Ninh  
**Chi phí dữ liệu & bản quyền:** 0 VNĐ (Hoàn toàn Miễn phí 100%)

---

## 1. Giới thiệu Tổng quan
Nền tảng được xây dựng dành riêng cho **chuyên viên thẩm định tín dụng trái phiếu doanh nghiệp BĐS**, giải quyết triệt để 2 bài toán lớn:
1. **Xác thực tuyên bố "Dự án là nhất":** Bóc tách và đối chuẩn độc lập quy mô, vị trí, nấc thang pháp lý và giá bán thực tế của dự án so với toàn bộ nguồn cung cùng địa bàn.
2. **Tuyệt đối an toàn bảo mật (Compliance):** Không yêu cầu tải lên bất kỳ tài liệu nội bộ (PDF/Teaser) nào của doanh nghiệp, loại bỏ hoàn toàn rủi ro vi phạm thỏa thuận bảo mật (NDA).

---

## 2. Cấu trúc Thư mục

```text
bds_credit_rating_platform/
│
├── database.py             # Schema CSDL SQLite & module truy vấn
├── real_estate_credit.db   # Cơ sở dữ liệu SQLite cục bộ (lưu trữ trên máy)
├── seed_data.py            # Dữ liệu đối chuẩn gốc các dự án & hạ tầng 3 tỉnh
├── scoring_engine.py       # Bộ máy chấm điểm tín dụng 4 trụ cột & Credit Rating
│
├── scrapers/
│   └── portal_scraper.py   # Module bóc tách tuyên bố CĐT từ báo chí công khai
│
├── app.py                  # Giao diện Web tương tác Streamlit
├── run_platform.bat        # File kích hoạt 1-click trên Windows
└── README.md               # Hướng dẫn chi tiết
```

---

## 3. Hướng dẫn Kích hoạt và Sử dụng

### Cách 1: Khởi động 1-click
- Nhấp đúp chuột vào file `run_platform.bat` trong thư mục `bds_credit_rating_platform`.
- Trình duyệt web sẽ tự động mở tại địa chỉ `http://localhost:8501`.

### Cách 2: Khởi động bằng dòng lệnh (Terminal / PowerShell)
```powershell
cd c:\Users\Dat\Desktop\Workspace1\bds_credit_rating_platform
python -m streamlit run app.py
```

---

## 4. Các Tính năng Chính trên Giao diện

1. **🎯 Thẩm định & Đối chuẩn Hồ sơ (Due Diligence Tool)**:
   - Nhập 4-5 thông số CĐT chào bán (Quy mô ha, số căn, giá kỳ vọng, tình trạng nộp tiền đất/GPXD).
   - Hệ thống tự động tính điểm tín dụng (0-100), xếp hạng (AAA đến CCC), kiểm tra nấc thang pháp lý và cảnh báo rủi ro lệch giá (Price Gap Index).
   - Tải về **Biên bản Thẩm định Tín dụng (Credit Memo)** định dạng văn bản phục vụ báo cáo nội bộ.

2. **🗺️ Bản đồ GIS Không gian & Hạ tầng (Interactive Map)**:
   - Trực quan hóa toàn bộ dự án trên nền bản đồ mở OpenStreetMap.
   - Tô màu dự án theo cấp độ rủi ro pháp lý (Xanh: L6-L7 an toàn; Cam: L4-L5 trung bình; Đỏ: L1-L3 rủi ro cao).
   - Ghim các tuyến giao thông trọng điểm (Cao tốc Mộc Bài, Bến Lức - Long Thành, Vành Đai 3, Vành Đai 4) và các cụm KCN lớn.

3. **📊 Thống kê Mặt bằng Địa phương (Market Benchmarks)**:
   - So sánh biên độ giá sơ cấp vs thứ cấp theo từng huyện (Bến Lức, Đức Hòa, Cần Giuộc, Bình Chánh, Trảng Bàng, Gò Dầu...).
   - Biểu đồ phân bổ nguồn cung pipeline.

4. **📁 Cơ sở Dữ liệu Master (Database)**:
   - Tra cứu, lọc theo tỉnh/huyện, thêm mới dự án trực tiếp vào SQLite.
   - Nút xuất dữ liệu ra file **Excel / CSV** miễn phí.

5. **🔍 Trích xuất Tuyên bố Báo chí**:
   - Dán link hoặc đoạn văn bài báo PR của CĐT $\rightarrow$ Hệ thống tự nhận diện quy mô diện tích, số căn và giá bán dự kiến.

---

## 5. Hướng dẫn Cập nhật Dữ liệu Mới Miễn phí 100%

Định kỳ mỗi tháng hoặc mỗi quý, bạn của bạn có thể truy cập các website sau để lấy danh sách dự án mở bán mới cập nhật vào hệ thống:
- **Sở Xây dựng Long An**: `https://sxd.longan.gov.vn` (Mục *Nhà ở và thị trường BĐS*)
- **Sở Xây dựng TP.HCM**: `https://construction.hochiminhcity.gov.vn` (Mục *Dự án phát triển nhà ở*)
- **Sở Xây dựng Tây Ninh**: `https://sxd.tayninh.gov.vn`
- **Báo cáo Thị trường Quý**: Tải file PDF miễn phí từ DKRA Group (`https://dkra.vn`)
