from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

# 保存UTR的文件路径
UTR_FILE = "utrs.txt"

# 内存中存储UTR集合
utr_set = set()

# 启动时从文件加载UTR
if os.path.exists(UTR_FILE):
    with open(UTR_FILE, 'r') as f:
        for line in f:
            utr_set.add(line.strip())

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
  <button onclick="submitUTR()">提交</button>
  <p id="result"></p>

  <script>
    async function submitUTR() {
      const utr = document.getElementById('utrInput').value.trim();
      if (!utr) {
        document.getElementById('result').innerText = "请输入有效的UTR";
        return;
      }
      const res = await fetch('/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ utr })
      });
      const data = await res.json();
      document.getElementById('result').innerText = data.message;
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
    if not utr:
        return jsonify({"message": "请输入有效的UTR"})
    if utr in utr_set:
        return jsonify({"message": f"❌ 已存在重复 UTR: {utr}"})
    else:
        utr_set.add(utr)
        with open(UTR_FILE, 'a') as f:
            f.write(utr + '\n')
        return jsonify({"message": f"✅ UTR {utr} 已成功录入，无重复。"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
