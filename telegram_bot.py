from dotenv import load_dotenv
load_dotenv()

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from models import db, UTR

# 获取 Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 启用日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start 命令处理
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 欢迎使用 UTR 工具机器人！\n\n使用以下命令：\n/query <UTR> - 查询是否已存在\n/add <UTR> <备注> - 添加新的 UTR")

# /query 命令处理
async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ 请提供要查询的 UTR，例如：/query 123456")
        return

    utr_value = context.args[0].strip()
    record = UTR.query.filter_by(utr=utr_value).first()
    if record:
        await update.message.reply_text(f"✅ 记录已存在\n备注：{record.note}")
    else:
        await update.message.reply_text("❌ 未找到此 UTR 记录")

# /add 命令处理
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("❗ 用法：/add <UTR> [备注]")
        return

    utr_value = context.args[0].strip()
    note = " ".join(context.args[1:]) if len(context.args) > 1 else ""

    existing = UTR.query.filter_by(utr=utr_value).first()
    if existing:
        await update.message.reply_text("⚠️ 此 UTR 已存在")
    else:
        new_record = UTR(utr=utr_value, note=note)
        db.session.add(new_record)
        db.session.commit()
        await update.message.reply_text("✅ UTR 添加成功")

# 启动 Telegram Bot
def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN 环境变量未设置")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("query", query))
    application.add_handler(CommandHandler("add", add))

    application.run_polling()
