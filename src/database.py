# database.py

from models import db, UTRRecord
from datetime import datetime

def add_utr(utr_number, remark):
    exists = UTRRecord.query.filter_by(utr=utr_number).first()
    if exists:
        return False  # 已存在
    new_record = UTRRecord(
        utr=utr_number,
        remark=remark,
        created_at=datetime.now()
    )
    db.session.add(new_record)
    db.session.commit()
    return True

def query_utr(utr_number):
    return UTRRecord.query.filter_by(utr=utr_number).first()
