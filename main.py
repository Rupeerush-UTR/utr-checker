from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

# 保存UTR的文件路径
UTR_FILE = "utrs.txt"

# 内存中存储UTR集合和明细
utr_dict = {}  # {utr: remark}

# 启动时从文件加载UTR
if os.path.exists(UTR_FILE):
    with open(UTR_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(',', 1)
            utr = parts[0]
            remark = parts[1] if len(parts) > 1 else ""
            utr_dict[utr] = remark

# 简易HTML页面
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
  <p id="result"></p>

  <h3>批量查询</h3>
  <textarea id="batchInput" placeholder="每行一个UTR" rows="6" cols="40"></textarea><br>
  <button onclick="batchQuery()">批量查询</button>
  <pre id="batchResult"></pre>

  <h3>查看所有明细</h3>
  <button onclick="fetchAll()">查看明细</button>
  <pre id="allData"></pre>

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

    async function batchQuery() {
      const lines = document.getElementById('batchInput').value.trim().split('\n');
      const res = await fetch('/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ utrs: lines })
      });
      const data = await res.json();
      document.getElementById('batchResult').innerText = data.result.join('\n');
    }

    async function fetchAll() {
      const res = await fetch('/all');
      const data = await res.json();
      document.getElementById('allData').innerText = data.all.join('\n');
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
    if utr in utr_dict:
        return jsonify({"message": f"❌ 已存在重复 UTR: {utr}"})
    else:
        utr_dict[utr] = remark
        with open(UTR_FILE, 'a') as f:
            f.write(f"{utr},{remark}\n")
        return jsonify({"message": f"✅ UTR {utr} 已成功录入，无重复。"})

@app.route('/batch', methods=['POST'])
def batch_check():
    data = request.get_json()
    utrs = data.get('utrs', [])
    result = []
    for utr in utrs:
        utr = utr.strip()
        if not utr:
            continue
        if utr in utr_dict:
            result.append(f"❌ 重复: {utr}（备注: {utr_dict[utr]}）")
        else:
            result.append(f"✅ 不重复: {utr}")
    return jsonify({"result": result})

@app.route('/all')
def all_data():
    all_list = [f"{utr} | 备注: {remark}" for utr, remark in utr_dict.items()]
    return jsonify({"all": all_list})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
