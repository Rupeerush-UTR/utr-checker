# database.py

from models import db, UTR
from datetime import datetime
from main import app  # 导入 Flask app 对象

def add_utr(utr_number, note):
    with app.app_context():
        exists = UTR.query.filter_by(utr=utr_number).first()
        if exists:
            return False  # 已存在
        new_record = UTR(
            utr=utr_number,
            note=note,
            created_at=datetime.now()
        )
        db.session.add(new_record)
        db.session.commit()
        return True

def query_utr(utr_number):
    with app.app_context():
        return UTR.query.filter_by(utr=utr_number).first()
