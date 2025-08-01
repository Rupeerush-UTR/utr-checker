from telegram.ext import ApplicationBuilder, CommandHandler
from models import db, UTR
import os

async def start(update, context):
    await update.message.reply_text("欢迎使用 UTR 工具！")

async def query(update, context):
    if len(context.args) < 1:
        await update.message.reply_text("请输入要查询的 UTR，例如 /query ABC123")
        return

    search = context.args[0]
    result = UTR.query.filter_by(utr=search).first()

    if result:
        await update.message.reply_text(f"UTR 已存在，备注：{result.note or '无'}")
    else:
        await update.message.reply_text("未找到该 UTR。")

async def add(update, context):
    if len(context.args) < 1:
        await update.message.reply_text("请输入要添加的 UTR，例如 /add ABC123 [备注]")
        return

    utr_value = context.args[0]
    note = ' '.join(context.args[1:]) if len(context.args) > 1 else ''

    existing = UTR.query.filter_by(utr=utr_value).first()
    if existing:
        await update.message.reply_text("该 UTR 已存在，不能重复添加。")
    else:
        new_utr = UTR(utr=utr_value, note=note)
        db.session.add(new_utr)
        db.session.commit()
        await update.message.reply_text("添加成功！")

async def start_bot(app):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("query", query))
    application.add_handler(CommandHandler("add", add))

    await application.initialize()
    await application.start()
    print("Telegram bot running...")
    await application.updater.start_polling()
    await application.updater.idle()
