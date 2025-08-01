# telegram_bot.py

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from models import db, UTR
from sqlalchemy.exc import SQLAlchemyError
import os

# 读取环境变量
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# 查询 UTR
async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❗ 格式错误：使用 /query <UTR>")
        return

    utr_value = context.args[0]
    try:
        utr_record = UTR.query.filter_by(utr=utr_value).first()
        if utr_record:
            await update.message.reply_text(f"✅ 已存在：{utr_record.utr}\n备注：{utr_record.remark}")
        else:
            await update.message.reply_text("❌ 未找到该 UTR。")
    except SQLAlchemyError as e:
        await update.message.reply_text("⚠️ 查询数据库出错。")

# 添加 UTR
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("❗ 格式错误：使用 /add <UTR> [备注]")
        return

    utr_value = context.args[0]
    remark = " ".join(context.args[1:]) if len(context.args) > 1 else ""

    try:
        existing = UTR.query.filter_by(utr=utr_value).first()
        if existing:
            await update.message.reply_text("⚠️ 已存在该 UTR，无需重复添加。")
        else:
            new_utr = UTR(utr=utr_value, remark=remark)
            db.session.add(new_utr)
            db.session.commit()
            await update.message.reply_text("✅ 添加成功。")
    except SQLAlchemyError:
        db.session.rollback()
        await update.message.reply_text("⚠️ 添加失败，数据库错误。")

# 主启动函数
async def run_bot():
    if not TELEGRAM_TOKEN:
        print("❌ 未找到 TELEGRAM_TOKEN 环境变量！")
        return

    print("🤖 Telegram Bot 开始启动并监听中...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("query", query))
    app.add_handler(CommandHandler("add", add))

    await app.run_polling()
