# telegram_bot.py

from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio
from models import db, UTR
from datetime import datetime
import os

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '你的bot token放这里')

async def query(update, context):
    if len(context.args) == 0:
        await update.message.reply_text("请输入 UTR，如：/query 123456")
        return
    utr = context.args[0].strip()
    record = UTR.query.filter_by(utr=utr).first()
    if record:
        await update.message.reply_text(f"UTR 已存在\n备注: {record.note}")
    else:
        await update.message.reply_text("UTR 未录入")

async def add(update, context):
    if len(context.args) == 0:
        await update.message.reply_text("请输入 UTR，如：/add 123456 备注可选")
        return
    utr = context.args[0].strip()
    note = " ".join(context.args[1:]) if len(context.args) > 1 else ''
    if UTR.query.filter_by(utr=utr).first():
        await update.message.reply_text("UTR 已存在")
    else:
        new_record = UTR(utr=utr, note=note)
        db.session.add(new_record)
        db.session.commit()
        await update.message.reply_text("UTR 添加成功")

def run_bot():
    async def main():
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("query", query))
        application.add_handler(CommandHandler("add", add))
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        await application.idle()

    asyncio.run(main())
