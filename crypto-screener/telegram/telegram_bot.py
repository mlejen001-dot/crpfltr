from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN

import sys
import os

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.insert(0, ROOT)

from app import run_screening

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Scanning...")

    result = run_screening()

    await update.message.reply_text(result)
    

from coin_analyzer import (
    analyze_coin,
    compute_verdict,
    analysis_to_text,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Crypto Analyzer Ready"
    )


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("Analyze command received")

    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage:\n/analyze BTCUSDT"
        )
        return

    symbol = context.args[0].upper()

    print(symbol)

    await update.message.reply_text(
        "Running analysis..."
    )

    result = analyze_coin(symbol)

    verdict = compute_verdict(result)

    text = analysis_to_text(result, verdict)

    await update.message.reply_text(
        f"<pre>{text}</pre>",
        parse_mode="HTML"
    )



app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))
app.add_handler(CommandHandler("scan", scan))

print("Bot running...")

app.run_polling()
