# telegram_bot.py
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from models import UTR, db

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("欢迎使用 UTR 查询和添加机器人。\n\n使用 /query <UTR> 查询\n使用 /add <UTR> [备注] 添加")

async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法：/query <UTR>")
        return

    utr = context.args[0].strip()
    result = UTR.query.filter_by(utr=utr).first()
    if result:
        await update.message.reply_text(f"✅ 已录入：\nUTR：{result.utr}\n备注：{result.note or '无'}")
    else:
        await update.message.reply_text("❌ 未查询到该 UTR")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法：/add <UTR> [备注]")
        return

    utr = context.args[0].strip()
    note = ' '.join(context.args[1:]) if len(context.args) > 1 else ''

    existing = UTR.query.filter_by(utr=utr).first()
    if existing:
        await update.message.reply_text("⚠️ 该 UTR 已存在")
        return

    new_utr = UTR(utr=utr, note=note)
    db.session.add(new_utr)
    db.session.commit()
    await update.message.reply_text(f"✅ 添加成功：{utr}")

def run_bot(app):
    async def start_bot():
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("query", query))
        application.add_handler(CommandHandler("add", add))

        print("🤖 Telegram bot 正在启动...")
        await application.run_polling()

    import asyncio
    asyncio.run(run_with_context(app, start_bot))

async def run_with_context(app, coro_func):
    with app.app_context():
        await coro_func()
