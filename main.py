from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
import pytz  # 要加上这行
india_tz = timezone('Asia/Kolkata')
import pandas as pd
import os
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class UTRRecord(db.Model):
    ...


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://utr_sj_user:l1QGJqrMyxksukna0QhZrhbfL9RbywAz@dpg-d24ui7vdiees739mrel0-a/utr_sj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

class UTR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utr = db.Column(db.String(100), unique=True, nullable=False)
    note = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/', methods=['GET'])
def index():
    query = request.args.get('query', '').strip()
    message = request.args.get('message', '')
    if query:
        records = UTR.query.filter(UTR.utr.contains(query)).order_by(UTR.created_at.desc()).all()
    else:
        records = UTR.query.order_by(UTR.created_at.desc()).all()

    # 转为印度时间并准备传给模板
    display_records = []
    for r in records:
        india_time = r.created_at.replace(tzinfo=pytz.UTC).astimezone(india_tz).strftime('%Y-%m-%d %H:%M:%S')
        display_records.append({
            'id': r.id,
            'utr': r.utr,
            'note': r.note,
            'created_at': india_time
        })

    return render_template('index.html', records=display_records, message=message, query=query)

@app.route('/add', methods=['POST'])
def add():
    utr = request.form.get('utr', '').strip()
    note = request.form.get('note', '').strip()
    if not utr:
        return redirect(url_for('index', message='UTR 不能为空'))

    existing = UTR.query.filter_by(utr=utr).first()
    if existing:
        return redirect(url_for('index', message='UTR 已存在'))

    new_record = UTR(utr=utr, note=note)
    db.session.add(new_record)
    db.session.commit()
    return redirect(url_for('index', message='录入成功'))

@app.route('/delete/<int:utr_id>', methods=['POST'])
def delete(utr_id):
    record = UTR.query.get(utr_id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for('index', message='删除成功'))

@app.route('/update_note/<int:utr_id>', methods=['POST'])
def update_note(utr_id):
    new_note = request.form.get('note', '').strip()  # HTML表单中字段是 note
    record = UTR.query.get(utr_id)
    if record:
        record.note = new_note
        db.session.commit()
    return redirect(url_for('index', message='备注已更新'))

@app.route('/batch_import', methods=['POST'])
def batch_import():
    file = request.files.get('file')
    if not file:
        return redirect(url_for('index', message='请上传文件'))

    try:
        df = pd.read_csv(file)
        count = 0
        for _, row in df.iterrows():
            utr = str(row.get('utr', '')).strip()
            note = str(row.get('note', '')).strip()
            if utr and not UTR.query.filter_by(utr=utr).first():
                db.session.add(UTR(utr=utr, note=note))
                count += 1
        db.session.commit()
        return redirect(url_for('index', message=f'成功导入 {count} 条记录'))
    except Exception as e:
        return redirect(url_for('index', message=f'导入失败: {str(e)}'))

@app.route('/export')
def export_excel():
    records = UTR.query.order_by(UTR.created_at.desc()).all()
    data = [{
        'ID': r.id,
        'UTR': r.utr,
        '备注': r.note,
        '时间': r.created_at.replace(tzinfo=timezone('UTC')).astimezone(india_tz).strftime('%Y-%m-%d %H:%M:%S')
    } for r in records]
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='utr_export.xlsx')

if __name__ == '__main__':
    import threading
    from telegram_bot import run_bot

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        db.create_all()

    # 启动 Telegram Bot
    threading.Thread(target=run_bot).start()

    # 启动 Flask
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
