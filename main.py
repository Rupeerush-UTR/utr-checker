from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 数据模型
class UTRRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utr = db.Column(db.String(100), unique=True, nullable=False)
    remark = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

db.create_all()

# 简易HTML模板
HTML = '''
<!DOCTYPE html>
<html>
<head>
  <title>UTR 检查工具</title>
  <meta charset="utf-8">
</head>
<body>
  <h2>UTR 录入与重复检查</h2>
  <input type="text" id="utrInput" placeholder="输入 UTR">
  <input type="text" id="remarkInput" placeholder="备注 (可选)">
  <button onclick="submitUTR()">提交</button>
  <button onclick="showAll()">查看明细</button>
  <div id="result"></div>

  <script>
    async function submitUTR() {
      const utr = document.getElementById('utrInput').value.trim();
      const remark = document.getElementById('remarkInput').value.trim();
      if (!utr) {
        document.getElementById('result').innerText = "请输入有效的UTR";
        return;
      }
      const res = await fetch('/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ utr, remark })
      });
      const data = await res.json();
      document.getElementById('result').innerText = data.message;
    }

    async function showAll() {
      const res = await fetch('/list');
      const data = await res.json();
      let html = '<h3>明细列表</h3><ul>';
      for (const item of data.records) {
        html += `<li>${item.utr} - ${item.remark || ''} - ${item.created_at}</li>`;
      }
      html += '</ul>';
      document.getElementById('result').innerHTML = html;
    }
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/check', methods=['POST'])
def check_utr():
    data = request.get_json()
    utr = data.get('utr', '').strip()
    remark = data.get('remark', '').strip()

    if not utr:
        return jsonify({"message": "请输入有效的UTR"})

    existing = UTRRecord.query.filter_by(utr=utr).first()
    if existing:
        return jsonify({"message": f"❌ 已存在重复 UTR: {utr}"})

    new_record = UTRRecord(utr=utr, remark=remark)
    db.session.add(new_record)
    db.session.commit()
    return jsonify({"message": f"✅ UTR {utr} 已成功录入，无重复。"})

@app.route('/list')
def list_utrs():
    records = UTRRecord.query.order_by(UTRRecord.created_at.desc()).all()
    return jsonify({
        "records": [
            {
                "utr": r.utr,
                "remark": r.remark,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
            } for r in records
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
