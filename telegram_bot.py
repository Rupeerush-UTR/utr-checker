import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from models import db, UTR
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ 格式错误：/query <UTR>")
        return
    utr = context.args[0].strip()
    record = UTR.query.filter_by(utr=utr).first()
    if record:
        await update.message.reply_text(f"✅ 已存在：{utr}\n备注：{record.remark}")
    else:
        await update.message.reply_text(f"❌ 未找到：{utr}")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ 格式错误：/add <UTR> [备注]")
        return
    utr = context.args[0].strip()
    remark = " ".join(context.args[1:]).strip() if len(context.args) > 1 else ""
    if UTR.query.filter_by(utr=utr).first():
        await update.message.reply_text("⚠️ 此 UTR 已存在")
        return
    new_utr = UTR(utr=utr, remark=remark, timestamp=datetime.utcnow())
    db.session.add(new_utr)
    db.session.commit()
    await update.message.reply_text(f"✅ 添加成功：{utr}")

def create_bot_app():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("query", query))
    application.add_handler(CommandHandler("add", add))
    return application
