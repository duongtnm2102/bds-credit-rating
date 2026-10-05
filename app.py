"""
Real Estate Credit Rating & Benchmarking Platform
Hành lang trọng điểm: TP.HCM (vùng ven) - Long An - Tây Ninh
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Đảm bảo đường dẫn import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import execute_query, execute_insert
from scoring_engine import (
    generate_bond_due_diligence_report,
    LEGAL_STAGES_INFO,
    haversine_distance
)
from scrapers.portal_scraper import search_public_project_news, extract_project_claims_from_text

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="BĐS Credit Rating Intelligence | TP.HCM - Long An - Tây Ninh",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho giao diện chuyên nghiệp tài chính/xếp hạng tín dụng
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #4B5563;
        margin-bottom: 20px;
    }
    /* Fix triệt để lỗi Streamlit tự động cắt chữ '...' trên mọi kích thước màn hình */
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        word-break: break-word !important;
        line-height: 1.25 !important;
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        word-break: break-word !important;
    }
    /* Thẻ KPI Responsive hiển thị đầy đủ 100% không bao giờ bị cắt '...' */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 14px;
        margin-bottom: 18px;
    }
    .kpi-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
        white-space: normal !important;
        word-break: break-word !important;
    }
    .kpi-value {
        font-weight: 700;
        line-height: 1.25;
        white-space: normal !important;
        word-break: break-word !important;
        overflow: visible !important;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .risk-badge-high {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .risk-badge-med {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .risk-badge-low {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/real-estate.png", width=64)
st.sidebar.title("BĐS CREDIT RATING")
st.sidebar.caption("Hành lang: TP.HCM - Long An - Tây Ninh | Chi phí: 0 VNĐ")

menu = st.sidebar.radio(
    "CHỨC NĂNG HỆ THỐNG",
    [
        "🎯 Thẩm định & Đối chuẩn Hồ sơ",
        "🗺️ Bản đồ GIS Không gian & Hạ tầng",
        "📊 Thống kê Mặt bằng Địa phương",
        "📁 Cơ sở Dữ liệu Master (Database)",
        "🔍 Trích xuất Tuyên bố Báo chí"
    ]
)

# ==============================================================================
# TAB 1: THẨM ĐỊNH & ĐỐI CHUẨN HỒ SƠ DỰ ÁN MỚI
# ==============================================================================
if menu == "🎯 Thẩm định & Đối chuẩn Hồ sơ":
    st.markdown('<div class="main-header">🎯 THẨM ĐỊNH & ĐỐI CHUẨN DỰ ÁN PHỤC VỤ XẾP HẠNG TÍN DỤNG</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Nhập tên thương mại dự án -> Bấm nút Check để hệ thống tự động kiểm tra CSDL và trích xuất hồ sơ</div>', unsafe_allow_html=True)

    # Khởi tạo session_state: MẶC ĐỊNH LUÔN RỖNG KHI MỞ TRANG HOẶC F5
    if "matched_project" not in st.session_state:
        st.session_state.matched_project = None
    if "project_search_name" not in st.session_state:
        st.session_state.project_search_name = ""
    if "checked_done" not in st.session_state:
        st.session_state.checked_done = False

    # Hàm tìm kiếm thông minh (Fuzzy Search)
    def search_project_by_name(query_name: str):
        if not query_name:
            return None
        projects = execute_query("SELECT * FROM projects")
        q = query_name.lower().strip()
        
        # 1. Khớp chính xác hoặc chuỗi con
        for p in projects:
            c_name = p["commercial_name"].lower()
            l_name = (p["legal_name"] or "").lower()
            if q in c_name or c_name in q or (l_name and (q in l_name or l_name in q)):
                return p
                
        # 2. Khớp theo từ khóa cốt lõi
        import re
        def clean_words(text):
            words = set(re.sub(r'[\(\)\-\,\.\+]', ' ', text.lower()).split())
            return words - {"kđt", "kdc", "dự", "án", "khu", "đô", "thị", "tập", "đoàn"}

        q_words = clean_words(query_name)
        best_p = None
        max_overlap = 0
        for p in projects:
            p_words = clean_words(p["commercial_name"])
            overlap = len(q_words.intersection(p_words))
            if overlap > max_overlap:
                max_overlap = overlap
                best_p = p

        if max_overlap >= 1:
            return best_p
        return None

    # KHUNG NHẬP TÊN DỰ ÁN VÀ NÚT CHECK (MẶC ĐỊNH ĐỂ TRỐNG HOÀN TOÀN)
    st.markdown("### 🔍 Bước 1: Nhập Tên Dự Án Cần Thẩm Định")
    col_input, col_btn = st.columns([4, 1])

    with col_input:
        project_input = st.text_input(
            "Tên thương mại dự án:",
            value=st.session_state.project_search_name,
            placeholder="Ví dụ: Vinhomes Green City Hậu Nghĩa, Eco Retreat Long An, Waterpoint..."
        )

    with col_btn:
        st.write("")
        st.write("")
        btn_check = st.button("🔎 CHECK INFO", type="primary", use_container_width=True)

    # Gợi ý bấm nhanh tên dự án phổ biến
    st.caption("💡 **Gợi ý chọn nhanh:** "
               "[Vinhomes Green City Hậu Nghĩa] | [Eco Retreat Long An] | [Waterpoint] | "
               "[The Sol City] | [Mizuki Park] | [Golden City Tây Ninh]")

    # Xử lý khi nhấn nút Check: Chỉ kiểm tra khi người dùng thực sự bấm nút
    if btn_check:
        if not project_input.strip():
            st.warning("⚠️ Vui lòng nhập tên thương mại dự án trước khi bấm Check!")
            st.session_state.matched_project = None
            st.session_state.checked_done = False
        else:
            matched = search_project_by_name(project_input)
            st.session_state.project_search_name = project_input
            st.session_state.matched_project = matched
            st.session_state.checked_done = True

    p = st.session_state.matched_project

    # NẾU ĐÃ CHECK VÀ TÌM THẤY DỰ ÁN -> HIỂN THỊ FORM GỌN GÀNG (MỤC 1 & MỤC 2)
    if p:
        st.success(f"✅ ĐÃ TÌM THẤY THÔNG TIN DỰ ÁN: **{p['commercial_name']}** (Mã: `{p['id']}`)")

        # HIỂN THỊ TỰ ĐỘNG THÔNG TIN ĐÃ CHECK
        col_in1, col_in2 = st.columns([1, 1])

        with col_in1:
            st.subheader("1. Thông tin Dự án CĐT Tuyên bố")
            project_name = st.text_input("Tên thương mại dự án:", value=p["commercial_name"])
            developer = st.text_input("Chủ đầu tư / Pháp nhân phát hành:", value=p["developer"])

            p_col1, p_col2 = st.columns(2)
            with p_col1:
                province = st.text_input("Tỉnh / Thành phố:", value=p["province"])
            with p_col2:
                district = st.text_input("Quận / Huyện:", value=p["district"])

            s_col1, s_col2 = st.columns(2)
            with s_col1:
                total_area_ha = st.number_input("Quy mô diện tích CĐT khai (ha):", value=float(p["total_area_ha"]), step=1.0)
            with s_col2:
                total_units = st.number_input("Tổng số sản phẩm (căn/nền):", value=int(p["total_units"] or 1000), step=50)

            declared_price = st.number_input("Giá bán CĐT kỳ vọng / chào bán (triệu VNĐ/m²):", value=float(p["primary_price_m2"] or 35.0), step=0.5)

        with col_in2:
            st.subheader("2. Pháp lý Thực tế (Tự động Check)")
            # Tìm index của legal_stage
            stage_keys = list(LEGAL_STAGES_INFO.keys())
            curr_stage_idx = stage_keys.index(p["legal_stage"]) if p["legal_stage"] in stage_keys else 0

            legal_stage = st.selectbox(
                "Nấc thang pháp lý CĐT tự khai:",
                stage_keys,
                index=curr_stage_idx,
                format_func=lambda x: f"{x} - {LEGAL_STAGES_INFO[x]['name']}"
            )

            st.caption(f"ℹ️ {LEGAL_STAGES_INFO[legal_stage]['desc']}")

            st.markdown("**Kiểm tra thực tế giấy tờ bổ trợ:**")
            chk_land_fee = st.checkbox("Đã có Biên lai / Thông báo nộp TIỀN SỬ DỤNG ĐẤT?", value=bool(p["has_land_fee_clearance"]))
            chk_gpxd = st.checkbox("Đã có Giấy phép Xây dựng (GPXD)?", value=bool(p["has_gpxd"]))
            chk_sale = st.checkbox("Có Văn bản đủ điều kiện mở bán của Sở Xây dựng?", value=bool(p["eligible_for_sale"]))

            # Tọa độ địa lý ngầm (không hiển thị ra giao diện theo yêu cầu)
            lat = float(p["latitude"] or 10.75)
            lon = float(p["longitude"] or 106.55)

        st.markdown("---")
        btn_run = st.button("🚀 BẮT ĐẦU ĐỐI CHUẨN ĐỘC LẬP & TẠO BÁO CÁO TÍN DỤNG", type="primary", use_container_width=True)

    elif st.session_state.checked_done and not p:
        st.warning(f"⚠️ Chưa tìm thấy dự án **'{project_input}'** trong CSDL nội bộ. Bạn có thể kiểm tra lại tên gõ đúng hoặc thêm nhanh dự án mới tại Tab **'📁 Cơ sở Dữ liệu Master'**.")
        btn_run = False
    else:
        btn_run = False


    # =========================================================================
    # KHI BẤM NÚT "BẮT ĐẦU ĐỐI CHUẨN": HIỂN THỊ TOÀN BỘ KẾT QUẢ & BẢNG GIÁ MỤC 2
    # =========================================================================
    if btn_run and p:
        with st.spinner("Đang truy vấn cơ sở dữ liệu đối chuẩn và phân tích rủi ro..."):
            report = generate_bond_due_diligence_report(
                project_name=project_name,
                developer=developer,
                province=province,
                district=district,
                total_area_ha=total_area_ha,
                total_units=total_units,
                legal_stage=legal_stage,
                has_land_fee=chk_land_fee,
                has_gpxd=chk_gpxd,
                eligible_for_sale=chk_sale,
                declared_price_m2=declared_price,
                lat=lat,
                lon=lon
            )

        # HIỂN THỊ KẾT QUẢ ĐỐI CHUẨN
        st.success("✅ Đã hoàn thành quá trình thẩm định và đối chuẩn độc lập!")

        # Dashboard Top Metrics (HIỂN THỊ ĐẦY ĐỦ 100% CHỮ TRÊN MỌI KÍCH THƯỚC MÀN HÌNH - KHÔNG BỊ CẮT '...')
        gap_val = report['price_eval']['gap_primary_pct']
        color_gap = "#EF4444" if gap_val > 25 else ("#F59E0B" if gap_val > 10 else "#10B981")

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card" style="border-left: 4px solid #38BDF8;">
                <div class="kpi-label">ĐIỂM RỦI RO DỰ ÁN</div>
                <div class="kpi-value" style="color: #38BDF8; font-size: 26px;">{report['composite_score']} / 100</div>
            </div>
            <div class="kpi-card" style="border-left: 4px solid #F59E0B;">
                <div class="kpi-label">XẾP HẠNG TÍN DỤNG</div>
                <div class="kpi-value" style="color: #F59E0B; font-size: 26px;">{report['rating_band']}</div>
            </div>
            <div class="kpi-card" style="border-left: 4px solid #EF4444;">
                <div class="kpi-label">PHÂN HẠNG RỦI RO</div>
                <div class="kpi-value" style="color: #EF4444; font-size: 16px;">{report['risk_class']}</div>
            </div>
            <div class="kpi-card" style="border-left: 4px solid {color_gap};">
                <div class="kpi-label">CHÊNH LỆCH GIÁ (PRICE GAP)</div>
                <div class="kpi-value" style="color: {color_gap}; font-size: 26px;">{gap_val:+}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Khuyến nghị Tài sản bảo đảm
        st.warning(f"🛡️ **Khuyến nghị Tài sản bảo đảm Trái phiếu:** {report['collateral_recommendation']}")

        # =========================================================================
        # BẢNG 4 & BẢNG GIÁ ĐỐI THỦ: ĐƯỢC ĐƯA VÀO ĐÂY SAU KHI BẤM ĐỐI CHUẨN
        # =========================================================================
        st.markdown("---")
        st.subheader("📋 BẢNG GIÁ CHI TIẾT SẢN PHẨM & ĐỐI CHUẨN ĐỊA PHƯƠNG")

        current_pricing = execute_query("""
            SELECT category, building_group, initial_price, progress_price, loan_price, early_price, avg_price, notes
            FROM project_detailed_pricing
            WHERE project_id = ?
        """, (p["id"],))

        if current_pricing:
            st.markdown(f"**Bảng 4: Giá bán dự kiến sản phẩm văn phòng và thương mại – dịch vụ ({p['commercial_name']})**")
            st.caption("Đơn vị: Triệu đồng/m² | Nguồn: Phương án chào bán CĐT & Hồ sơ tín dụng")
            df_cur = pd.DataFrame(current_pricing)
            df_cur_display = df_cur[[
                "category", "building_group", "initial_price", "progress_price", "loan_price", "early_price", "avg_price"
            ]].rename(columns={
                "category": "Phân loại",
                "building_group": "Nhóm tòa / Phân khu",
                "initial_price": "Giá ban đầu",
                "progress_price": "Theo tiến độ",
                "loan_price": "Vay 70%",
                "early_price": "Trả sớm",
                "avg_price": "Bình quân"
            })
            for col in ["Giá ban đầu", "Theo tiến độ", "Vay 70%", "Trả sớm", "Bình quân"]:
                df_cur_display[col] = df_cur_display[col].map(lambda x: f"{x:,.2f}")

            st.dataframe(df_cur_display, use_container_width=True, hide_index=True)
        else:
            st.info("Dự án này là phân khúc đất nền/nhà phố đơn lẻ, không có cơ cấu tháp cao tầng phức hợp.")

        # Bảng đối chuẩn chi tiết đối thủ cùng địa bàn
        peer_pricing = execute_query("""
            SELECT p.id, p.commercial_name, p.district, dp.category, dp.building_group,
                   dp.initial_price, dp.progress_price, dp.loan_price, dp.early_price, dp.avg_price
            FROM projects p
            JOIN project_detailed_pricing dp ON p.id = dp.project_id
            WHERE p.district = ? AND p.id != ?
            ORDER BY p.commercial_name, dp.category
        """, (p["district"], p["id"]))

        if not peer_pricing:
            peer_pricing = execute_query("""
                SELECT p.id, p.commercial_name, p.district, dp.category, dp.building_group,
                       dp.initial_price, dp.progress_price, dp.loan_price, dp.early_price, dp.avg_price
                FROM projects p
                JOIN project_detailed_pricing dp ON p.id = dp.project_id
                WHERE p.province = ? AND p.id != ?
                ORDER BY p.commercial_name, dp.category
            """, (p["province"], p["id"]))

        if peer_pricing:
            with st.expander(f"🏢 BẢNG GIÁ CHI TIẾT TƯƠNG TỰ CỦA CÁC DỰ ÁN ĐỐI THỦ CÙNG ĐỊA BÀN ({p['district']}, {p['province']})", expanded=True):
                st.caption("Dùng để so sánh trực diện giá Văn phòng & Thương mại - dịch vụ của dự án với các đối thủ cạnh tranh lân cận")
                df_peer = pd.DataFrame(peer_pricing)
                peer_names = df_peer["commercial_name"].unique().tolist()
                for peer_name in peer_names:
                    st.markdown(f"**• Bảng giá đối thủ: {peer_name}**")
                    df_sub = df_peer[df_peer["commercial_name"] == peer_name][[
                        "category", "building_group", "initial_price", "progress_price", "loan_price", "early_price", "avg_price"
                    ]].rename(columns={
                        "category": "Phân loại",
                        "building_group": "Nhóm tòa / Phân khu",
                        "initial_price": "Giá ban đầu",
                        "progress_price": "Theo tiến độ",
                        "loan_price": "Vay 70%",
                        "early_price": "Trả sớm",
                        "avg_price": "Bình quân"
                    })
                    for col in ["Giá ban đầu", "Theo tiến độ", "Vay 70%", "Trả sớm", "Bình quân"]:
                        df_sub[col] = df_sub[col].map(lambda x: f"{x:,.2f}")
                    st.dataframe(df_sub, use_container_width=True, hide_index=True)

        # Khuyến nghị Tài sản bảo đảm
        st.warning(f"🛡️ **Khuyến nghị Tài sản bảo đảm Trái phiếu:** {report['collateral_recommendation']}")

        # Chi tiết 4 Trụ Cột
        st.markdown("### KẾT QUẢ KIỂM CHỨNG THEO 4 TRỤ CỘT")

        tab_leg, tab_scale, tab_pri, tab_gis = st.tabs([
            "1. Pháp lý & Nấc thang Phê duyệt",
            "2. Đối chuẩn Quy mô & Cạnh tranh",
            "3. Kiểm chứng Định giá Chi tiết",
            "4. Phân tích GIS & Kết nối Hạ tầng"
        ])

        with tab_leg:
            le = report["legal_eval"]
            st.write(f"**Giai đoạn Pháp lý hiện tại:** `{le['stage_code']}` - **{le['stage_name']}**")
            st.progress(le["score"] / 100.0)
            st.caption(f"Điểm số Pháp lý: {le['score']}/100 | Mức độ rủi ro: **{le['risk_level']}**")

            if le["warnings"]:
                for w in le["warnings"]:
                    st.error(f"⚠️ {w}")
            else:
                st.success("Pháp lý dự án cơ bản hoàn chỉnh, đã có văn bản huy động vốn hợp pháp.")

        with tab_scale:
            sc = report["scale_eval"]
            c_sc1, c_sc2 = st.columns([1, 1])
            with c_sc1:
                st.write(f"• **Vị thế quy mô tại {district}**: Xếp hạng **#{sc['rank']}** trên tổng số {sc['total_peers_in_district']} dự án đang triển khai.")
                st.write(f"• **Tỷ trọng nguồn cung**: Chiếm khoảng **{sc['area_share_pct']}%** tổng quỹ đất dự án tại huyện.")
                st.write(f"• **Đánh giá áp lực cạnh tranh**: {sc['competition_assessment']}")
            with c_sc2:
                st.write("**Top 3 dự án lớn nhất cùng địa bàn để đối chiếu:**")
                if sc["top_competitors"]:
                    for idx, p_comp in enumerate(sc["top_competitors"], 1):
                        st.markdown(f"{idx}. **{p_comp['commercial_name']}** — Quy mô: `{p_comp['total_area_ha']} ha` | Sản phẩm: `{p_comp['product_type']}`")
                else:
                    st.info("Chưa có dự án cạnh tranh lớn cùng phân khúc trong cơ sở dữ liệu huyện này.")

        with tab_pri:
            pe = report["price_eval"]
            p_c1, p_c2 = st.columns([1, 1])
            with p_c1:
                st.write(f"• **Giá CĐT kỳ vọng**: `{pe['declared_price']} triệu/m²`")
                st.write(f"• **Giá sơ cấp trung bình huyện**: `{pe['district_primary_avg']} triệu/m²`")
                st.write(f"• **Giá thứ cấp thị trường**: `{pe['district_secondary_avg']} triệu/m²`")
                st.write(f"• **Đánh giá định vị**: **{pe['assessment']}**")

                if pe["warnings"]:
                    for pw in pe["warnings"]:
                        st.error(f"🚨 {pw}")
                else:
                    st.success("Mức giá CĐT chào bán phù hợp với mặt bằng thị trường địa phương.")

            with p_c2:
                # Biểu đồ so sánh giá
                fig = go.Figure(data=[
                    go.Bar(
                        x=["Giá Thứ cấp Dân sinh", "Giá Sơ cấp Huyện", "Giá CĐT Kỳ vọng"],
                        y=[pe["district_secondary_avg"], pe["district_primary_avg"], pe["declared_price"]],
                        marker_color=["#94A3B8", "#3B82F6", "#EF4444" if pe["gap_primary_pct"] > 20 else "#10B981"]
                    )
                ])
                fig.update_layout(title="So sánh Giá (triệu VNĐ/m²)", height=280, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)

            # Bổ sung đối chuẩn chính sách thanh toán chi tiết
            if current_pricing:
                st.markdown("#### 💡 Phân tích Cơ cấu Chiết khấu Theo Chính Sách Bán Hàng:")
                df_curr_p = pd.DataFrame(current_pricing)
                avg_init = df_curr_p["initial_price"].mean()
                avg_prog = df_curr_p["progress_price"].mean()
                avg_early = df_curr_p["early_price"].mean()
                discount_prog = ((avg_init - avg_prog) / avg_init) * 100
                discount_early = ((avg_init - avg_early) / avg_init) * 100

                st.write(f"- **Chính sách Theo tiến độ**: Chiết khấu trung bình **{discount_prog:.1f}%** so với giá ban đầu niêm yết.")
                st.write(f"- **Chính sách Trả sớm (Thanh toán 95%)**: Chiết khấu trung bình lên đến **{discount_early:.1f}%** (thực chất là chi phí tài chính ngầm CĐT chấp nhận trả để hút vốn sớm).")
                st.write(f"- **Chính sách Vay 70% (HTLS 0%)**: Giữ nguyên giá ban đầu nhưng CĐT phải chịu chi phí lãi suất thay cho người mua trong thời gian ân hạn.")

        with tab_gis:
            ge = report["gis_eval"]
            st.write(f"• **Khoảng cách đến TT TP.HCM (Chợ Bến Thành)**: `{ge['hcm_distance_km']} km`")
            st.write(f"• **Tuyến Cao tốc / Vành đai gần nhất**: `{ge['nearest_expressway']['name']}` — Cách `{ge['nearest_expressway']['distance_km']} km` (Trạng thái: *{ge['nearest_expressway']['status']}*)")
            st.write(f"• **Cụm Khu công nghiệp gần nhất**: `{ge['nearest_iz']['name']}` — Cách `{ge['nearest_iz']['distance_km']} km`")

            st.write("**Các mốc hạ tầng lân cận:**")
            for node in ge["nearby_nodes"]:
                st.caption(f"- {node['name']} ({node['node_type']}): cách **{node['distance_km']} km**")

        # XUẤT CREDIT MEMO
        st.markdown("---")
        memo_text = f"""================================================================================
BÁO CÁO THẨM ĐỊNH & ĐỐI CHUẨN TÍN DỤNG DỰ ÁN BẤT ĐỘNG SẢN (CREDIT MEMO)
Tên dự án: {project_name} | Chủ đầu tư: {developer}
Địa bàn: {district}, {province}
================================================================================

1. KẾT LUẬN XẾP HẠNG & RỦI RO
- Điểm đánh giá: {report['composite_score']}/100
- Xếp hạng tín dụng tương đương: {report['rating_band']} ({report['risk_class']})
- Khuyến nghị Tài sản bảo đảm: {report['collateral_recommendation']}

2. ĐỐI CHUẨN PHÁP LÝ (LEGAL CHECKLIST)
- Nấc thang phê duyệt: {report['legal_eval']['stage_code']} ({report['legal_eval']['stage_name']})
- Đã nộp tiền sử dụng đất: {'CÓ' if chk_land_fee else 'CHƯA (RỦI RO LỚN)'}
- Giấy phép xây dựng: {'CÓ' if chk_gpxd else 'CHƯA'}
- Đủ điều kiện mở bán: {'CÓ' if chk_sale else 'CHƯA'}

3. ĐỐI CHUẨN QUY MÔ & CẠNH TRANH
- Quy mô: {total_area_ha} ha | Tổng số sản phẩm: {total_units} căn
- Xếp hạng quy mô tại {district}: #{report['scale_eval']['rank']} / {report['scale_eval']['total_peers_in_district']} dự án
- Thị phần nguồn cung dự kiến: {report['scale_eval']['area_share_pct']}%

4. ĐỐI CHUẨN GIÁ BÁN & THANH KHOẢN (PRICE GAP)
- Giá CĐT kỳ vọng: {declared_price} triệu/m2
- Giá sơ cấp trung bình huyện: {report['price_eval']['district_primary_avg']} triệu/m2 (Lệch: {report['price_eval']['gap_primary_pct']:+}%)
- Giá thứ cấp trung bình: {report['price_eval']['district_secondary_avg']} triệu/m2
- Đánh giá: {report['price_eval']['assessment']}

5. KẾT NỐI HẠ TẦNG & VỊ TRÍ GIS
- Khoảng cách đến TT TP.HCM: {report['gis_eval']['hcm_distance_km']} km
- Trục giao thông huyết mạch gần nhất: {report['gis_eval']['nearest_expressway']['name']} ({report['gis_eval']['nearest_expressway']['distance_km']} km)
- KCN hỗ trợ nhu cầu thực: {report['gis_eval']['nearest_iz']['name']} ({report['gis_eval']['nearest_iz']['distance_km']} km)
================================================================================
"""
        st.download_button(
            label="📥 Tải xuống Biên bản Thẩm định Tín dụng (Credit Memo .txt)",
            data=memo_text,
            file_name=f"Credit_Memo_{project_name.replace(' ', '_')}.txt",
            mime="text/plain"
        )

# ==============================================================================
# TAB 2: BẢN ĐỒ GIS KHÔNG GIAN & HẠ TẦNG
# ==============================================================================
elif menu == "🗺️ Bản đồ GIS Không gian & Hạ tầng":
    st.markdown('<div class="main-header">🗺️ BẢN ĐỒ GIS HÀNH LANG TP.HCM - LONG AN - TÂY NINH</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Trực quan hóa vị trí dự án, hành lang giao thông (Vành Đai 3, Cao tốc Mộc Bài) và các cụm Khu công nghiệp lớn</div>', unsafe_allow_html=True)

    projects = execute_query("SELECT * FROM projects")
    infra_nodes = execute_query("SELECT * FROM infrastructure_nodes")

    # Bản đồ trung tâm: Vùng Bến Lức - Bình Chánh (10.75, 106.55)
    m = folium.Map(location=[10.85, 106.45], zoom_start=10, tiles="CartoDB positron")

    # Vẽ các mốc hạ tầng
    for node in infra_nodes:
        icon_color = "blue"
        if "Cao tốc" in node["node_type"] or "Vành đai" in node["node_type"]:
            icon_color = "red"
        elif "Khu công nghiệp" in node["node_type"]:
            icon_color = "purple"

        folium.Marker(
            location=[node["latitude"], node["longitude"]],
            popup=f"<b>{node['name']}</b><br>Loại: {node['node_type']}<br>Trạng thái: {node['status']}",
            tooltip=f"{node['name']} ({node['node_type']})",
            icon=folium.Icon(color=icon_color, icon="info-sign")
        ).add_to(m)

    # Vẽ các dự án BĐS
    for p in projects:
        # Màu theo pháp lý
        if p["legal_stage"] in ["L7", "L6"]:
            color = "green"
        elif p["legal_stage"] in ["L4", "L5"]:
            color = "orange"
        else:
            color = "darkred"

        folium.CircleMarker(
            location=[p["latitude"], p["longitude"]],
            radius=max(6, min(22, p["total_area_ha"] / 15)), # Kích thước vòng tròn tỉ lệ theo diện tích ha
            popup=(
                f"<b>{p['commercial_name']}</b><br>"
                f"CĐT: {p['developer']}<br>"
                f"Quy mô: <b>{p['total_area_ha']} ha</b> ({p['total_units'] or 0} căn)<br>"
                f"Pháp lý: <b>{p['legal_stage']}</b><br>"
                f"Giá sơ cấp: <b>{p['primary_price_m2']} tr/m2</b>"
            ),
            tooltip=f"{p['commercial_name']} ({p['total_area_ha']} ha)",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(m)

    st_folium(m, width="100%", height=600)

    # Chú thích bản đồ
    st.markdown("""
    **Chú thích Bản đồ:**
    - 🟢 **Vòng tròn Xanh lá**: Dự án Pháp lý an toàn (L6: Đủ điều kiện mở bán, L7: Đã có sổ).
    - 🟠 **Vòng tròn Cam**: Dự án Pháp lý trung bình (L4: Đã nộp tiền đất, L5: Có GPXD).
    - 🔴 **Vòng tròn Đỏ đậm**: Dự án Pháp lý rủi ro cao (L1-L3: Mới duyệt chủ trương / 1/500, chưa nộp tiền đất).
    - 📍 **Điểm ghim Đỏ**: Tuyến Cao tốc (TP.HCM - Mộc Bài, Bến Lức - Long Thành) & Tuyến Vành đai 3/4.
    - 📍 **Điểm ghim Tím**: Cụm Khu công nghiệp lớn (KCN Phước Đông 2.190ha, KCN Thuận Đạo, Tân Đức...).
    """)

# ==============================================================================
# TAB 3: THỐNG KÊ MẶT BẰNG ĐỊA PHƯƠNG
# ==============================================================================
elif menu == "📊 Thống kê Mặt bằng Địa phương":
    st.markdown('<div class="main-header">📊 MẶT BẰNG ĐỐI CHUẨN GIÁ & NGUỒN CUNG ĐỊA PHƯƠNG</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Dữ liệu nguồn cung và giá giao dịch chuẩn hóa từ Sở Xây dựng và Báo cáo nghiên cứu thị trường DKRA/CBRE (0 VNĐ)</div>', unsafe_allow_html=True)

    benchmarks = execute_query("SELECT * FROM district_benchmarks")
    df_bm = pd.DataFrame(benchmarks)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("So sánh Giá Sơ cấp & Thứ cấp theo Địa bàn (triệu VNĐ/m²)")
        fig_bar = px.bar(
            df_bm,
            x="district",
            y=["avg_primary_price_m2", "avg_secondary_price_m2"],
            barmode="group",
            color_discrete_sequence=["#2563EB", "#94A3B8"],
            labels={"value": "Giá (triệu VNĐ/m²)", "district": "Quận / Huyện", "variable": "Loại giá"},
            title="Biên độ chênh lệch giữa Giá sơ cấp CĐT rao và Giá thứ cấp giao dịch thật"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        st.subheader("Tổng Nguồn cung Dự án Dự kiến (Căn/Nền)")
        fig_pipe = px.pie(
            df_bm,
            values="total_pipeline_units",
            names="district",
            title="Thị phần nguồn cung căn/nền phân bổ theo Quận/Huyện",
            hole=0.4
        )
        st.plotly_chart(fig_pipe, use_container_width=True)

    st.markdown("### Bảng Số liệu Đối chuẩn Chi tiết:")
    st.dataframe(
        df_bm[[
            "province", "district", "avg_primary_price_m2", "avg_secondary_price_m2",
            "total_pipeline_units", "historical_absorption_pct", "dominant_product_type", "source_reference"
        ]],
        use_container_width=True
    )

# ==============================================================================
# TAB 4: CƠ SỞ DỮ LIỆU MASTER (DATABASE)
# ==============================================================================
elif menu == "📁 Cơ sở Dữ liệu Master (Database)":
    st.markdown('<div class="main-header">📁 MASTER DATABASE DỰ ÁN HÀNH LANG TP.HCM - LONG AN - TÂY NINH</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cơ sở dữ liệu lưu trữ nội bộ (SQLite) - Quản lý tập trung các dự án đã được chuẩn hóa</div>', unsafe_allow_html=True)

    filter_prov = st.selectbox("Lọc theo Tỉnh/Thành:", ["Tất cả", "Long An", "TP.HCM", "Tây Ninh"])

    if filter_prov == "Tất cả":
        query = "SELECT * FROM projects ORDER BY total_area_ha DESC"
        data = execute_query(query)
    else:
        query = "SELECT * FROM projects WHERE province = ? ORDER BY total_area_ha DESC"
        data = execute_query(query, (filter_prov,))

    df_p = pd.DataFrame(data)

    st.write(f"Tổng số dự án quản lý: **{len(df_p)}** dự án")

    # Display table
    show_cols = [
        "id", "commercial_name", "legal_name", "developer", "province", "district",
        "total_area_ha", "total_units", "legal_stage", "primary_price_m2", "secondary_price_m2", "product_type"
    ]
    st.dataframe(df_p[show_cols], use_container_width=True)

    # Nút xuất Excel / CSV miễn phí
    csv = df_p.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📥 Tải toàn bộ Database về file CSV/Excel",
        data=csv,
        file_name="Master_Database_BDS_Credit_Rating.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("➕ Thêm nhanh Dự án mới vào CSDL:")
    with st.expander("Mở form thêm dự án mới"):
        with st.form("add_project_form"):
            new_id = st.text_input("Mã dự án (vd: LA-BL-99):")
            new_com = st.text_input("Tên thương mại:")
            new_leg = st.text_input("Tên pháp lý:")
            new_dev = st.text_input("Chủ đầu tư:")
            c1, c2 = st.columns(2)
            with c1:
                new_prov = st.selectbox("Tỉnh:", ["Long An", "TP.HCM", "Tây Ninh"])
                new_area = st.number_input("Diện tích (ha):", value=10.0)
                new_stage = st.selectbox("Pháp lý:", ["L1", "L2", "L3", "L4", "L5", "L6", "L7"])
            with c2:
                new_dist = st.text_input("Huyện/Quận:")
                new_units = st.number_input("Số căn:", value=500)
                new_price = st.number_input("Giá sơ cấp (tr/m2):", value=25.0)

            btn_save = st.form_submit_button("Lưu Dự án vào CSDL")
            if btn_save:
                execute_insert("""
                INSERT INTO projects (
                    id, commercial_name, legal_name, developer, province, district,
                    total_area_ha, total_units, legal_stage, primary_price_m2
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (new_id, new_com, new_leg, new_dev, new_prov, new_dist, new_area, new_units, new_stage, new_price))
                st.success("Đã thêm dự án mới vào CSDL!")
                st.rerun()

# ==============================================================================
# TAB 5: TRÍCH XUẤT TUYÊN BỐ BÁO CHÍ
# ==============================================================================
elif menu == "🔍 Trích xuất Tuyên bố Báo chí":
    st.markdown('<div class="main-header">🔍 TỰ ĐỘNG BÓC TÁCH TUYÊN BỐ CĐT TỪ BÁO CHÍ & TRUYỀN THÔNG</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tránh vi phạm bảo mật file nội bộ: Khai thác trực tiếp các bài báo PR công khai của CĐT trên mạng</div>', unsafe_allow_html=True)

    text_input = st.text_area(
        "Dán đoạn văn bản bài báo PR hoặc bài giới thiệu dự án vào đây:",
        value="Dự án Waterpoint Nam Long tại Bến Lức, Long An có quy mô 355ha, cung cấp hơn 10000 căn nhà phố biệt thự ven sông với mức giá dự kiến từ 52 triệu/m2.",
        height=150
    )

    if st.button("🔎 Bóc tách Thông số CĐT Tuyên bố", type="primary"):
        claims = extract_project_claims_from_text(text_input)

        st.markdown("### Kết quả Phát hiện Tự động:")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Quy mô phát hiện:", f"{claims['detected_area_ha']} ha" if claims['detected_area_ha'] else "Không tìm thấy")
        with c2:
            st.metric("Số lượng sản phẩm:", f"{claims['detected_units']:,} căn/nền" if claims['detected_units'] else "Không tìm thấy")
        with c3:
            st.metric("Giá bán kỳ vọng:", f"{claims['detected_price_m2']} triệu/m²" if claims['detected_price_m2'] else "Không tìm thấy")

        st.info("💡 Bạn có thể lấy trực tiếp các con số này đưa sang tab **'🎯 Thẩm định & Đối chuẩn Hồ sơ'** để chạy chấm điểm tín dụng ngay mà không cần dùng đến tài liệu nội bộ.")
