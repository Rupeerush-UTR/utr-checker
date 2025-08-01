from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from io import BytesIO
import os
import asyncio
import threading

from models import db, UTR

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
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

# 🔄 同时启动 Flask 和 Bot
async def start_all():
    from telegram_bot import run_bot
    await run_bot()

def start_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()
    asyncio.run(start_all())
