from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
import pandas as pd
import os
import threading

from models import db, UTR

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db.init_app(app)

@app.route('/')
def index():
    utrs = UTR.query.order_by(UTR.created_at.desc()).all()
    return render_template('index.html', utrs=utrs)

@app.route('/add', methods=['POST'])
def add():
    utr_value = request.form['utr']
    remark = request.form.get('remark', '')
    if UTR.query.filter_by(utr=utr_value).first():
        return redirect(url_for('index'))
    new_utr = UTR(utr=utr_value, remark=remark)
    db.session.add(new_utr)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:utr_id>')
def delete(utr_id):
    utr = UTR.query.get_or_404(utr_id)
    db.session.delete(utr)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export():
    utrs = UTR.query.order_by(UTR.created_at.desc()).all()
    data = [{'UTR': u.utr, '备注': u.remark, '添加时间': u.created_at.strftime('%Y-%m-%d %H:%M:%S')} for u in utrs]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='UTRs')
    output.seek(0)
    return send_file(output, download_name="utrs.xlsx", as_attachment=True)

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '').strip()
    results = UTR.query.filter(UTR.utr.contains(keyword)).order_by(UTR.created_at.desc()).all()
    return render_template('index.html', utrs=results)

@app.route('/update_remark/<int:utr_id>', methods=['POST'])
def update_remark(utr_id):
    utr = UTR.query.get_or_404(utr_id)
    new_remark = request.form.get('remark', '')
    utr.remark = new_remark
    db.session.commit()
    return redirect(url_for('index'))

# 启动入口
if __name__ == '__main__':
    from telegram_bot import run_bot
    # 启动 Telegram bot 放在子线程
    threading.Thread(target=run_bot).start()
    # Flask 必须主线程运行
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
