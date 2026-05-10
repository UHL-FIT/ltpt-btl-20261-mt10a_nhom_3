"""
model.py - Data layer: Pure functions for patient data processing.
Uses pandas for analysis and SQLite for persistence.
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "patients.db")

# ──────────────────────────────────────────────
# DATABASE INITIALIZATION
# ──────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row_factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    sql = """
    CREATE TABLE IF NOT EXISTS patients (
        ma_bn       TEXT PRIMARY KEY,
        ten         TEXT NOT NULL,
        tuoi        INTEGER NOT NULL,
        gioi_tinh   TEXT NOT NULL,
        chieu_cao   REAL NOT NULL,
        can_nang    REAL NOT NULL,
        huyet_ap    TEXT NOT NULL,
        lich_su_kham TEXT,
        loai_benh   TEXT,
        lich_su_thuoc TEXT,
        ngay_tao    TEXT
    )
    """
    with get_connection() as conn:
        conn.execute(sql)
        conn.commit()


# ──────────────────────────────────────────────
# PURE FUNCTIONS – CALCULATIONS
# ──────────────────────────────────────────────

def calculate_bmi(can_nang_kg: float, chieu_cao_cm: float) -> float:
    """Pure: compute BMI from weight (kg) and height (cm)."""
    if chieu_cao_cm <= 0:
        raise ValueError("Chiều cao phải > 0")
    chieu_cao_m = chieu_cao_cm / 100.0
    return round(can_nang_kg / (chieu_cao_m ** 2), 2)


def classify_bmi(bmi: float) -> str:
    """Pure: return BMI classification label."""
    if bmi < 18.5:
        return "Thiếu cân"
    elif bmi < 25.0:
        return "Bình thường"
    elif bmi < 30.0:
        return "Thừa cân"
    else:
        return "Béo phì"


def classify_age_group(tuoi: int) -> str:
    """Pure: classify a patient age into a group."""
    if tuoi < 18:
        return "<18"
    elif tuoi <= 40:
        return "18-40"
    elif tuoi <= 60:
        return "41-60"
    else:
        return ">60"


def parse_huyet_ap(huyet_ap: str):
    """Pure: parse 'systolic/diastolic' string to (int, int) or None."""
    try:
        parts = huyet_ap.strip().split("/")
        return int(parts[0]), int(parts[1])
    except Exception:
        return None


# ──────────────────────────────────────────────
# VALIDATION
# ──────────────────────────────────────────────

def validate_patient(data: dict) -> list[str]:
    """
    Pure: validate patient dict. Returns list of error messages.
    Empty list means valid.
    """
    errors = []
    if not data.get("ma_bn", "").strip():
        errors.append("Mã bệnh nhân không được để trống.")
    try:
        tuoi = int(data.get("tuoi", ""))
        if tuoi <= 0 or tuoi > 150:
            errors.append("Tuổi phải là số nguyên dương (1-150).")
    except (ValueError, TypeError):
        errors.append("Tuổi phải là số nguyên.")
    try:
        cc = float(data.get("chieu_cao", ""))
        if cc <= 0:
            errors.append("Chiều cao phải > 0.")
    except (ValueError, TypeError):
        errors.append("Chiều cao phải là số.")
    try:
        cn = float(data.get("can_nang", ""))
        if cn <= 0:
            errors.append("Cân nặng phải > 0.")
    except (ValueError, TypeError):
        errors.append("Cân nặng phải là số.")
    if not data.get("ten", "").strip():
        errors.append("Tên bệnh nhân không được để trống.")
    ha = data.get("huyet_ap", "")
    if ha and parse_huyet_ap(ha) is None:
        errors.append("Huyết áp phải có định dạng: systolic/diastolic (ví dụ: 120/80).")
    return errors


# ──────────────────────────────────────────────
# CRUD OPERATIONS
# ──────────────────────────────────────────────

def add_patient(data: dict) -> tuple[bool, str]:
    """Insert a new patient. Returns (success, message)."""
    try:
        bmi = calculate_bmi(float(data["can_nang"]), float(data["chieu_cao"]))
        sql = """
        INSERT INTO patients
            (ma_bn, ten, tuoi, gioi_tinh, chieu_cao, can_nang,
             huyet_ap, lich_su_kham, loai_benh, lich_su_thuoc, ngay_tao)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """
        values = (
            data["ma_bn"].strip(),
            data["ten"].strip(),
            int(data["tuoi"]),
            data["gioi_tinh"],
            float(data["chieu_cao"]),
            float(data["can_nang"]),
            data.get("huyet_ap", ""),
            data.get("lich_su_kham", ""),
            data.get("loai_benh", ""),
            data.get("lich_su_thuoc", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        with get_connection() as conn:
            conn.execute(sql, values)
            conn.commit()
        return True, f"Đã thêm bệnh nhân {data['ten']} (BMI: {bmi})"
    except sqlite3.IntegrityError:
        return False, f"Mã bệnh nhân '{data['ma_bn']}' đã tồn tại!"
    except Exception as e:
        return False, str(e)


def update_patient(ma_bn: str, data: dict) -> tuple[bool, str]:
    """Update an existing patient record."""
    try:
        sql = """
        UPDATE patients SET
            ten=?, tuoi=?, gioi_tinh=?, chieu_cao=?, can_nang=?,
            huyet_ap=?, lich_su_kham=?, loai_benh=?, lich_su_thuoc=?
        WHERE ma_bn=?
        """
        values = (
            data["ten"].strip(),
            int(data["tuoi"]),
            data["gioi_tinh"],
            float(data["chieu_cao"]),
            float(data["can_nang"]),
            data.get("huyet_ap", ""),
            data.get("lich_su_kham", ""),
            data.get("loai_benh", ""),
            data.get("lich_su_thuoc", ""),
            ma_bn,
        )
        with get_connection() as conn:
            conn.execute(sql, values)
            conn.commit()
        return True, "Cập nhật thành công!"
    except Exception as e:
        return False, str(e)


def delete_patient(ma_bn: str) -> tuple[bool, str]:
    """Delete a patient by ID."""
    try:
        with get_connection() as conn:
            conn.execute("DELETE FROM patients WHERE ma_bn=?", (ma_bn,))
            conn.commit()
        return True, f"Đã xoá bệnh nhân '{ma_bn}'."
    except Exception as e:
        return False, str(e)


def get_all_patients() -> pd.DataFrame:
    """Fetch all patients as a DataFrame."""
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM patients", conn)
        return df
    except Exception:
        return pd.DataFrame()


def search_patients(keyword: str) -> pd.DataFrame:
    """Search patients by name or ID (case-insensitive)."""
    try:
        sql = "SELECT * FROM patients WHERE LOWER(ten) LIKE ? OR LOWER(ma_bn) LIKE ?"
        kw = f"%{keyword.lower()}%"
        with get_connection() as conn:
            df = pd.read_sql_query(sql, conn, params=(kw, kw))
        return df
    except Exception:
        return pd.DataFrame()


# ──────────────────────────────────────────────
# ANALYTICS – PURE PANDAS FUNCTIONS
# ──────────────────────────────────────────────

def avg_blood_pressure_by_age_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pure: compute average systolic & diastolic BP by age group.
    Input: full patients DataFrame.
    Output: DataFrame with columns [Nhóm tuổi, TB Tâm thu, TB Tâm trương].
    """
    if df.empty:
        return pd.DataFrame(columns=["Nhóm tuổi", "TB Tâm thu (mmHg)", "TB Tâm trương (mmHg)"])

    df = df.copy()
    df["nhom_tuoi"] = df["tuoi"].astype(int).apply(classify_age_group)

    parsed = df["huyet_ap"].apply(parse_huyet_ap)
    df["systolic"] = parsed.apply(lambda x: x[0] if x else None)
    df["diastolic"] = parsed.apply(lambda x: x[1] if x else None)

    df = df.dropna(subset=["systolic", "diastolic"])
    if df.empty:
        return pd.DataFrame(columns=["Nhóm tuổi", "TB Tâm thu (mmHg)", "TB Tâm trương (mmHg)"])

    group_order = ["<18", "18-40", "41-60", ">60"]
    result = (
        df.groupby("nhom_tuoi", observed=True)[["systolic", "diastolic"]]
        .mean()
        .round(1)
        .reset_index()
    )
    result.columns = ["Nhóm tuổi", "TB Tâm thu (mmHg)", "TB Tâm trương (mmHg)"]
    result["Nhóm tuổi"] = pd.Categorical(result["Nhóm tuổi"], categories=group_order, ordered=True)
    result = result.sort_values("Nhóm tuổi").reset_index(drop=True)
    return result


def disease_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pure: count visit frequency by disease type.
    Returns DataFrame with columns [Loại bệnh, Số lượt].
    """
    if df.empty:
        return pd.DataFrame(columns=["Loại bệnh", "Số lượt"])
    result = (
        df["loai_benh"]
        .fillna("Không rõ")
        .replace("", "Không rõ")
        .value_counts()
        .reset_index()
    )
    result.columns = ["Loại bệnh", "Số lượt"]
    return result


def bmi_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pure: compute BMI for every patient and add classification.
    Returns DataFrame with ma_bn, ten, bmi, phan_loai_bmi.
    """
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["bmi"] = df.apply(
        lambda r: calculate_bmi(float(r["can_nang"]), float(r["chieu_cao"])), axis=1
    )
    df["phan_loai_bmi"] = df["bmi"].apply(classify_bmi)
    return df[["ma_bn", "ten", "bmi", "phan_loai_bmi"]]


def summary_stats(df: pd.DataFrame) -> dict:
    """Pure: return a dict of summary statistics."""
    if df.empty:
        return {"tong_bn": 0, "trung_binh_tuoi": "-", "trung_binh_bmi": "-"}
    bmi_df = bmi_distribution(df)
    return {
        "tong_bn": len(df),
        "trung_binh_tuoi": round(df["tuoi"].astype(float).mean(), 1),
        "trung_binh_bmi": round(bmi_df["bmi"].mean(), 2) if not bmi_df.empty else "-",
        "nam": int((df["gioi_tinh"] == "Nam").sum()),
        "nu": int((df["gioi_tinh"] == "Nữ").sum()),
    }
