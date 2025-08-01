from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UTR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utr = db.Column(db.String(120), unique=True, nullable=False)
    remark = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
