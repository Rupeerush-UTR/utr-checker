from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from models import db, UTR

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法：/query <UTR>")
        return
    utr = context.args[0].strip()
    record = UTR.query.filter_by(utr=utr).first()
    if record:
        await update.message.reply_text(f"✅ 该 UTR 已存在\n备注: {record.remark or '无'}")
    else:
        await update.message.reply_text("❌ 未找到该 UTR")

async def handle_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法：/add <UTR> [备注]")
        return
    utr = context.args[0].strip()
    remark = ' '.join(context.args[1:]).strip() if len(context.args) > 1 else ''

    if UTR.query.filter_by(utr=utr).first():
        await update.message.reply_text("⚠️ 该 UTR 已存在，无法重复添加")
        return

    new_utr = UTR(utr=utr, remark=remark)
    db.session.add(new_utr)
    db.session.commit()
    await update.message.reply_text("✅ 添加成功")

async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("query", handle_query))
    app.add_handler(CommandHandler("add", handle_add))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
