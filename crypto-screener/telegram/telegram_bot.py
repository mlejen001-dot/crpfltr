```python
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

from coin_analyzer import analyze_coin


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Crypto Analyzer Ready"
    )


```python
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

    print(result)

    await update.message.reply_text(
        str(result["score"])
    )
```


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))

print("Bot running...")

app.run_polling()
