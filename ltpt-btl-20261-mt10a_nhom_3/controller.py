"""
controller.py - Controller layer.
Functions that bridge UI actions and model operations.
All functions are pure wrappers: they receive data, delegate to model, return results.
"""

import model
import pandas as pd
from tkinter import messagebox


# ──────────────────────────────────────────────
# STARTUP
# ──────────────────────────────────────────────

def initialize_app() -> None:
    """Must be called once at startup to ensure DB schema exists."""
    model.init_db()


# ──────────────────────────────────────────────
# PATIENT CRUD
# ──────────────────────────────────────────────

def handle_add_patient(form_data: dict, on_success=None) -> tuple[bool, str]:
    """
    Validate then insert a patient.
    Calls on_success() callback if insertion succeeded.
    """
    errors = model.validate_patient(form_data)
    if errors:
        return False, "\n".join(errors)
    ok, msg = model.add_patient(form_data)
    if ok and on_success:
        on_success()
    return ok, msg


def handle_update_patient(ma_bn: str, form_data: dict, on_success=None) -> tuple[bool, str]:
    """Validate then update an existing patient."""
    form_data["ma_bn"] = ma_bn  # Inject ID so validation passes
    errors = model.validate_patient(form_data)
    if errors:
        return False, "\n".join(errors)
    ok, msg = model.update_patient(ma_bn, form_data)
    if ok and on_success:
        on_success()
    return ok, msg


def handle_delete_patient(ma_bn: str, on_success=None) -> tuple[bool, str]:
    """Delete a patient after confirmation."""
    if not ma_bn:
        return False, "Chưa chọn bệnh nhân để xoá."
    ok, msg = model.delete_patient(ma_bn)
    if ok and on_success:
        on_success()
    return ok, msg


def handle_search(keyword: str) -> pd.DataFrame:
    """Return search results as DataFrame."""
    if keyword.strip():
        return model.search_patients(keyword)
    return model.get_all_patients()


def get_patient_list() -> pd.DataFrame:
    """Fetch all patients."""
    return model.get_all_patients()


# ──────────────────────────────────────────────
# ANALYTICS
# ──────────────────────────────────────────────

def get_bp_by_age_group() -> pd.DataFrame:
    """Average blood pressure by age group."""
    df = model.get_all_patients()
    return model.avg_blood_pressure_by_age_group(df)


def get_disease_frequency() -> pd.DataFrame:
    """Visit frequency by disease type."""
    df = model.get_all_patients()
    return model.disease_frequency(df)


def get_bmi_distribution() -> pd.DataFrame:
    """BMI data for all patients."""
    df = model.get_all_patients()
    return model.bmi_distribution(df)


def get_summary_stats() -> dict:
    """High-level summary statistics."""
    df = model.get_all_patients()
    return model.summary_stats(df)


def compute_bmi_preview(can_nang: str, chieu_cao: str) -> str:
    """
    Real-time BMI preview for the input form.
    Returns formatted string or empty string on invalid input.
    """
    try:
        bmi = model.calculate_bmi(float(can_nang), float(chieu_cao))
        label = model.classify_bmi(bmi)
        return f"BMI: {bmi}  →  {label}"
    except Exception:
        return ""


def generate_patient_id(prefix: str = "BN") -> str:
    """Auto-generate a unique patient ID based on current count."""
    df = model.get_all_patients()
    next_num = len(df) + 1
    return f"{prefix}{next_num:04d}"
