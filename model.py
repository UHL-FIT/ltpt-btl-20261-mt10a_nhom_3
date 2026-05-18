"""
model.py - Data layer: Pure functions for patient data processing.
Uses pandas for analysis and SQLite for persistence.
"""

import os
import re
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
        lich_su_thuoc TEXT,
        ngay_tao    TEXT
    );
    
    CREATE TABLE IF NOT EXISTS diseases (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ten         TEXT NOT NULL UNIQUE
    );
    
    CREATE TABLE IF NOT EXISTS patient_diseases (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_bn       TEXT NOT NULL,
        disease_id  INTEGER NOT NULL,
        FOREIGN KEY (ma_bn) REFERENCES patients(ma_bn) ON DELETE CASCADE,
        FOREIGN KEY (disease_id) REFERENCES diseases(id),
        UNIQUE(ma_bn, disease_id)
    )
    """
    with get_connection() as conn:
        # Split multiple statements
        for statement in sql.split(';'):
            if statement.strip():
                conn.execute(statement.strip())
        conn.commit()
        
        # Insert default diseases if not exist
        default_diseases = [
            "Tim mạch", "Tiểu đường", "Hô hấp", "Tiêu hóa",
            "Thần kinh", "Xương khớp", "Da liễu", "Khác"
        ]
        for disease in default_diseases:
            conn.execute(
                "INSERT OR IGNORE INTO diseases (ten) VALUES (?)",
                (disease,)
            )
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
    ma_bn = str(data.get("ma_bn", "")).strip()
    if not ma_bn:
        errors.append("Mã bệnh nhân không được để trống.")
    elif not re.match(r"^BN\d+$", ma_bn):
        errors.append("Mã bệnh nhân phải bắt đầu bằng BN và theo sau là chữ số, ví dụ: BN0001.")
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
    if not str(data.get("ten", "")).strip():
        errors.append("Tên bệnh nhân không được để trống.")
    ha = str(data.get("huyet_ap", "")).strip()
    if ha and parse_huyet_ap(ha) is None:
        errors.append("Huyết áp phải có định dạng: systolic/diastolic (ví dụ: 120/80).")
    return errors


# ──────────────────────────────────────────────
# CRUD OPERATIONS
# ──────────────────────────────────────────────

def add_patient(data: dict, conn: sqlite3.Connection | None = None) -> tuple[bool, str]:
    """Insert a new patient. Returns (success, message)."""
    owns_connection = conn is None
    try:
        bmi = calculate_bmi(float(data["can_nang"]), float(data["chieu_cao"]))
        sql = """
        INSERT INTO patients
            (ma_bn, ten, tuoi, gioi_tinh, chieu_cao, can_nang,
             huyet_ap, lich_su_kham, lich_su_thuoc, ngay_tao)
        VALUES (?,?,?,?,?,?,?,?,?,?)
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
            data.get("lich_su_thuoc", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        if owns_connection:
            with get_connection() as conn:
                conn.execute(sql, values)
                
                loai_benh_list = data.get("loai_benh", [])
                if isinstance(loai_benh_list, str):  # Handle single string
                    loai_benh_list = [loai_benh_list] if loai_benh_list else []
                
                for disease_name in loai_benh_list:
                    if disease_name.strip():
                        disease_row = conn.execute(
                            "SELECT id FROM diseases WHERE ten = ?", (disease_name.strip(),)
                        ).fetchone()
                        if disease_row:
                            disease_id = disease_row[0]
                        else:
                            conn.execute("INSERT INTO diseases (ten) VALUES (?)", (disease_name.strip(),))
                            disease_id = conn.lastrowid
                        conn.execute(
                            "INSERT OR IGNORE INTO patient_diseases (ma_bn, disease_id) VALUES (?, ?)",
                            (data["ma_bn"].strip(), disease_id)
                        )
                conn.commit()
        else:
            conn.execute(sql, values)
            loai_benh_list = data.get("loai_benh", [])
            if isinstance(loai_benh_list, str):  # Handle single string
                loai_benh_list = [loai_benh_list] if loai_benh_list else []
            
            for disease_name in loai_benh_list:
                if disease_name.strip():
                    disease_row = conn.execute(
                        "SELECT id FROM diseases WHERE ten = ?", (disease_name.strip(),)
                    ).fetchone()
                    if disease_row:
                        disease_id = disease_row[0]
                    else:
                        conn.execute("INSERT INTO diseases (ten) VALUES (?)", (disease_name.strip(),))
                        disease_id = conn.lastrowid
                    conn.execute(
                        "INSERT OR IGNORE INTO patient_diseases (ma_bn, disease_id) VALUES (?, ?)",
                        (data["ma_bn"].strip(), disease_id)
                    )
        return True, f"Đã thêm bệnh nhân {data['ten']} (BMI: {bmi})"
    except sqlite3.IntegrityError:
        return False, f"Mã bệnh nhân '{data['ma_bn']}' đã tồn tại!"
    except Exception as e:
        return False, str(e)


def update_patient(ma_bn: str, data: dict, conn: sqlite3.Connection | None = None) -> tuple[bool, str]:
    """Update an existing patient record."""
    owns_connection = conn is None
    try:
        sql = """
        UPDATE patients SET
            ten=?, tuoi=?, gioi_tinh=?, chieu_cao=?, can_nang=?,
            huyet_ap=?, lich_su_kham=?, lich_su_thuoc=?
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
            data.get("lich_su_thuoc", ""),
            ma_bn,
        )

        if owns_connection:
            with get_connection() as conn:
                conn.execute(sql, values)
                
                conn.execute("DELETE FROM patient_diseases WHERE ma_bn=?", (ma_bn,))
                
                loai_benh_list = data.get("loai_benh", [])
                if isinstance(loai_benh_list, str):  # Handle single string
                    loai_benh_list = [loai_benh_list] if loai_benh_list else []
                
                for disease_name in loai_benh_list:
                    if disease_name.strip():
                        disease_row = conn.execute(
                            "SELECT id FROM diseases WHERE ten = ?", (disease_name.strip(),)
                        ).fetchone()
                        if disease_row:
                            disease_id = disease_row[0]
                        else:
                            conn.execute("INSERT INTO diseases (ten) VALUES (?)", (disease_name.strip(),))
                            disease_id = conn.lastrowid
                        conn.execute(
                            "INSERT OR IGNORE INTO patient_diseases (ma_bn, disease_id) VALUES (?, ?)",
                            (ma_bn, disease_id)
                        )
                conn.commit()
        else:
            conn.execute(sql, values)
            conn.execute("DELETE FROM patient_diseases WHERE ma_bn=?", (ma_bn,))
            loai_benh_list = data.get("loai_benh", [])
            if isinstance(loai_benh_list, str):  # Handle single string
                loai_benh_list = [loai_benh_list] if loai_benh_list else []
            
            for disease_name in loai_benh_list:
                if disease_name.strip():
                    disease_row = conn.execute(
                        "SELECT id FROM diseases WHERE ten = ?", (disease_name.strip(),)
                    ).fetchone()
                    if disease_row:
                        disease_id = disease_row[0]
                    else:
                        conn.execute("INSERT INTO diseases (ten) VALUES (?)", (disease_name.strip(),))
                        disease_id = conn.lastrowid
                    conn.execute(
                        "INSERT OR IGNORE INTO patient_diseases (ma_bn, disease_id) VALUES (?, ?)",
                        (ma_bn, disease_id)
                    )
        return True, "Cập nhật thành công!"
    except Exception as e:
        return False, str(e)


def delete_patient(ma_bn: str) -> tuple[bool, str]:
    """Delete a patient by ID."""
    try:
        with get_connection() as conn:
            # Delete patient diseases first (cascading)
            conn.execute("DELETE FROM patient_diseases WHERE ma_bn=?", (ma_bn,))
            # Delete patient
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


def get_patients_with_diseases() -> pd.DataFrame:
    """Fetch all patients with their diseases as a DataFrame (with loai_benh column)."""
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM patients", conn)
        
        if df.empty:
            return df
        
        # Add loai_benh column with comma-separated disease names
        diseases_list = []
        for ma_bn in df["ma_bn"]:
            diseases = get_patient_diseases(ma_bn)
            diseases_list.append(", ".join(diseases) if diseases else "")
        
        df["loai_benh"] = diseases_list
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


def get_patient_diseases(ma_bn: str) -> list[str]:
    """Get list of disease names for a patient."""
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT d.ten FROM diseases d
                JOIN patient_diseases pd ON d.id = pd.disease_id
                WHERE pd.ma_bn = ?
            """, (ma_bn,)).fetchall()
        return [row[0] for row in rows]
    except Exception:
        return []


def get_all_diseases() -> list[str]:
    """Get list of all disease names."""
    try:
        with get_connection() as conn:
            rows = conn.execute("SELECT ten FROM diseases ORDER BY ten").fetchall()
        return [row[0] for row in rows]
    except Exception:
        return []


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


def disease_frequency(df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Pure: count visit frequency by disease type.
    If df is provided (legacy), use it. Otherwise, get from database.
    Returns DataFrame with columns [Loại bệnh, Số lượt].
    """
    if df is None:
        # Get from database
        try:
            with get_connection() as conn:
                df = pd.read_sql_query("""
                    SELECT d.ten, COUNT(pd.ma_bn) as count
                    FROM diseases d
                    LEFT JOIN patient_diseases pd ON d.id = pd.disease_id
                    GROUP BY d.id, d.ten
                    ORDER BY count DESC
                """, conn)
            if df.empty:
                return pd.DataFrame(columns=["Loại bệnh", "Số lượt"])
            df.columns = ["Loại bệnh", "Số lượt"]
            return df
        except Exception:
            return pd.DataFrame(columns=["Loại bệnh", "Số lượt"])
    else:
        # Legacy: use provided DataFrame (for backward compatibility)
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


# ──────────────────────────────────────────────
# IMPORT/EXPORT CSV
# ──────────────────────────────────────────────

def export_to_csv(filepath: str) -> tuple[bool, str]:
    """Export all patients to CSV file."""
    try:
        df = get_all_patients()
        if df.empty:
            return False, "Không có dữ liệu để xuất."
        # Column order (without loai_benh)
        columns = ["ma_bn", "ten", "tuoi", "gioi_tinh", "chieu_cao", "can_nang", 
                   "huyet_ap", "lich_su_kham", "lich_su_thuoc", "ngay_tao"]
        df = df[columns]
        # Vietnamese column names for CSV header
        df.columns = ["Mã BN", "Tên", "Tuổi", "Giới tính", "Chiều cao (cm)", "Cân nặng (kg)", 
                      "Huyết áp", "Lịch sử khám", "Lịch sử thuốc", "Ngày tạo"]
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        return True, f"Đã xuất {len(df)} bệnh nhân ra file: {filepath}"
    except Exception as e:
        return False, f"Lỗi xuất CSV: {str(e)}"


def import_from_csv(filepath: str, merge: bool = False) -> tuple[bool, str]:
    """
    Import patients from CSV file.
    If merge=True: update existing records, add new ones.
    If merge=False: skip existing records.
    """
    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
        
        # Normalize column names to English
        column_mapping = {
            "Mã BN": "ma_bn", "mã_bn": "ma_bn", "ma bn": "ma_bn",
            "Tên": "ten", "tên": "ten",
            "Tuổi": "tuoi", "tuổi": "tuoi",
            "Giới tính": "gioi_tinh", "giới_tính": "gioi_tinh", "giới tinh": "gioi_tinh",
            "Chiều cao (cm)": "chieu_cao", "chiều_cao": "chieu_cao", "chieu cao": "chieu_cao",
            "Cân nặng (kg)": "can_nang", "cân_nặng": "can_nang", "can nang": "can_nang",
            "Huyết áp": "huyet_ap", "huyết_áp": "huyet_ap", "huyet ap": "huyet_ap",
            "Lịch sử khám": "lich_su_kham", "lịch_sử_khám": "lich_su_kham", "lich su kham": "lich_su_kham",
            "Lịch sử thuốc": "lich_su_thuoc", "lịch_sử_thuốc": "lich_su_thuoc", "lich su thuoc": "lich_su_thuoc",
            "Ngày tạo": "ngay_tao", "ngày_tạo": "ngay_tao", "ngay tao": "ngay_tao",
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Required columns
        required = ["ma_bn", "ten", "tuoi", "gioi_tinh", "chieu_cao", "can_nang"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            return False, f"Thiếu cột bắt buộc: {', '.join(missing)}"
        
        # Convert types
        df["tuoi"] = pd.to_numeric(df["tuoi"], errors="coerce").astype("Int64")
        df["chieu_cao"] = pd.to_numeric(df["chieu_cao"], errors="coerce").astype("float")
        df["can_nang"] = pd.to_numeric(df["can_nang"], errors="coerce").astype("float")
        
        added = 0
        updated = 0
        errors = []
        
        with get_connection() as conn:
            conn.execute("BEGIN")
            for idx, row in df.iterrows():
                row_data = row.to_dict()
                row_data = {k: (v if pd.notna(v) else "") for k, v in row_data.items()}
                
                # Validate
                validation_errors = validate_patient(row_data)
                if validation_errors:
                    errors.append(f"Dòng {idx+2}: {'; '.join(validation_errors)}")
                    continue
                
                ma_bn = row_data["ma_bn"]
                existing = conn.execute("SELECT 1 FROM patients WHERE ma_bn=?", (ma_bn,)).fetchone()
                
                if existing:
                    if merge:
                        ok, msg = update_patient(ma_bn, row_data, conn=conn)
                        if ok:
                            updated += 1
                        else:
                            errors.append(f"Dòng {idx+2}: Cập nhật thất bại - {msg}")
                else:
                    ok, msg = add_patient(row_data, conn=conn)
                    if ok:
                        added += 1
                    else:
                        errors.append(f"Dòng {idx+2}: Thêm thất bại - {msg}")
            
            if errors:
                conn.rollback()
                summary = f"Đã thêm: {added}, Cập nhật: {updated}"
                summary += f"\nLỗi: {len(errors)}\n" + "\n".join(errors[:5])
                return False, summary
            conn.commit()
        
        return True, f"Đã thêm: {added}, Cập nhật: {updated}"
    except Exception as e:
        return False, f"Lỗi nhập CSV: {str(e)}"
