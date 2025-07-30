from flask import Flask, request, jsonify, render_template_string, send_file
import os
import io
import csv

app = Flask(__name__)

# 内存中存储UTR和备注
utr_data = []  # 每项为 dict: {"utr": ..., "remark": ...}

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
  <input type="text" id="remarkInput" placeholder="备注（可选）">
  <button onclick="submitUTR()">提交</button>
  <button onclick="bulkCheck()">批量提交</button>
  <button onclick="showAll()">查看明细</button>
  <button onclick="exportCSV()">导出Excel</button>
  <br><br>
  <textarea id="bulkInput" placeholder="一行一个UTR，可附备注，用英文逗号分隔"></textarea>
  <br><br>
  <input type="text" id="searchInput" oninput="searchData()" placeholder="搜索UTR或备注">
  <div id="result"></div>
  <ul id="utrList"></ul>

<script>
  async function submitUTR() {
    const utr = document.getElementById('utrInput').value.trim();
    const remark = document.getElementById('remarkInput').value.trim();
    const res = await fetch('/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ utr, remark })
    });
    const data = await res.json();
    document.getElementById('result').innerText = data.message;
  }

  async function bulkCheck() {
    const lines = document.getElementById('bulkInput').value.trim().split('\n');
    const list = [];
    for (const line of lines) {
      if (line.trim()) {
        const [utr, remark] = line.split(',').map(x => x.trim());
        list.push({ utr, remark: remark || '' });
      }
    }
    const res = await fetch('/bulk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ list })
    });
    const data = await res.json();
    document.getElementById('result').innerText = data.message;
  }

  async function showAll() {
    const res = await fetch('/list');
    const data = await res.json();
    const ul = document.getElementById('utrList');
    ul.innerHTML = '';
    data.forEach(item => {
      const li = document.createElement('li');
      li.innerText = `${item.utr} - ${item.remark}`;
      ul.appendChild(li);
    });
  }

  async function exportCSV() {
    window.location.href = '/export';
  }

  function searchData() {
    const keyword = document.getElementById('searchInput').value.toLowerCase();
    const items = document.querySelectorAll('#utrList li');
    items.forEach(li => {
      li.style.display = li.innerText.toLowerCase().includes(keyword) ? '' : 'none';
    });
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
    if any(x['utr'] == utr for x in utr_data):
        return jsonify({"message": f"❌ 已存在重复 UTR: {utr}"})
    utr_data.append({"utr": utr, "remark": remark})
    return jsonify({"message": f"✅ UTR {utr} 已成功录入，无重复。"})

@app.route('/bulk', methods=['POST'])
def bulk_check():
    data = request.get_json()
    added = 0
    for item in data.get('list', []):
        utr = item.get('utr', '').strip()
        remark = item.get('remark', '').strip()
        if utr and not any(x['utr'] == utr for x in utr_data):
            utr_data.append({"utr": utr, "remark": remark})
            added += 1
    return jsonify({"message": f"✅ 成功录入 {added} 个新UTR"})

@app.route('/list')
def get_list():
    return jsonify(utr_data)

@app.route('/export')
def export():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["utr", "remark"])
    writer.writeheader()
    writer.writerows(utr_data)
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', download_name='utr_data.csv', as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
