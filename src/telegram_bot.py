from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from models import db, UTR
from sqlalchemy.exc import SQLAlchemyError
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "你的真实 token"

async def query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("用法：/query <UTR>")
        return
    utr = context.args[0].strip()
    record = UTR.query.filter_by(utr=utr).first()
    if record:
        await update.message.reply_text(f"✅ 已存在\n备注: {record.remark}")
    else:
        await update.message.reply_text("❌ 未找到该 UTR")

async def add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("用法：/add <UTR> [备注]")
        return
    utr = context.args[0].strip()
    remark = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    if UTR.query.filter_by(utr=utr).first():
        await update.message.reply_text("⚠️ 该 UTR 已存在")
        return
    try:
        new_utr = UTR(utr=utr, remark=remark)
        db.session.add(new_utr)
        db.session.commit()
        await update.message.reply_text("✅ 添加成功")
    except SQLAlchemyError as e:
        await update.message.reply_text("❌ 添加失败，请稍后重试")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("欢迎使用 UTR 查询 Bot！\n使用 /query <UTR> 查询\n使用 /add <UTR> [备注] 添加")

# 🔄 修改：封装成创建 Application 的函数
async def create_bot_application():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("query", query_handler))
    app.add_handler(CommandHandler("add", add_handler))
    return app
