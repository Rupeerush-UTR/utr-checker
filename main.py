from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)

DB_FILE = 'utr_records.db'

# ✅ 自动初始化数据库
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utr_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utr TEXT UNIQUE NOT NULL,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ✅ 首页（查询 + 展示记录）
@app.route('/', methods=['GET'])
def index():
    query = request.args.get('query', '')
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if query:
        cursor.execute("SELECT * FROM utr_records WHERE utr LIKE ? ORDER BY id DESC", (f'%{query}%',))
    else:
        cursor.execute("SELECT * FROM utr_records ORDER BY id DESC")

    records = cursor.fetchall()
    conn.close()

    return render_template('index.html', records=records, query=query, message='')

# ✅ 单条录入
@app.route('/add', methods=['POST'])
def add():
    utr = request.form.get('utr').strip()
    note = request.form.get('note', '').strip()

    if not utr:
        return redirect('/')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utr_records WHERE utr = ?", (utr,))
    exists = cursor.fetchone()

    if exists:
        message = f"UTR {utr} 已存在"
    else:
        cursor.execute("INSERT INTO utr_records (utr, note) VALUES (?, ?)", (utr, note))
        conn.commit()
        message = f"UTR {utr} 录入成功"

    conn.close()
    return redirect(f"/?query={utr}")

# ✅ 删除记录
@app.route('/delete/<int:record_id>')
def delete(record_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM utr_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return redirect('/')

# ✅ 修改备注
@app.route('/update_note/<int:record_id>', methods=['POST'])
def update_note(record_id):
    note = request.form.get('note', '').strip()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE utr_records SET note = ? WHERE id = ?", (note, record_id))
    conn.commit()
    conn.close()
    return redirect('/')

# ✅ 导出 Excel
@app.route('/export')
def export():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM utr_records ORDER BY id DESC", conn)
    conn.close()

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='UTRs')
    output.seek(0)

    return send_file(output, download_name="utr_records.xlsx", as_attachment=True)

# ✅ 批量录入
@app.route('/batch_add', methods=['POST'])
def batch_add():
    content = request.form.get('batch_input', '')
    lines = content.strip().splitlines()
    added = 0
    skipped = 0

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for line in lines:
        if not line.strip():
            continue
        parts = line.strip().split(',')
        utr = parts[0].strip()
        note = parts[1].strip() if len(parts) > 1 else ''
        try:
            cursor.execute("INSERT INTO utr_records (utr, note) VALUES (?, ?)", (utr, note))
            added += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    conn.close()

    message = f"批量录入完成：新增 {added} 条，跳过 {skipped} 条（已存在）"
    return redirect(f"/?query=&message={message}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
