from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from io import BytesIO
import os
from models import db, UTR
import asyncio
import threading

from telegram_bot import run_bot  # 必须在这引入，否则启动 bot 会报错

app = Flask(__name__)

# ✅ 从环境变量读取数据库连接字符串
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

@app.route('/')
def index():
    utrs = UTR.query.order_by(UTR.timestamp.desc()).all()
    return render_template('index.html', utrs=utrs)

@app.route('/add', methods=['POST'])
def add():
    utr = request.form['utr'].strip()
    remark = request.form.get('remark', '').strip()
    if not utr:
        return redirect(url_for('index'))
    if UTR.query.filter_by(utr=utr).first():
        return redirect(url_for('index'))
    new_utr = UTR(utr=utr, remark=remark)
    db.session.add(new_utr)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    record = UTR.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/export')
def export():
    utrs = UTR.query.order_by(UTR.timestamp.desc()).all()
    data = [{'UTR': u.utr, '备注': u.remark, '时间': u.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for u in utrs]
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='utrs.xlsx')

# 🔄 新增：异步启动 bot 和 Flask（在主线程）
async def start_all():
    from telegram_bot import run_bot()
    print("🤖 Telegram Bot 正在启动...")

    bot_app = await run_bot()
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    print("✅ Bot started polling")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # 启动 Flask（用线程避免阻塞主线程）
    def start_flask():
        app.run(host="0.0.0.0", port=10000)

    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    # 启动 Telegram bot（在主线程的 asyncio 事件循环中）
    asyncio.run(start_all())
