"""
Seed Data Script: Generates comprehensive benchmark data for
Hành lang TP.HCM (vùng ven) - Long An - Tây Ninh
"""

from database import init_db, get_connection

def seed_all():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Clear old data
    cursor.execute("DELETE FROM legal_milestones")
    cursor.execute("DELETE FROM projects")
    cursor.execute("DELETE FROM infrastructure_nodes")
    cursor.execute("DELETE FROM district_benchmarks")

    # ==========================================
    # 1. DANH SÁCH DỰ ÁN BĐS (MASTER PROJECTS)
    # ==========================================
    projects = [
        # --- LONG AN (Bến Lức, Đức Hòa, Cần Giuộc) ---
        (
            "LA-BL-01", "KĐT Waterpoint", "Khu đô thị An Thạnh - Bến Lức", "Tập đoàn Nam Long & Nishi Nippon",
            "Long An", "Bến Lức", "Xã An Thạnh", "Tỉnh lộ 830, Xã An Thạnh, Huyện Bến Lức, Long An",
            10.6358, 106.4789, 355.0, 10000, "Khu đô thị phức hợp, Nhà phố, Biệt thự, Dinh thự",
            "L6", 1, 1, 1, 52.0, 46.0, 78.5,
            "Mặt tiền Vành Đai 4 (TL830), giáp sông Vàm Cỏ Đông, cách nút giao Cao tốc Trung Lương 3km",
            "Quy mô đại đô thị lớn nhất Bến Lức. Tiến độ tốt nhưng cần nguồn vốn dài hạn lớn.",
            "https://sxd.longan.gov.vn"
        ),
        (
            "LA-DH-01", "Vinhomes Green City (Hậu Nghĩa)", "Khu đô thị mới Hậu Nghĩa - Đức Hòa", "Tập đoàn Vingroup",
            "Long An", "Đức Hòa", "Thị trấn Hậu Nghĩa & Xã Đức Lập Thượng", "Huyện Đức Hòa, Tỉnh Long An",
            10.9023, 106.4255, 197.2, 5170, "Biệt thự, Nhà liền kề, Shophouse, Căn hộ cao tầng",
            "L3", 0, 0, 0, 42.0, 32.0, 60.0,
            "Gần QL N2, kết nối thuận lợi về Hóc Môn, Củ Chi",
            "Dự án hạt nhân của Đức Hòa, tuy nhiên mới ở giai đoạn giải phóng mặt bằng và giao đất, chưa nộp tiền SDĐ.",
            "https://longan.gov.vn"
        ),
        (
            "LA-DH-02", "KĐT Du lịch Sinh thái Cát Tường Phú Sinh", "Khu dân cư Thương mại Dịch vụ Mỹ Hạnh Bắc", "Cát Tường Group",
            "Long An", "Đức Hòa", "Xã Mỹ Hạnh Bắc", "Tỉnh lộ 9, Xã Mỹ Hạnh Bắc, Đức Hòa, Long An",
            10.8876, 106.5021, 79.0, 3800, "Đất nền, Nhà phố liên kế",
            "L7", 1, 1, 1, 24.5, 21.0, 85.0,
            "Tiếp giáp ranh giới Hóc Môn (TP.HCM), cách trung tâm Hóc Môn 10km",
            "Dự án đã hình thành dân cư đông đúc, pháp lý hoàn chỉnh ra sổ hồng từng nền, thanh khoản thứ cấp ổn định.",
            "https://sxd.longan.gov.vn"
        ),
        (
            "LA-CG-01", "The Sol City", "Khu dân cư Thương mại Dịch vụ Tài Lộc", "Thắng Lợi Group",
            "Long An", "Cần Giuộc", "Xã Long Thượng", "Xã Long Thượng, Huyện Cần Giuộc, Long An",
            10.6321, 106.6085, 35.5, 1500, "Đất nền, Nhà phố shophouse",
            "L6", 1, 1, 1, 36.0, 31.5, 72.0,
            "Liền kề Chợ Hưng Long (Bình Chánh, TP.HCM), kết nối Nguyễn Văn Linh qua QL50",
            "Vị trí giáp ranh TP.HCM rất gần, phân khu 1 đã bàn giao, phân khu mở rộng đang xin giấy phép.",
            "https://sxd.longan.gov.vn"
        ),
        (
            "LA-BL-02", "Lago Centro", "Khu dân cư Lương Bình", "Seaside Real Estate & An Nông",
            "Long An", "Bến Lức", "Xã Lương Bình", "Đường ĐT 830, Xã Lương Bình, Bến Lức, Long An",
            10.7423, 106.4521, 13.2, 715, "Đất nền nhà phố liên kế",
            "L6", 1, 1, 1, 21.0, 18.5, 65.0,
            "Nằm trên trục Vành đai 4 kết nối Đức Hòa - Bến Lức, gần KCN Phú An Thạnh",
            "Quy mô trung bình, tiện ích nội khu vừa phải, phụ thuộc vào tốc độ lấp đầy dân cư của KCN lân cận.",
            "https://sxd.longan.gov.vn"
        ),
        (
            "LA-DH-03", "West Lakes Golf & Villas", "Khu nhà ở chuyên gia và biệt thự sân golf Tân Mỹ", "C.S.Q Land & Trần Anh Group",
            "Long An", "Đức Hòa", "Xã Tân Mỹ", "Xã Tân Mỹ, Huyện Đức Hòa, Long An",
            10.9654, 106.4012, 120.0, 537, "Biệt thự nghỉ dưỡng sân golf",
            "L6", 1, 1, 1, 38.0, 32.0, 45.0,
            "Mặt tiền Tỉnh lộ 822, bao bọc quanh sân golf 27 lỗ Tân Mỹ",
            "Sản phẩm kén khách do định vị nghỉ dưỡng cao cấp tại khu vực thiên về công nghiệp.",
            "https://sxd.longan.gov.vn"
        ),
        (
            "LA-CG-02", "T&T City Millennia", "Khu đô thị Long Hậu 267ha", "Tập đoàn T&T",
            "Long An", "Cần Giuộc", "Xã Long Hậu", "Xã Long Hậu, Huyện Cần Giuộc, Long An",
            10.6212, 106.7215, 267.0, 7800, "Đất nền, Nhà phố, Shophouse, Căn hộ",
            "L5", 1, 1, 0, 48.0, 40.0, 58.0,
            "Sát cạnh KCN Long Hậu, KĐT Cảng Hiệp Phước (Nhà Bè, TP.HCM), hưởng lợi từ trục đường Nguyễn Hữu Thọ",
            "Quy mô lớn, tiềm năng kết nối Nam Sài Gòn, tiến độ xây dựng hạ tầng đang tích cực.",
            "https://sxd.longan.gov.vn"
        ),

        # --- TP. HỒ CHÍ MINH (Bình Chánh, Hóc Môn, Củ Chi, Nhà Bè) ---
        (
            "HCM-BC-01", "KĐT Mizuki Park", "Khu đô thị Nguyên Sơn - Bình Chánh", "Tập đoàn Nam Long, Hankyu Hanshin",
            "TP.HCM", "Bình Chánh", "Xã Bình Hưng", "Đại lộ Nguyễn Văn Linh, Bình Hưng, Bình Chánh, TP.HCM",
            10.7221, 106.6645, 26.0, 4600, "Căn hộ biệt lập (Flora), Nhà phố liên kế (Valora)",
            "L7", 1, 1, 1, 56.0, 52.0, 92.0,
            "Mặt tiền Nguyễn Văn Linh, cách Phú Mỹ Hưng 4.5km, kết nối trực tiếp Chợ Lớn qua QL50",
            "Pháp lý chuẩn mực, đã bàn giao nhiều giai đoạn có sổ, thanh khoản rất tốt.",
            "https://construction.hochiminhcity.gov.vn"
        ),
        (
            "HCM-BC-02", "Westgate Bình Chánh", "Khu dân cư Trung tâm Hành chính Tân Túc", "Tập đoàn BĐS An Gia",
            "TP.HCM", "Bình Chánh", "Thị trấn Tân Túc", "Đường Tân Túc, TT. Tân Túc, Bình Chánh, TP.HCM",
            10.6865, 106.5742, 3.1, 2000, "Căn hộ chung cư cao tầng",
            "L7", 1, 1, 1, 45.0, 41.0, 88.0,
            "Ngay trung tâm hành chính Bình Chánh, đối diện bệnh viện huyện, gần cao tốc Trung Lương",
            "Đã bàn giao đón cư dân về ở, tiện ích đầy đủ, tỷ lệ hấp thụ cao.",
            "https://construction.hochiminhcity.gov.vn"
        ),
        (
            "HCM-CC-01", "KDC Bella Vista (Củ Chi - Ranh Long An)", "Khu dân cư Đô thị mới Đức Lập Hạ", "Trần Anh Group",
            "TP.HCM", "Củ Chi", "Xã Thái Mỹ (Giáp Đức Hòa)", "Tỉnh lộ 8, ranh giới Củ Chi và Long An",
            10.9321, 106.4876, 25.0, 1800, "Đất nền nhà phố liên kế",
            "L6", 1, 1, 1, 23.0, 19.5, 68.0,
            "Nằm trên trục Tỉnh lộ 8 nối Củ Chi sang Đức Hòa, gần KCN Tây Bắc Củ Chi",
            "Khu vực dân cư đang hình thành, kết nối tốt sang cụm KCN Đức Hòa 3.",
            "https://construction.hochiminhcity.gov.vn"
        ),
        (
            "HCM-TD-01", "Vinhomes Grand Park (TP. Thủ Đức - Điển hình TP mới)", "Khu dân cư và Công viên Phước Thiện", "Tập đoàn Vingroup",
            "TP.HCM", "TP. Thủ Đức", "Phường Long Bình & Long Thạnh Mỹ", "Đường Nguyễn Xiển, TP. Thủ Đức, TP.HCM",
            10.8456, 106.8378, 271.0, 44000, "Đại đô thị căn hộ, Nhà phố, Dinh thự The Manhattan",
            "L7", 1, 1, 1, 68.0, 60.0, 94.0,
            "Tiếp giáp Vành Đai 3, kết nối Xa lộ Hà Nội và Tuyến Metro số 1 Bến Thành - Suối Tiên",
            "Đại đô thị kiểu mẫu của TP.HCM mới, thanh khoản và mức độ hoàn thiện tiện ích cao nhất vùng.",
            "https://construction.hochiminhcity.gov.vn"
        ),

        # --- TÂY NINH (Trảng Bàng, Gò Dầu, TP. Tây Ninh) ---
        (
            "TN-TN-01", "Golden City Tây Ninh", "Dự án Khu nhà ở Xã hội Hưng Phát", "Công ty CP Đầu tư Thành Phố Vàng",
            "Tây Ninh", "TP. Tây Ninh", "Phường 2", "Đường Yết Kiêu, Phường 2, TP. Tây Ninh",
            11.3124, 106.0987, 3.5, 1652, "Căn hộ NOXH & Thương mại cao tầng",
            "L6", 1, 1, 1, 18.5, 16.0, 75.0,
            "Ngay trung tâm TP. Tây Ninh, mặt tiền đường Yết Kiêu - Phạm Văn Đồng",
            "Dự án chung cư cao tầng đầu tiên tại TP. Tây Ninh, đáp ứng nhu cầu nhà ở trung tâm.",
            "https://sxd.tayninh.gov.vn"
        ),
        (
            "TN-TB-01", "Mai Anh Luxury Trảng Bàng", "Khu dân cư Đô thị mới Phường Gia Lộc", "Mai Anh Real Estate",
            "Tây Ninh", "Trảng Bàng", "Phường Gia Lộc", "Quốc lộ 22, Phường Gia Lộc, TX. Trảng Bàng, Tây Ninh",
            11.0354, 106.3687, 2.1, 120, "Shophouse, Nhà phố thương mại",
            "L6", 1, 1, 1, 32.0, 27.0, 68.0,
            "Mặt tiền QL22, cách ngã tư Trảng Bàng 1.5km, gần tuyến Cao tốc TP.HCM - Mộc Bài tương lai",
            "Quy mô nhỏ nhưng vị trí mặt tiền thương mại sầm uất, phục vụ chuyên gia KCN Trảng Bàng.",
            "https://sxd.tayninh.gov.vn"
        ),
        (
            "TN-GD-01", "KDC Đô thị Phước Đông", "Khu dân cư Dịch vụ Công nghiệp Phước Đông", "Sài Gòn VRG",
            "Tây Ninh", "Gò Dầu", "Xã Phước Đông", "Đường ĐT 782, Xã Phước Đông, Huyện Gò Dầu, Tây Ninh",
            11.1123, 106.3125, 32.0, 1600, "Đất nền, Nhà ở công nhân và chuyên gia",
            "L6", 1, 1, 1, 16.5, 14.0, 82.0,
            "Liền kề trực tiếp KCN Phước Đông 2.190ha (KCN lớn nhất Đông Nam Bộ)",
            "Nhu cầu ở thực và thuê rất cao từ hơn 60.000 công nhân và kỹ sư KCN Phước Đông.",
            "https://sxd.tayninh.gov.vn"
        ),
        (
            "TN-TB-02", "KĐT Phố Mới An Tịnh", "Khu dân cư Thương mại Dịch vụ An Tịnh", "BĐS Tây Ninh Land",
            "Tây Ninh", "Trảng Bàng", "Phường An Tịnh", "Quốc lộ 22, Phường An Tịnh, TX. Trảng Bàng, Tây Ninh",
            11.0211, 106.3891, 10.5, 650, "Đất nền nhà phố liên kế",
            "L5", 1, 1, 0, 22.0, 18.0, 55.0,
            "Gần nút giao QL22 và cổng KCN Trảng Bàng",
            "Đang thi công hạ tầng đường nhựa nội khu, đang xin văn bản mở bán của Sở XD Tây Ninh.",
            "https://sxd.tayninh.gov.vn"
        )
    ]

    for p in projects:
        cursor.execute("""
        INSERT INTO projects (
            id, commercial_name, legal_name, developer, province, district, ward, address,
            latitude, longitude, total_area_ha, total_units, product_type,
            legal_stage, has_land_fee_clearance, has_gpxd, eligible_for_sale,
            primary_price_m2, secondary_price_m2, absorption_rate_pct,
            infrastructure_notes, risk_notes, source_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

    # ==========================================
    # 2. HẠ TẦNG TRỌNG ĐIỂM (INFRASTRUCTURE NODES)
    # ==========================================
    infra = [
        ("INF-01", "Cao tốc TP.HCM - Mộc Bài", "Cao tốc", "Tây Ninh & TP.HCM", "Trảng Bàng & Củ Chi", 11.0421, 106.3542, "Đang chuẩn bị khởi công", "2027", 15.0),
        ("INF-02", "Cao tốc Bến Lức - Long Thành", "Cao tốc", "Long An & TP.HCM", "Bến Lức & Bình Chánh", 10.6489, 106.5211, "Đang thi công hoàn thiện", "2025-2026", 12.0),
        ("INF-03", "Đường Vành Đai 3 TP.HCM", "Vành đai", "TP.HCM & Long An", "Bình Chánh, Củ Chi, Bến Lức", 10.7612, 106.5512, "Đang thi công toàn tuyến", "2026", 10.0),
        ("INF-04", "Đường Vành Đai 4 TP.HCM", "Vành đai", "Long An", "Bến Lức, Đức Hòa, Cần Giuộc", 10.7254, 106.4682, "Đang lập báo cáo nghiên cứu", "2028", 15.0),
        ("INF-05", "KCN Phước Đông (2.190 ha)", "Khu công nghiệp", "Tây Ninh", "Gò Dầu & Trảng Bàng", 11.1154, 106.3087, "Đang hoạt động (KCN lớn nhất)", "Hiện hữu", 15.0),
        ("INF-06", "KCN Thuận Đạo & Phúc Long", "Khu công nghiệp", "Long An", "Bến Lức", 10.6387, 106.5124, "Đang hoạt động lấp đầy 95%", "Hiện hữu", 8.0),
        ("INF-07", "KCN Tân Đức - Tân Đô (1.100 ha)", "Khu công nghiệp", "Long An", "Đức Hòa", 10.7845, 106.4621, "Đang hoạt động lấp đầy 90%", "Hiện hữu", 10.0),
        ("INF-08", "KCN Long Hậu & Cảng Hiệp Phước", "Cụm KCN - Cảng biển", "Long An & TP.HCM", "Cần Giuộc & Nhà Bè", 10.6289, 106.7412, "Đang hoạt động", "Hiện hữu", 10.0),
        ("INF-09", "Nút giao Cao tốc Trung Lương - Bến Lức", "Nút giao cao tốc", "Long An", "Bến Lức", 10.6512, 106.4912, "Đang hoạt động", "Hiện hữu", 8.0),
        ("INF-10", "Trung tâm TP.HCM (Chợ Bến Thành)", "Trung tâm đô thị", "TP.HCM", "Quận 1", 10.7725, 106.6980, "Trung tâm đô thị lõi", "Hiện hữu", 50.0)
    ]

    for item in infra:
        cursor.execute("""
        INSERT INTO infrastructure_nodes (
            id, name, node_type, province, district, latitude, longitude, status, completion_year, impact_radius_km
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)

    # ==========================================
    # 3. MẶT BẰNG ĐỐI CHUẨN ĐỊA PHƯƠNG (BENCHMARKS)
    # ==========================================
    benchmarks = [
        ("Long An", "Bến Lức", 38.5, 30.0, 18500, 68.0, "Nhà phố, Biệt thự đô thị ven sông, Đất nền", "Báo cáo DKRA Q2/2024 & Sở XD Long An"),
        ("Long An", "Đức Hòa", 28.0, 20.5, 24000, 72.0, "Đất nền dự án, Nhà phố liền thổ kề KCN", "Báo cáo DKRA & BĐS.com.vn"),
        ("Long An", "Cần Giuộc", 40.0, 32.5, 14200, 65.0, "Đô thị vệ tinh Nam Sài Gòn, Nhà phố shophouse", "Sở Xây dựng Long An"),
        ("TP.HCM", "Bình Chánh", 48.0, 42.0, 9500, 85.0, "Căn hộ trung cấp, Nhà liền kề hoàn chỉnh", "Sở Xây dựng TP.HCM"),
        ("TP.HCM", "Củ Chi", 25.0, 19.5, 6000, 62.0, "Đất thổ cư phân lô, KDC bán tập trung", "Báo cáo Savills Q2/2024"),
        ("TP.HCM", "TP. Thủ Đức", 72.0, 62.0, 52000, 89.0, "Căn hộ cao cấp, Đại đô thị", "CBRE Vietnam"),
        ("Tây Ninh", "Trảng Bàng", 26.5, 21.0, 4200, 64.0, "Shophouse trục QL22, KDC công nghiệp", "Sở Xây dựng Tây Ninh"),
        ("Tây Ninh", "Gò Dầu", 17.5, 14.0, 3100, 75.0, "Đất nền phụ trợ KCN Phước Đông", "Sở Xây dựng Tây Ninh"),
        ("Tây Ninh", "TP. Tây Ninh", 22.0, 18.5, 2800, 70.0, "Nhà ở thương mại trung tâm, NOXH", "UBND Tỉnh Tây Ninh")
    ]

    for b in benchmarks:
        cursor.execute("""
        INSERT INTO district_benchmarks (
            province, district, avg_primary_price_m2, avg_secondary_price_m2,
            total_pipeline_units, historical_absorption_pct, dominant_product_type, source_reference
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, b)

    conn.commit()
    conn.close()
    print("Seed data loaded successfully!")

if __name__ == "__main__":
    seed_all()
