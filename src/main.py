from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
import pandas as pd
import os

from models import db, UTR
from telegram_bot import start_bot  # 注意要用 async 的方法

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")  # Render 环境变量已自动注入
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 首页
@app.route('/')
def index():
    utrs = UTR.query.order_by(UTR.created_at.desc()).all()
    return render_template('index.html', utrs=utrs)

# 添加 UTR
@app.route('/add', methods=['POST'])
def add_utr():
    utr_value = request.form['utr']
    note = request.form.get('note', '')

    existing = UTR.query.filter_by(utr=utr_value).first()
    if not existing:
        new_utr = UTR(utr=utr_value, note=note)
        db.session.add(new_utr)
        db.session.commit()
    return redirect(url_for('index'))

# 查询 UTR
@app.route('/query', methods=['GET'])
def query_utr():
    search = request.args.get('search', '')
    results = UTR.query.filter(UTR.utr.contains(search)).all()
    return render_template('query.html', utrs=results, search=search)

# 删除 UTR
@app.route('/delete/<int:utr_id>', methods=['POST'])
def delete_utr(utr_id):
    utr = UTR.query.get_or_404(utr_id)
    db.session.delete(utr)
    db.session.commit()
    return redirect(url_for('index'))

# 导出 Excel
@app.route('/export', methods=['GET'])
def export_excel():
    utrs = UTR.query.order_by(UTR.created_at.desc()).all()
    data = [{'UTR': u.utr, '备注': u.note, '创建时间': u.created_at.strftime('%Y-%m-%d %H:%M:%S')} for u in utrs]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name='utrs.xlsx', as_attachment=True)

# 启动
if __name__ == '__main__':
    import asyncio

    async def main():
        async with app.app_context():
            db.create_all()
            await start_bot(app)

    asyncio.run(main())
