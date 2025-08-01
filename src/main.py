from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
import pandas as pd
import os

from models import db, UTR

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")  # Render 会自动注入该变量
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db.init_app(app)

@app.route('/')
def index():
    utrs = UTR.query.order_by(UTR.created_at.desc()).all()
    return render_template('index.html', utrs=utrs)

@app.route('/add', methods=['POST'])
def add_utr():
    utr = request.form['utr'].strip()
    note = request.form['note'].strip()
    if not UTR.query.filter_by(utr=utr).first():
        new_utr = UTR(utr=utr, note=note)
        db.session.add(new_utr)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export():
    utrs = UTR.query.order_by(UTR.created_at.desc()).all()
    df = pd.DataFrame([{'UTR': u.utr, '备注': u.note, '创建时间': u.created_at} for u in utrs])
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="utrs.xlsx", as_attachment=True)

def start_flask():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    from telegram_bot import run_bot
    import threading
    threading.Thread(target=start_flask).start()
    run_bot()
