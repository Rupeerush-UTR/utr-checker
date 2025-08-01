from flask import Flask, render_template_string
from models import db, UTR
from telegram_bot import run_telegram_bot

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://utr_sj_user:l1QGJqrMyxksukna0QhZrhbfL9RbywAz@dpg-d24ui7vdiees739mrel0-a.oregon-postgres.render.com/utr_sj'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    utrs = UTR.query.order_by(UTR.timestamp.desc()).all()
    return render_template_string("""
        <h1>UTR 记录</h1>
        <ul>
            {% for utr in utrs %}
                <li>{{ utr.utr }} - {{ utr.remark or '' }} - {{ utr.timestamp }}</li>
            {% endfor %}
        </ul>
    """, utrs=utrs)

if __name__ == '__main__':
    run_telegram_bot()
    app.run(host='0.0.0.0', port=10000)
