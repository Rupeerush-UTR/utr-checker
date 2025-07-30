from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

# 存储：UTR -> 备注
utr_dict = {}

# HTML 页面
HTML = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>UTR 检查工具</title>
</head>
<body>
  <h2>UTR 检查工具</h2>
  <input id="utr" placeholder="UTR">
  <input id="note" placeholder="备注">
  <button onclick="submit()">提交</button>
  <br><br>

  <textarea id="bulk" rows="5" cols="40" placeholder="多个UTR查询，用换行或逗号分隔"></textarea>
  <br>
  <button onclick="bulkCheck()">批量查询</button>
  <button onclick="showAll()">查看明细</button>

  <pre id="result"></pre>

<script>
async function submit() {
  const utr = document.getElementById("utr").value.trim();
  const note = document.getElementById("note").value.trim();
  const res = await fetch("/check", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ utr, note })
  });
  const data = await res.json();
  document.getElementById("result").innerText = data.message;
}

async function bulkCheck() {
  const text = document.getElementById("bulk").value;
  const list = text.split(/[\n,]+/).map(s => s.trim()).filter(s => s);
  const res = await fetch("/batch", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ utrs: list })
  });
  const data = await res.json();
  document.getElementById("result").innerText = data.results.join("\\n");
}

async function showAll() {
  const res = await fetch("/all");
  const data = await res.json();
  let output = "全部已录入UTR明细：\\n";
  for (const [utr, note] of Object.entries(data)) {
    output += `- ${utr}：${note}\\n`;
  }
  document.getElementById("result").innerText = output;
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
    note = data.get('note', '').strip()
    if not utr:
        return jsonify({"message": "❌ 请输入有效的 UTR"})
    if utr in utr_dict:
        return jsonify({"message": f"❌ 已存在重复 UTR: {utr}"})
    utr_dict[utr] = note or "-"
    return jsonify({"message": f"✅ UTR {utr} 已成功录入，备注：{utr_dict[utr]}"})

@app.route('/batch', methods=['POST'])
def batch_check():
    data = request.get_json()
    utrs = data.get('utrs', [])
    results = []
    for utr in utrs:
        utr = utr.strip()
        if not utr:
            continue
        if utr in utr_dict:
            results.append(f"❌ 已存在重复：{utr}")
        else:
            utr_dict[utr] = "-"
            results.append(f"✅ 新录入：{utr}")
    return jsonify({"results": results})

@app.route('/all')
def all_utrs():
    return jsonify(utr_dict)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
