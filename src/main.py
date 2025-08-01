from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
import pandas as pd
import os
import threading

from models import db, UTR
from telegram_bot import run_bot  # Telegram 相关逻辑在这里

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")  # Render自动注入
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)

@app.route('/')
def index():
    utrs = UTR.query.order_by(UTR.timestamp.desc()).all()
    return render_template('index.html', utrs=utrs)

@app.route('/add', methods=['POST'])
def add_utr():
    utr_code = request.form['utr']
    remark = request.form['remark']
    if utr_code:
        existing = UTR.query.filter_by(utr=utr_code).first()
        if not existing:
            new_utr = UTR(utr=utr_code, remark=remark)
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
    utrs = UTR.query.order_by(UTR.timestamp.desc()).all()
    data = {
        'UTR': [u.utr for u in utrs],
        'Remark': [u.remark for u in utrs],
        'Timestamp': [u.timestamp.strftime('%Y-%m-%d %H:%M:%S') for u in utrs]
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='UTRs')
    output.seek(0)
    return send_file(output, download_name='utrs.xlsx', as_attachment=True)

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '')
    if keyword:
        utrs = UTR.query.filter(UTR.utr.ilike(f'%{keyword}%')).order_by(UTR.timestamp.desc()).all()
    else:
        utrs = UTR.query.order_by(UTR.timestamp.desc()).all()
    return render_template('index.html', utrs=utrs, search=keyword)

# 🚀 主程序入口
if __name__ == '__main__':
    # 启动 Telegram bot 的线程（子线程）
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # 启动 Flask（主线程）必须绑定正确端口
    port = int(os.environ.get('PORT', 5000))  # Render 会设置 PORT 环境变量
    app.run(debug=True, host='0.0.0.0', port=port)
