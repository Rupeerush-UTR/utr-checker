from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
from flask_sqlalchemy import SQLAlchemy
from main import db, UTR  # 使用你已有的模型
import os
from dotenv import load_dotenv

# 加载 .env 中的环境变量（可选）
load_dotenv()

# 替换成你的 Bot Token
TOKEN = "8180506085:AAGl-Lq_6U5ydstIcU5Ccj2MRE2fUDXwKkM"

def query(update, context):
    if len(context.args) != 1:
        update.message.reply_text("用法：/query <UTR>")
        return

    utr = context.args[0]
    existing = UTR.query.filter_by(utr=utr).first()
    if existing:
        update.message.reply_text(f"✅ 已存在记录：\nUTR: {existing.utr}\n备注: {existing.note or '无'}\n时间: {existing.created_at}")
    else:
        update.message.reply_text("❌ 未找到该 UTR。")

def add(update, context):
    if len(context.args) < 1:
        update.message.reply_text("用法：/add <UTR> [备注]")
        return

    utr = context.args[0]
    note = " ".join(context.args[1:]) if len(context.args) > 1 else None

    existing = UTR.query.filter_by(utr=utr).first()
    if existing:
        update.message.reply_text("⚠️ 已存在该 UTR，无法重复添加。")
        return

    new_record = UTR(utr=utr, note=note)
    db.session.add(new_record)
    db.session.commit()
    update.message.reply_text("✅ 添加成功！")

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("query", query))
    dp.add_handler(CommandHandler("add", add))

    updater.start_polling()
    updater.idle()
