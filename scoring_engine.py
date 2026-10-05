import math
import sys
from typing import Dict, Any, List
from database import execute_query

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Định nghĩa 7 nấc thang pháp lý
LEGAL_STAGES_INFO = {
    "L1": {"name": "Chấp thuận Chủ trương đầu tư", "weight": 20, "risk": "RẤT CAO", "desc": "Mới ở giai đoạn ý tưởng/chủ trương, chưa có đất sạch."},
    "L2": {"name": "Phê duyệt Quy hoạch 1/500", "weight": 35, "risk": "CAO", "desc": "Đã duyệt quy hoạch chi tiết, nhưng chưa giao đất và chưa tính tiền sử dụng đất."},
    "L3": {"name": "Quyết định Giao đất / Thuê đất", "weight": 50, "risk": "TRUNG BÌNH - CAO", "desc": "Đã được giao đất nhưng thường nghẽn ở khâu thẩm định giá đất."},
    "L4": {"name": "Hoàn thành Nộp Tiền Sử dụng Đất", "weight": 70, "risk": "TRUNG BÌNH", "desc": "Vượt qua nút thắt rủi ro lớn nhất về nghĩa vụ tài chính với Nhà nước."},
    "L5": {"name": "Được cấp Giấy phép Xây dựng (GPXD)", "weight": 80, "risk": "TRUNG BÌNH - THẤP", "desc": "Được phép triển khai thi công xây dựng công trình hợp pháp."},
    "L6": {"name": "Đủ điều kiện bán nhà hình thành trong tương lai", "weight": 92, "risk": "THẤP", "desc": "Sở Xây dựng đã có văn bản cho phép mở bán huy động vốn hợp pháp."},
    "L7": {"name": "Nghiệm thu hoàn thành / Cấp sổ hồng", "weight": 100, "risk": "RẤT THẤP", "desc": "Dự án hoàn chỉnh, tài sản hiện hữu, thanh khoản cao nhất."}
}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Tính khoảng cách đường chim bay giữa 2 tọa độ GPS (km)"""
    R = 6371.0 # Bán kính Trái Đất (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def evaluate_legal_risk(legal_stage: str, has_land_fee: bool, has_gpxd: bool, eligible_for_sale: bool) -> Dict[str, Any]:
    """Chấm điểm rủi ro Pháp lý (0 - 100)"""
    stage_info = LEGAL_STAGES_INFO.get(legal_stage, LEGAL_STAGES_INFO["L1"])
    score = stage_info["weight"]
    warnings = []

    if legal_stage in ["L1", "L2", "L3"]:
        warnings.append(f"Dự án đang ở giai đoạn {legal_stage} ({stage_info['name']}) - CHƯA ĐỦ ĐIỀU KIỆN HUY ĐỘNG VỐN.")
        warnings.append("Khuyến nghị tín dụng: KHÔNG ĐƯỢC tính dòng tiền bán nhà vào phương án trả nợ trong 12-18 tháng tới.")

    if not has_land_fee and legal_stage not in ["L6", "L7"]:
        score = min(score, 50)
        warnings.append("CẢNH BÁO NÚT THẮT: Chưa có biên lai/chứng nhận nộp tiền sử dụng đất. Đây là nguyên nhân hàng đầu khiến dự án bị 'đóng băng' pháp lý tại VN.")

    if has_gpxd and score < 75:
        score += 10

    if eligible_for_sale:
        score = max(score, 90)

    score = min(100, max(10, score))
    return {
        "score": score,
        "stage_code": legal_stage,
        "stage_name": stage_info["name"],
        "risk_level": stage_info["risk"],
        "description": stage_info["desc"],
        "warnings": warnings
    }

def benchmark_scale(province: str, district: str, total_area_ha: float, total_units: int) -> Dict[str, Any]:
    """Đối chuẩn quy mô so với các dự án cùng địa bàn"""
    query = """
    SELECT id, commercial_name, total_area_ha, total_units, product_type
    FROM projects
    WHERE province = ? AND district = ?
    ORDER BY total_area_ha DESC
    """
    peers = execute_query(query, (province, district))

    all_areas = [p["total_area_ha"] for p in peers]
    total_peer_projects = len(peers)

    # Tìm vị trí xếp hạng
    rank = 1
    for a in all_areas:
        if total_area_ha < a:
            rank += 1

    # Tính thị phần quy mô
    sum_area = sum(all_areas) + (total_area_ha if total_area_ha not in all_areas else 0)
    area_share_pct = round((total_area_ha / max(1, sum_area)) * 100, 1)

    # Đánh giá áp lực cạnh tranh
    if total_peer_projects >= 5 and total_area_ha < 15:
        comp_pressure = "TRUNG BÌNH (Nhiều dự án đối thủ quy mô tương đương)"
        score = 65
    elif total_area_ha >= 100:
        comp_pressure = "CAO VỀ VỐN (Đại dự án đòi hỏi vốn hạ tầng cực lớn)"
        score = 75
    elif rank <= 2:
        comp_pressure = "ƯU THẾ DẪN ĐẦU (Nằm trong top quy mô lớn nhất huyện)"
        score = 85
    else:
        comp_pressure = "BÌNH THƯỜNG"
        score = 70

    return {
        "score": score,
        "rank": rank,
        "total_peers_in_district": total_peer_projects,
        "area_share_pct": area_share_pct,
        "competition_assessment": comp_pressure,
        "top_competitors": peers[:3]
    }

def benchmark_pricing(province: str, district: str, declared_price_m2: float) -> Dict[str, Any]:
    """Đối chuẩn giá bán kỳ vọng của CĐT với mặt bằng thị trường"""
    # Lấy benchmark huyện
    query = "SELECT * FROM district_benchmarks WHERE province = ? AND district = ?"
    bm = execute_query(query, (province, district))

    if bm:
        primary_avg = bm[0]["avg_primary_price_m2"]
        secondary_avg = bm[0]["avg_secondary_price_m2"]
        hist_absorption = bm[0]["historical_absorption_pct"]
    else:
        # Fallback trung bình vùng
        primary_avg = 35.0
        secondary_avg = 28.0
        hist_absorption = 65.0

    gap_primary_pct = round(((declared_price_m2 - primary_avg) / primary_avg) * 100, 1)
    gap_secondary_pct = round(((declared_price_m2 - secondary_avg) / secondary_avg) * 100, 1)

    warnings = []
    if gap_primary_pct > 25.0:
        price_assessment = "ĐỊNH GIÁ QUÁ CAO (OVERPRICED)"
        score = 45
        warnings.append(f"Giá CĐT kỳ vọng ({declared_price_m2} tr/m2) cao hơn +{gap_primary_pct}% so với mặt bằng sơ cấp huyện ({primary_avg} tr/m2).")
        warnings.append("RỦI RO TÍN DỤNG: Dòng tiền bán hàng dự phóng trong phương án phát hành trái phiếu có xác suất hụt thu 30-50% do giá không cạnh tranh.")
    elif gap_primary_pct > 10.0:
        price_assessment = "ĐỊNH GIÁ CAO (PREMIUM)"
        score = 65
        warnings.append(f"Giá cao hơn +{gap_primary_pct}% so với thị trường. Dự án bắt buộc phải có tiện ích vượt trội hoặc thương hiệu mạnh để tiêu thụ được.")
    elif gap_primary_pct >= -10.0:
        price_assessment = "PHÙ HỢP THỊ TRƯỜNG (MARKET-IN-LINE)"
        score = 85
    else:
        price_assessment = "ĐỊNH GIÁ CẠNH TRANH (COMPETITIVE)"
        score = 90

    return {
        "score": score,
        "declared_price": declared_price_m2,
        "district_primary_avg": primary_avg,
        "district_secondary_avg": secondary_avg,
        "gap_primary_pct": gap_primary_pct,
        "gap_secondary_pct": gap_secondary_pct,
        "historical_absorption_pct": hist_absorption,
        "assessment": price_assessment,
        "warnings": warnings
    }

def analyze_location_gis(lat: float, lon: float, province: str) -> Dict[str, Any]:
    """Đo cự ly không gian đến hạ tầng giao thông và KCN trọng điểm"""
    query = "SELECT * FROM infrastructure_nodes"
    nodes = execute_query(query)

    distances = []
    for n in nodes:
        d = haversine_distance(lat, lon, n["latitude"], n["longitude"])
        distances.append({
            "name": n["name"],
            "node_type": n["node_type"],
            "status": n["status"],
            "distance_km": d
        })

    # Sắp xếp theo khoảng cách
    distances.sort(key=lambda x: x["distance_km"])

    # Tìm khoảng cách đến TT TP.HCM (Chợ Bến Thành)
    hcm_node = next((d for d in distances if "Bến Thành" in d["name"]), None)
    hcm_distance_km = hcm_node["distance_km"] if hcm_node else 30.0

    # Tìm cao tốc gần nhất
    expressway = next((d for d in distances if d["node_type"] == "Cao tốc" or d["node_type"] == "Vành đai"), distances[0])

    # Tìm KCN gần nhất
    iz = next((d for d in distances if d["node_type"] in ["Khu công nghiệp", "Cụm KCN - Cảng biển"]), distances[1])

    # Tính điểm vị trí
    score = 70
    if hcm_distance_km <= 20:
        score += 20
    elif hcm_distance_km <= 35:
        score += 10
    elif hcm_distance_km > 60:
        score -= 15

    if expressway["distance_km"] <= 5:
        score += 10
    elif expressway["distance_km"] > 15:
        score -= 5

    score = min(100, max(20, score))

    return {
        "score": score,
        "hcm_distance_km": hcm_distance_km,
        "nearest_expressway": expressway,
        "nearest_iz": iz,
        "nearby_nodes": distances[:4]
    }

def generate_bond_due_diligence_report(
    project_name: str,
    developer: str,
    province: str,
    district: str,
    total_area_ha: float,
    total_units: int,
    legal_stage: str,
    has_land_fee: bool,
    has_gpxd: bool,
    eligible_for_sale: bool,
    declared_price_m2: float,
    lat: float,
    lon: float
) -> Dict[str, Any]:
    """Hàm tổng hợp tạo Báo cáo Thẩm định Độc lập & Chấm điểm Tín dụng Trái phiếu"""

    legal_eval = evaluate_legal_risk(legal_stage, has_land_fee, has_gpxd, eligible_for_sale)
    scale_eval = benchmark_scale(province, district, total_area_ha, total_units)
    price_eval = benchmark_pricing(province, district, declared_price_m2)
    gis_eval = analyze_location_gis(lat, lon, province)

    # Trọng số tính điểm tổng hợp cho tín dụng trái phiếu:
    # Pháp lý: 35% | Giá & Dòng tiền: 25% | Quy mô & Cạnh tranh: 20% | Vị trí GIS: 20%
    composite_score = round(
        legal_eval["score"] * 0.35 +
        price_eval["score"] * 0.25 +
        scale_eval["score"] * 0.20 +
        gis_eval["score"] * 0.20,
        1
    )

    # Xếp hạng tín dụng tương đương (Credit Rating Band)
    if composite_score >= 85:
        rating_band = "AAA - AA"
        risk_class = "RỦI RO RẤT THẤP (Prime)"
        collateral_recom = "Dự án đủ điều kiện làm Tài sản bảo đảm chính; dòng tiền bán hàng an toàn."
    elif composite_score >= 75:
        rating_band = "A"
        risk_class = "RỦI RO THẤP (Investment Grade)"
        collateral_recom = "Dự án có thể làm Tài sản bảo đảm; cần giám sát tài khoản phong tỏa nguồn thu."
    elif composite_score >= 65:
        rating_band = "BBB"
        risk_class = "RỦI RO TRUNG BÌNH (Satisfactory)"
        collateral_recom = "Yêu cầu bổ sung thêm TSĐB bổ trợ độc lập (BĐS thanh khoản cao khác hoặc bảo lãnh ngân hàng)."
    elif composite_score >= 50:
        rating_band = "BB - B"
        risk_class = "RỦI RO ĐẦU CƠ CAO (Speculative)"
        collateral_recom = "KHÔNG CHẤP NHẬN dùng dự án làm TSĐB độc nhất. Bắt buộc có TSĐB độc lập trị giá tối thiểu 150% giá trị trái phiếu."
    else:
        rating_band = "CCC - D"
        risk_class = "RỦI RO VỠ NỢ CỰC CAO (High Default Risk)"
        collateral_recom = "KHUYẾN NGHỊ TỪ CHỐI BẢO LÃNH / XẾP HẠNG KHÔNG ĐẠT ĐIỀU KIỆN ĐẦU TƯ."

    return {
        "project_name": project_name,
        "developer": developer,
        "province": province,
        "district": district,
        "total_area_ha": total_area_ha,
        "total_units": total_units,
        "composite_score": composite_score,
        "rating_band": rating_band,
        "risk_class": risk_class,
        "collateral_recommendation": collateral_recom,
        "legal_eval": legal_eval,
        "scale_eval": scale_eval,
        "price_eval": price_eval,
        "gis_eval": gis_eval
    }

if __name__ == "__main__":
    # Test thử 1 case
    res = generate_bond_due_diligence_report(
        project_name="Dự án Thử nghiệm ABC",
        developer="BĐS Thành Đô",
        province="Long An",
        district="Đức Hòa",
        total_area_ha=30.0,
        total_units=1500,
        legal_stage="L3",
        has_land_fee=False,
        has_gpxd=False,
        eligible_for_sale=False,
        declared_price_m2=38.0,
        lat=10.8876,
        lon=106.5021
    )
    print(f"Test Score: {res['composite_score']} | Rating: {res['rating_band']} | Risk: {res['risk_class']}")
