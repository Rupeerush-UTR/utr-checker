from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import openpyxl
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utr_records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UTRRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utr = db.Column(db.String(100), unique=True, nullable=False)
    remark = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_utr():
    data = request.json
    utrs = data.get('utrs', [])
    remark = data.get('remark', '')
    added = []
    duplicates = []

    for utr in utrs:
        if not utr.strip():
            continue
        exists = UTRRecord.query.filter_by(utr=utr.strip()).first()
        if exists:
            duplicates.append(utr.strip())
        else:
            new_record = UTRRecord(utr=utr.strip(), remark=remark)
            db.session.add(new_record)
            added.append(utr.strip())

    db.session.commit()
    return jsonify({'added': added, 'duplicates': duplicates})

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        records = UTRRecord.query.filter(
            UTRRecord.utr.contains(keyword) | UTRRecord.remark.contains(keyword)
        ).order_by(UTRRecord.created_at.desc()).all()
    else:
        records = UTRRecord.query.order_by(UTRRecord.created_at.desc()).all()
    return jsonify([
        {'id': r.id, 'utr': r.utr, 'remark': r.remark or '', 'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        for r in records
    ])

@app.route('/delete/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    record = UTRRecord.query.get(record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/update_remark/<int:record_id>', methods=['POST'])
def update_remark(record_id):
    new_remark = request.json.get('remark', '')
    record = UTRRecord.query.get(record_id)
    if record:
        record.remark = new_remark
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/export', methods=['GET'])
def export_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['UTR', '备注', '创建时间'])

    records = UTRRecord.query.order_by(UTRRecord.created_at.desc()).all()
    for r in records:
        ws.append([r.utr, r.remark or '', r.created_at.strftime('%Y-%m-%d %H:%M:%S')])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(output, download_name=f"utr_export_{now}.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
