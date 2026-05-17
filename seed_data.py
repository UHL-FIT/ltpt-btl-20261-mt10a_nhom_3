"""
seed_data.py – Insert sample patient data for demonstration.
Run once: python seed_data.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import model

SAMPLE_PATIENTS = [
    {"ma_bn":"BN0001","ten":"Nguyễn Văn An",    "tuoi":"45","gioi_tinh":"Nam","chieu_cao":"170","can_nang":"72","huyet_ap":"130/85","lich_su_kham":"Khám định kỳ","loai_benh":["Tim mạch", "Tiểu đường"],  "lich_su_thuoc":"Aspirin 100mg"},
    {"ma_bn":"BN0002","ten":"Trần Thị Bình",     "tuoi":"32","gioi_tinh":"Nữ","chieu_cao":"158","can_nang":"55","huyet_ap":"110/70","lich_su_kham":"Khám lần đầu", "loai_benh":["Tiểu đường"],"lich_su_thuoc":"Metformin 500mg"},
    {"ma_bn":"BN0003","ten":"Lê Minh Cường",     "tuoi":"60","gioi_tinh":"Nam","chieu_cao":"165","can_nang":"80","huyet_ap":"145/90","lich_su_kham":"Tái khám",    "loai_benh":["Tim mạch", "Xương khớp"],  "lich_su_thuoc":"Amlodipine 5mg"},
    {"ma_bn":"BN0004","ten":"Phạm Thu Dung",     "tuoi":"28","gioi_tinh":"Nữ","chieu_cao":"162","can_nang":"58","huyet_ap":"115/75","lich_su_kham":"Khám thai",    "loai_benh":["Khác"],      "lich_su_thuoc":"Vitamin tổng hợp"},
    {"ma_bn":"BN0005","ten":"Hoàng Đình Em",     "tuoi":"55","gioi_tinh":"Nam","chieu_cao":"168","can_nang":"90","huyet_ap":"150/95","lich_su_kham":"Tái khám",    "loai_benh":["Tiểu đường", "Tim mạch"],"lich_su_thuoc":"Insulin"},
    {"ma_bn":"BN0006","ten":"Vũ Thị Phương",     "tuoi":"17","gioi_tinh":"Nữ","chieu_cao":"155","can_nang":"45","huyet_ap":"105/65","lich_su_kham":"Khám lần đầu", "loai_benh":["Hô hấp"],   "lich_su_thuoc":"Salbutamol"},
    {"ma_bn":"BN0007","ten":"Đặng Quốc Giang",   "tuoi":"38","gioi_tinh":"Nam","chieu_cao":"175","can_nang":"68","huyet_ap":"120/80","lich_su_kham":"Khám định kỳ","loai_benh":["Xương khớp"],"lich_su_thuoc":"Ibuprofen 400mg"},
    {"ma_bn":"BN0008","ten":"Bùi Thị Hoa",       "tuoi":"65","gioi_tinh":"Nữ","chieu_cao":"152","can_nang":"60","huyet_ap":"155/98","lich_su_kham":"Tái khám",    "loai_benh":["Tim mạch", "Thần kinh"],  "lich_su_thuoc":"Atenolol 50mg"},
    {"ma_bn":"BN0009","ten":"Ngô Văn Hùng",      "tuoi":"42","gioi_tinh":"Nam","chieu_cao":"172","can_nang":"95","huyet_ap":"140/90","lich_su_kham":"Khám định kỳ","loai_benh":["Tiêu hóa", "Xương khớp"], "lich_su_thuoc":"Omeprazole 20mg"},
    {"ma_bn":"BN0010","ten":"Trịnh Thị Lan",     "tuoi":"50","gioi_tinh":"Nữ","chieu_cao":"160","can_nang":"65","huyet_ap":"125/82","lich_su_kham":"Khám định kỳ","loai_benh":["Da liễu"],  "lich_su_thuoc":"Cetirizine 10mg"},
    {"ma_bn":"BN0011","ten":"Lý Văn Minh",       "tuoi":"70","gioi_tinh":"Nam","chieu_cao":"163","can_nang":"58","huyet_ap":"160/100","lich_su_kham":"Tái khám",   "loai_benh":["Thần kinh", "Tim mạch"], "lich_su_thuoc":"Aspirin + Clopidogrel"},
    {"ma_bn":"BN0012","ten":"Dương Thị Nga",     "tuoi":"25","gioi_tinh":"Nữ","chieu_cao":"165","can_nang":"52","huyet_ap":"108/68","lich_su_kham":"Khám lần đầu", "loai_benh":["Hô hấp"],   "lich_su_thuoc":"Montelukast 10mg"},
]

if __name__ == "__main__":
    model.init_db()
    added, skipped = 0, 0
    for p in SAMPLE_PATIENTS:
        ok, msg = model.add_patient(p)
        if ok:
            added += 1
        else:
            skipped += 1
            print(f"  Bỏ qua {p['ma_bn']}: {msg}")
    print(f"✅  Seed xong: {added} thêm mới, {skipped} bỏ qua.")
