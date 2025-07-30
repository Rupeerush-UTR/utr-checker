from flask import Flask, request, render_template, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import io
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utr_records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UTRRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utr = db.Column(db.String(120), unique=True, nullable=False)
    remark = db.Column(db.String(300), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        utr_input = request.form.get('utr_input', '').strip()
        remark = request.form.get('remark', '')
        if utr_input:
            exists = UTRRecord.query.filter_by(utr=utr_input).first()
            if exists:
                message = f'❌ 已存在：{utr_input}'
            else:
                new_record = UTRRecord(utr=utr_input, remark=remark)
                db.session.add(new_record)
                db.session.commit()
                message = f'✅ 添加成功：{utr_input}'
    query = request.args.get('query', '').strip()
    if query:
        records = UTRRecord.query.filter(UTRRecord.utr.contains(query)).all()
    else:
        records = UTRRecord.query.order_by(UTRRecord.id.desc()).all()
    return render_template('index.html', records=records, message=message, query=query)

@app.route('/delete/<int:record_id>')
def delete(record_id):
    record = UTRRecord.query.get(record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:record_id>', methods=['POST'])
def update(record_id):
    record = UTRRecord.query.get(record_id)
    if record:
        new_remark = request.form.get('new_remark', '')
        record.remark = new_remark
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/batch', methods=['POST'])
def batch():
    data = request.form.get('batch_input', '')
    lines = data.splitlines()
    added = 0
    skipped = 0
    for line in lines:
        line = line.strip()
        if line:
            if not UTRRecord.query.filter_by(utr=line).first():
                db.session.add(UTRRecord(utr=line))
                added += 1
            else:
                skipped += 1
    db.session.commit()
    message = f'批量导入完成，成功添加 {added} 条，跳过 {skipped} 条重复记录。'
    return redirect(url_for('index', message=message))

@app.route('/export')
def export():
    records = UTRRecord.query.order_by(UTRRecord.id.desc()).all()
    data = [{'UTR': r.utr, '备注': r.remark or ''} for r in records]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='UTR记录')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='utr_records.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# ✅ 适配 Render：监听 0.0.0.0:$PORT
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=False, host='0.0.0.0', port=port)
