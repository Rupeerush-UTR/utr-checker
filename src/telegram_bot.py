import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from models import db, UTR

# 从环境变量中读取 Telegram Token（Render 后台设置）
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def query_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("请提供要查询的UTR，例如：/query 123456")
        return

    utr = context.args[0]
    match = UTR.query.filter_by(utr=utr).first()
    if match:
        await update.message.reply_text(f"✅ 已存在：{utr}（备注：{match.remark}）")
    else:
        await update.message.reply_text(f"❌ 未找到：{utr}")

async def add_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("请提供UTR，例如：/add 123456 备注内容")
        return

    utr = context.args[0]
    remark = " ".join(context.args[1:]) if len(context.args) > 1 else ""

    existing = UTR.query.filter_by(utr=utr).first()
    if existing:
        await update.message.reply_text("⚠️ 已存在该UTR！")
    else:
        new_utr = UTR(utr=utr, remark=remark)
        db.session.add(new_utr)
        db.session.commit()
        await update.message.reply_text("✅ 添加成功！")

def run_bot():
    import asyncio
    from flask import Flask
    from main import app
    from telegram.ext import ApplicationBuilder, CommandHandler
    from telegram.commands import query_utr, add_utr

    async def main():
        print("🚀 Telegram bot 正在启动...")
        application = ApplicationBuilder().token(TOKEN).build()

        application.add_handler(CommandHandler("query", query_utr))
        application.add_handler(CommandHandler("add", add_utr))

        await application.run_polling()  # ✅ 改成这行，自动完成所有初始化、启动、监听、阻塞

    with app.app_context():
        asyncio.run(main())
