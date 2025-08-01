from flask import Flask, render_template, request, redirect, url_for, send_file
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
    return render_template('index.html', utrs=UTR.query.order_by(UTR.id.desc()).all())

@app.route('/add', methods=['POST'])
def add_utr():
    utr_value = request.form['utr']
    remark = request.form.get('remark', '')
    if not UTR.query.filter_by(utr=utr_value).first():
        new_utr = UTR(utr=utr_value, remark=remark)
        db.session.add(new_utr)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:utr_id>')
def delete_utr(utr_id):
    utr = UTR.query.get_or_404(utr_id)
    db.session.delete(utr)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export_utrs():
    utrs = UTR.query.order_by(UTR.id.desc()).all()
    df = pd.DataFrame([(utr.utr, utr.remark, utr.timestamp.strftime('%Y-%m-%d %H:%M:%S')) for utr in utrs],
                      columns=['UTR', '备注', '添加时间'])
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="utrs.xlsx", as_attachment=True)

def start_flask():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    threading.Thread(target=start_flask).start()
    run_bot(app)
