"""
Database Module for Real Estate Credit Rating & Benchmarking Platform
Hành lang trọng điểm: TP.HCM (vùng ven) - Long An - Tây Ninh
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "real_estate_credit.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Bảng Dự án BĐS (Master Projects Table)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        commercial_name TEXT NOT NULL,
        legal_name TEXT,
        developer TEXT NOT NULL,
        province TEXT NOT NULL,
        district TEXT NOT NULL,
        ward TEXT,
        address TEXT,
        latitude REAL,
        longitude REAL,
        total_area_ha REAL NOT NULL,
        total_units INTEGER,
        product_type TEXT,
        legal_stage TEXT NOT NULL,
        has_land_fee_clearance INTEGER DEFAULT 0,
        has_gpxd INTEGER DEFAULT 0,
        eligible_for_sale INTEGER DEFAULT 0,
        primary_price_m2 REAL,
        secondary_price_m2 REAL,
        absorption_rate_pct REAL,
        infrastructure_notes TEXT,
        risk_notes TEXT,
        source_url TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Bảng Nấc thang Pháp lý chi tiết (Legal Milestones History)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS legal_milestones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT NOT NULL,
        milestone_code TEXT NOT NULL,
        milestone_name TEXT NOT NULL,
        document_number TEXT,
        issued_date TEXT,
        authority TEXT,
        status TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    """)

    # 3. Bảng Điểm mốc Hạ tầng & Công nghiệp (Infrastructure & Industrial Corridors)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS infrastructure_nodes (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        node_type TEXT NOT NULL,
        province TEXT NOT NULL,
        district TEXT,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        status TEXT NOT NULL,
        completion_year TEXT,
        impact_radius_km REAL
    )
    """)

    # 4. Bảng Mặt bằng Đối chuẩn Giá & Nguồn cung Địa phương (Market Benchmarks)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS district_benchmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        province TEXT NOT NULL,
        district TEXT NOT NULL,
        avg_primary_price_m2 REAL,
        avg_secondary_price_m2 REAL,
        total_pipeline_units INTEGER,
        historical_absorption_pct REAL,
        dominant_product_type TEXT,
        source_reference TEXT
    )
    """)

    # 5. Bảng Chi tiết Phân loại Sản phẩm, Nhóm tòa & Các Loại Giá (Detailed Product Pricing)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_detailed_pricing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT NOT NULL,
        category TEXT NOT NULL,
        building_group TEXT NOT NULL,
        initial_price REAL NOT NULL,
        progress_price REAL NOT NULL,
        loan_price REAL NOT NULL,
        early_price REAL NOT NULL,
        avg_price REAL NOT NULL,
        notes TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    """)

    conn.commit()
    conn.close()

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

def execute_insert(query: str, params: tuple = ()) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_FILE)
