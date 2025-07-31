import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from database import add_utr, query_utr

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("欢迎使用 UTR 查询工具！")

async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法：/query <UTR>")
        return
    utr = context.args[0]
    record = query_utr(utr)
    if record:
        await update.message.reply_text(f"✅ 已存在\n备注：{record.remark or '无'}\n时间：{record.timestamp}")
    else:
        await update.message.reply_text("❌ 未找到")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法：/add <UTR> [备注]")
        return
    utr = context.args[0]
    remark = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    success = add_utr(utr, remark)
    if success:
        await update.message.reply_text("✅ 添加成功")
    else:
        await update.message.reply_text("⚠️ 该 UTR 已存在")

def run_bot():
    print("🤖 Telegram bot 正在启动...")
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("query", query))
    application.add_handler(CommandHandler("add", add))

    application.run_polling()
