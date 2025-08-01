from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from models import db, UTR
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def run_bot(app):
    application = Application.builder().token(TOKEN).build()

    async def query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("用法：/query <UTR>")
            return
        query_utr = context.args[0]
        with app.app_context():
            result = UTR.query.filter_by(utr=query_utr).first()
            if result:
                await update.message.reply_text(f"UTR 已存在，备注：{result.remark}")
            else:
                await update.message.reply_text("UTR 不存在")

    async def add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("用法：/add <UTR> [备注]")
            return
        new_utr = context.args[0]
        remark = " ".join(context.args[1:]) if len(context.args) > 1 else ""
        with app.app_context():
            if UTR.query.filter_by(utr=new_utr).first():
                await update.message.reply_text("UTR 已存在，不能重复添加")
            else:
                utr_entry = UTR(utr=new_utr, remark=remark)
                db.session.add(utr_entry)
                db.session.commit()
                await update.message.reply_text("UTR 添加成功")

    application.add_handler(CommandHandler("query", query_handler))
    application.add_handler(CommandHandler("add", add_handler))

    application.run_polling()
