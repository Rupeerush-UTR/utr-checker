from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UTR(db.Model):
    __tablename__ = 'utr_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    utr = db.Column(db.String(100), unique=True, nullable=False)
    note = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
