# main.py
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
import pandas as pd
import os
import threading

from models import db, UTR
from telegram_bot import run_bot

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db.init_app(app)

@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    if query:
        results = UTR.query.filter(UTR.utr.ilike(f"%{query}%")).all()
    else:
        results = UTR.query.order_by(UTR.created_at.desc()).all()
    return render_template('index.html', utrs=results, query=query)

@app.route('/add', methods=['POST'])
def add_utr():
    utr = request.form['utr'].strip()
    note = request.form['note'].strip()

    if not utr:
        return redirect(url_for('index'))

    existing = UTR.query.filter_by(utr=utr).first()
    if existing:
        return redirect(url_for('index'))

    new_utr = UTR(utr=utr, note=note)
    db.session.add(new_utr)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_utr(id):
    record = UTR.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export_utrs():
    utrs = UTR.query.order_by(UTR.created_at.desc()).all()
    df = pd.DataFrame([{'UTR': u.utr, '备注': u.note, '创建时间': u.created_at} for u in utrs])
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="utrs.xlsx", as_attachment=True)

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    threading.Thread(target=run_flask).start()
    run_bot(app)
