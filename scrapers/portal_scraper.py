"""
Portal Scraper & Public Data Collector Module
Khai thác dữ liệu miễn phí từ các cổng thông tin công khai:
- Sở Xây dựng Long An, TP.HCM, Tây Ninh
- Tin tức báo chí & thị trường công khai
"""

import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search_public_project_news(project_name: str, location: str = "") -> List[Dict[str, Any]]:
    """
    Tìm kiếm thông tin báo chí công khai về dự án để trích xuất tuyên bố CĐT
    sử dụng DuckDuckGo HTML (Miễn phí 100%, không cần API key)
    """
    query = f'"{project_name}" "{location}" quy mô giá bán dự án'
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    results = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            snippets = soup.find_all("div", class_="result__body")
            for item in snippets[:5]:
                title_elem = item.find("a", class_="result__snippet") or item.find("a", class_="result__url")
                body_elem = item.find("a", class_="result__snippet")
                link_elem = item.find("a", class_="result__url")

                title = title_elem.get_text(strip=True) if title_elem else "Tin tức dự án"
                snippet_text = body_elem.get_text(strip=True) if body_elem else ""
                href = link_elem.get("href", "") if link_elem else ""

                if snippet_text:
                    results.append({
                        "title": title,
                        "snippet": snippet_text,
                        "url": href
                    })
    except Exception as e:
        results.append({
            "title": f"Không thể kết nối tìm kiếm trực tiếp ({str(e)})",
            "snippet": "Vui lòng nhập trực tiếp thông số từ thông cáo báo chí hoặc website CĐT.",
            "url": ""
        })
    return results

def extract_project_claims_from_text(text: str) -> Dict[str, Any]:
    """
    Trích xuất các con số CĐT tuyên bố từ văn bản bài báo (quy mô ha, số căn, giá bán triệu/m2)
    """
    claims = {
        "detected_area_ha": None,
        "detected_units": None,
        "detected_price_m2": None
    }

    # Bắt quy mô diện tích (ha)
    ha_match = re.search(r'(\d+[\.,]?\d*)\s*(?:ha|hécta|hecta)', text, re.IGNORECASE)
    if ha_match:
        try:
            claims["detected_area_ha"] = float(ha_match.group(1).replace(",", "."))
        except Exception:
            pass

    # Bắt số lượng căn/nền
    unit_match = re.search(r'(\d+[\.,]?\d*)\s*(?:căn|nền|sản phẩm|lô)', text, re.IGNORECASE)
    if unit_match:
        try:
            val_str = unit_match.group(1).replace(".", "").replace(",", "")
            claims["detected_units"] = int(val_str)
        except Exception:
            pass

    # Bắt giá bán (triệu/m2)
    price_match = re.search(r'(\d+[\.,]?\d*)\s*(?:triệu|tr)/m2', text, re.IGNORECASE)
    if price_match:
        try:
            claims["detected_price_m2"] = float(price_match.group(1).replace(",", "."))
        except Exception:
            pass

    return claims

if __name__ == "__main__":
    sample_text = "Dự án Waterpoint Nam Long tại Bến Lức có quy mô 355ha, cung cấp hơn 10000 căn nhà phố biệt thự với mức giá dự kiến từ 52 triệu/m2."
    extracted = extract_project_claims_from_text(sample_text)
    print("Extracted claims:", extracted)
