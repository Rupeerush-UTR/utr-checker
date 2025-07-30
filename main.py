from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class UTRRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utr = db.Column(db.String(100), unique=True, nullable=False)
    remark = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

HTML = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>UTR 检查工具</title>
</head>
<body>
  <h2>UTR 检查工具（数据库版）</h2>
  <input type="text" id="utrInput" placeholder="输入UTR">
  <input type="text" id="remarkInput" placeholder="备注（可选）">
  <button onclick="submitUTR()">提交</button>
  <button onclick="loadAll()">查看明细</button>
  <button onclick="deleteSelected()">删除所选</button>
  <button onclick="exportData()">导出 Excel</button>
  <input type="text" id="searchInput" placeholder="搜索UTR/备注" oninput="filterList()">
  <div id="message"></div>
  <ul id="utrList"></ul>
<script>
async function submitUTR() {
  const utr = document.getElementById('utrInput').value.trim();
  const remark = document.getElementById('remarkInput').value.trim();
  const res = await fetch('/submit', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({utr, remark})
  });
  const data = await res.json();
  document.getElementById('message').innerText = data.message;
  loadAll();
}
async function loadAll() {
  const res = await fetch('/all');
  const list = await res.json();
  const ul = document.getElementById('utrList');
  ul.innerHTML = '';
  for (const item of list) {
    const li = document.createElement('li');
    li.innerHTML = `
      <input type="checkbox" data-id="${item.id}"> 
      ${item.utr} - ${item.remark||''} (${item.created_at})
    `;
    ul.appendChild(li);
  }
}
async function deleteSelected(){
  const items = Array.from(document.querySelectorAll('#utrList input[type=checkbox]:checked'));
  const ids = items.map(i=>i.dataset.id);
  const res = await fetch('/delete', {
    method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ids})
  });
  const data = await res.json();
  document.getElementById('message').innerText = data.message;
  loadAll();
}
function filterList(){
  const kw = document.getElementById('searchInput').value.toLowerCase();
  document.querySelectorAll('#utrList li').forEach(li=>{
    li.style.display = li.innerText.toLowerCase().includes(kw) ? '' : 'none';
  });
}
function exportData(){
  window.location.href = '/export';
}
window.onload=loadAll;
</script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return render_template_string(HTML)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    utr = data.get('utr','').strip()
    remark = data.get('remark','').strip()
    if not utr:
        return jsonify({'message':'UTR不能为空'})
    if UTRRecord.query.filter_by(utr=utr).first():
        return jsonify({'message':'❌ UTR 已存在'})
    record = UTRRecord(utr=utr, remark=remark)
    db.session.add(record); db.session.commit()
    return jsonify({'message':'✅ 成功录入'})

@app.route('/all')
def all_utrs():
    recs = UTRRecord.query.order_by(UTRRecord.id.desc()).all()
    return jsonify([{'id':r.id,'utr':r.utr,'remark':r.remark,'created_at':r.created_at.strftime('%Y-%m-%d %H:%M:%S')} for r in recs])

@app.route('/delete', methods=['POST'])
def delete():
    ids = request.get_json().get('ids',[])
    for i in ids:
        r=UTRRecord.query.get(i)
        if r:
            db.session.delete(r)
    db.session.commit()
    return jsonify({'message':f'删除 {len(ids)} 条记录'})

@app.route('/export')
def export():
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active; ws.append(['UTR','备注','创建时间'])
    for r in UTRRecord.query.order_by(UTRRecord.id).all():
        ws.append([r.utr, r.remark or '', r.created_at.strftime('%Y-%m-%d %H:%M:%S')])
    from io import BytesIO
    buf=BytesIO(); wb.save(buf); buf.seek(0)
    return (buf.getvalue(), 200, {
      'Content-Type':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'Content-Disposition':'attachment; filename="utr_data.xlsx"'
    })

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=False)
