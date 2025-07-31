# telegram_bot.py

from telegram.ext import ApplicationBuilder, CommandHandler
from models import db, UTR  # 通过 models.py 单独定义模型，避免循环导入

import os

TOKEN = os.getenv('BOT_TOKEN', '你的默认token')

async def query(update, context):
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /query <UTR>")
        return
    utr = context.args[0].strip()
    record = UTR.query.filter_by(utr=utr).first()
    if record:
        await update.message.reply_text(f"已存在\nUTR: {record.utr}\n备注: {record.note}")
    else:
        await update.message.reply_text("UTR 未找到")

async def add(update, context):
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /add <UTR> [备注]")
        return
    utr = context.args[0].strip()
    note = ' '.join(context.args[1:]) if len(context.args) > 1 else ''
    if UTR.query.filter_by(utr=utr).first():
        await update.message.reply_text("UTR 已存在")
        return
    new_record = UTR(utr=utr, note=note)
    db.session.add(new_record)
    db.session.commit()
    await update.message.reply_text("添加成功")

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("query", query))
    app.add_handler(CommandHandler("add", add))
    app.run_polling()
