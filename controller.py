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
    return model.get_patients_with_diseases()


def get_patient_list() -> pd.DataFrame:
    """Fetch all patients."""
    return model.get_all_patients()


# ──────────────────────────────────────────────
# ANALYTICS
# ──────────────────────────────────────────────

def get_bp_by_age_group(df=None) -> pd.DataFrame:
    """Average blood pressure by age group."""
    if df is None: df = model.get_all_patients()
    return model.avg_blood_pressure_by_age_group(df)


def get_disease_frequency() -> pd.DataFrame:
    """Visit frequency by disease type."""
    return model.disease_frequency()


def get_bmi_distribution(df=None) -> pd.DataFrame:
    """BMI data for all patients."""
    if df is None: df = model.get_all_patients()
    return model.bmi_distribution(df)


def get_summary_stats(df=None) -> dict:
    """High-level summary statistics."""
    if df is None: df = model.get_all_patients()
    return model.summary_stats(df)


def get_stats_payload() -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetch shared dashboard data once, then derive all stats from it."""
    df = model.get_all_patients()
    return (
        model.summary_stats(df),
        model.avg_blood_pressure_by_age_group(df),
        model.disease_frequency(),
        model.bmi_distribution(df),
    )


# ──────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────

def compute_bmi_preview(can_nang_str: str, chieu_cao_str: str) -> str:
    """Real-time BMI calculation for form preview."""
    try:
        cn = float(can_nang_str.strip())
        cc = float(chieu_cao_str.strip())
        if cn <= 0 or cc <= 0:
            return ""
        bmi = model.calculate_bmi(cn, cc)
        classification = model.classify_bmi(bmi)
        return f"📊  BMI: {bmi} ({classification})"
    except (ValueError, TypeError):
        return ""


def get_all_diseases() -> list[str]:
    """Get all available disease types."""
    return model.get_all_diseases()


def get_patient_diseases(ma_bn: str) -> list[str]:
    """Get diseases for a specific patient."""
    return model.get_patient_diseases(ma_bn)


# ──────────────────────────────────────────────
# IMPORT/EXPORT
# ──────────────────────────────────────────────

def handle_export_csv(filepath: str) -> tuple[bool, str]:
    """Export all patients to CSV."""
    return model.export_to_csv(filepath)


def handle_import_csv(filepath: str, merge: bool = False, on_success=None) -> tuple[bool, str]:
    """Import patients from CSV."""
    ok, msg = model.import_from_csv(filepath, merge=merge)
    if ok and on_success:
        on_success()
    return ok, msg


