import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# --- AI Chat Function ---
# Please install OpenAI SDK first: `pip3 install openai`
PROMPT = '''
按照这段描述来分析以下数据。
描述：在 {{Date}}，{{Chain}} 链上发生了一笔交易。资金从 {{From}} (地址: {{FromAddress}}) 转移到了 {{To}} (地址: {{ToAddress}})。这笔交易涉及 {{Amount}}  {{Token}} 代币，总价值约为 {{Value}} 美元。操作类型为 {{Action}}，当时的价格是 {{Price}} 美元。
从用户输入中寻找对应的字段，如果找不到则省略对应的话，可能输入有多条，以最后一条为准，向前找关联交易，也就是FromAddress或者ToAddress与最后一条数据的FromAddress或者ToAddress相同的数据，最后来一个总结将资金路由描述清楚'''

def deepseek_chat(text: str, prompt: str = PROMPT) -> str:
    client = OpenAI(api_key=os.getenv("DS_APIKEY"), base_url=os.getenv("DS_BASE_URL"))

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        stream=False
    )

    return response.choices[0].message.content

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the command /start is issued."""
    await update.message.reply_text("Hi! I am an AI assistant. Ask me anything.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages by passing them to the AI chat function."""
    user_message = update.message.text
    ai_response = deepseek_chat(user_message)
    await update.message.reply_text(ai_response)


def main() -> None:
    """Start the bot."""
    # Get the token from environment variable
    token = os.getenv("TGBOT_APIKEY")
    if not token:
        raise ValueError("No TGBOT_APIKEY found in environment variables")
    
    if not os.getenv("DS_APIKEY") or not os.getenv("DS_BASE_URL"):
        raise ValueError("DS_APIKEY or DS_BASE_URL not found in environment variables")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - use the AI chat function
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()