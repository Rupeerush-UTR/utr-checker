from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# 配置数据库路径（SQLite 本地文件）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 数据模型：用于存储已提交的 UTR
class UTRRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utr = db.Column(db.String(100), unique=True, nullable=False)
    remark = db.Column(db.String(255), nullable=True)

# 确保数据库表在应用上下文中创建
with app.app_context():
    db.create_all()

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 提交单个 UTR
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    utr = data.get('utr', '').strip()
    remark = data.get('remark', '').strip()

    if not utr:
        return jsonify({'status': 'error', 'message': 'UTR不能为空'})

    existing = UTRRecord.query.filter_by(utr=utr).first()
    if existing:
        return jsonify({'status': 'duplicate'})
    
    new_record = UTRRecord(utr=utr, remark=remark)
    db.session.add(new_record)
    db.session.commit()
    return jsonify({'status': 'success'})

# 批量查询
@app.route('/bulk-check', methods=['POST'])
def bulk_check():
    data = request.get_json()
    utrs = data.get('utrs', [])
    results = []

    for utr in utrs:
        found = UTRRecord.query.filter_by(utr=utr.strip()).first()
        results.append({'utr': utr, 'exists': bool(found)})

    return jsonify(results)

# 查询所有记录
@app.route('/all', methods=['GET'])
def all_utrs():
    all_data = UTRRecord.query.all()
    result = [{'utr': r.utr, 'remark': r.remark} for r in all_data]
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
