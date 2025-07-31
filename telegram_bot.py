import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from models import db, UTR
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("欢迎使用 UTR 工具。使用 /add <UTR> <备注> 添加，/query <UTR> 查询。")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args:
            return await update.message.reply_text("请提供 UTR，例如：/add 1234567890 测试备注")

        utr = args[0].strip()
        note = " ".join(args[1:]).strip() if len(args) > 1 else ""

        if db.session.query(UTR).filter_by(utr=utr).first():
            return await update.message.reply_text("❌ 此 UTR 已存在")

        record = UTR(utr=utr, note=note)
        db.session.add(record)
        db.session.commit()
        await update.message.reply_text(f"✅ 添加成功：{utr}")
    except Exception as e:
        await update.message.reply_text(f"发生错误：{str(e)}")

async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args:
            return await update.message.reply_text("请输入要查询的 UTR，例如：/query 1234567890")

        utr = args[0].strip()
        record = db.session.query(UTR).filter_by(utr=utr).first()
        if record:
            return await update.message.reply_text(f"✅ 已存在记录：\nUTR: {record.utr}\n备注: {record.note}")
        else:
            return await update.message.reply_text("❌ 未找到记录")
    except Exception as e:
        await update.message.reply_text(f"发生错误：{str(e)}")

def run_bot():
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN 未设置")
        return

    # 显式创建事件循环（为线程兼容而加）
    asyncio.set_event_loop(asyncio.new_event_loop())
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("query", query))
    application.run_polling()
