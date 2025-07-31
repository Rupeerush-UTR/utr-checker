import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from models import db, UTR
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("欢迎使用 UTR 工具。\n使用 /add <UTR> <备注> 添加\n使用 /query <UTR> 查询")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        return await update.message.reply_text("请输入要查询的 UTR，例如：/query 1234567890")

    utr = args[0].strip()
    record = db.session.query(UTR).filter_by(utr=utr).first()
    if record:
        return await update.message.reply_text(f"✅ 记录存在：\nUTR: {record.utr}\n备注: {record.note}")
    else:
        return await update.message.reply_text("❌ 没找到该记录")

def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN 未设置（.env 文件里）")
        return

    print("✅ 正在启动 Telegram Bot...")

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("query", query))
    application.run_polling(close_loop=False)  # 防止 Flask+线程环境中异常
