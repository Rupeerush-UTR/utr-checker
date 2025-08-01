import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from models import db, UTR
from flask import current_app

TOKEN = "8180506085:AAGl-Lq_6U5ydstIcU5Ccj2MRE2fUDXwKkM"

# 查询指令
async def query_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("请提供要查询的 UTR，例如 /query 123456")
        return

    utr_code = context.args[0]
    with current_app.app_context():
        result = UTR.query.filter_by(utr=utr_code).first()
        if result:
            await update.message.reply_text(f"✅ 已存在：{utr_code}\n备注：{result.note or '无'}")
        else:
            await update.message.reply_text(f"❌ 未找到：{utr_code}")

# 添加指令
async def add_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("请提供要添加的 UTR，例如 /add 123456 [备注]")
        return

    utr_code = context.args[0]
    note = " ".join(context.args[1:]) if len(context.args) > 1 else ""

    with current_app.app_context():
        if UTR.query.filter_by(utr=utr_code).first():
            await update.message.reply_text(f"⚠️ 已存在：{utr_code}")
        else:
            new_utr = UTR(utr=utr_code, note=note)
            db.session.add(new_utr)
            db.session.commit()
            await update.message.reply_text(f"✅ 添加成功：{utr_code}")

# 启动 Bot
def run_bot():
    from main import app

    async def main():
        print("🤖 Telegram Bot 正在启动...")
        application = ApplicationBuilder().token(TOKEN).build()

        application.add_handler(CommandHandler("query", query_utr))
        application.add_handler(CommandHandler("add", add_utr))

        await application.run_polling()

    with app.app_context():
        asyncio.run(main())
