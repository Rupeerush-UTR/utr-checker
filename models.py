from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UTR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utr = db.Column(db.String(64), unique=True, nullable=False)
    remark = db.Column(db.String(256))  # 确保数据库表中也有此列
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
