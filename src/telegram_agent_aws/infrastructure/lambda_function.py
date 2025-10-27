import asyncio
import json

from telegram import Bot, Update

from telegram_agent_aws.config import settings
from telegram_agent_aws.infrastructure.telegram.handlers import handle_photo, handle_text, handle_voice

# ¡IMPORTANTE! Mueve la configuración de Opik de __init__.py aquí
# para evitar el 'init timeout' (Este sigue siendo un buen cambio).
from telegram_agent_aws.infrastructure.opik_utils import configure
_OPIK_CONFIGURED = False


# Esta función sigue siendo ASÍNCRONA
async def process_update(update_data: dict):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    update = Update.de_json(update_data, bot=bot)

    class WebhookContext:
        def __init__(self, bot):
            self.bot = bot

    context = WebhookContext(bot)

    try:
        if update.message:
            if update.message.text:
                await handle_text(update, context)
            elif update.message.voice:
                await handle_voice(update, context)
            elif update.message.photo:
                await handle_photo(update, context)
            else:
                await update.message.reply_text("Sorry, I don't support this message type yet.")
        else:
            print("Update doesn't contain a message")
    except Exception as e:
        print(f"Error processing update: {e}")
        if update.message:
            try:
                await update.message.reply_text("Sorry, something went wrong processing your message.")
            except Exception as reply_error:
                print(f"Failed to send error message: {reply_error}")
        raise
    finally:
        await bot.shutdown()


# Esta función vuelve a ser SÍNCRONA
def lambda_handler(event, context):
    global _OPIK_CONFIGURED

    if not _OPIK_CONFIGURED:
        print("--- Running Opik/Comet configuration (first invocation only) ---")
        configure()
        _OPIK_CONFIGURED = True

    print("**Event received**")
    print(json.dumps(event, indent=2))

    try:
        body = event.get("body", "{}")

        if isinstance(body, str):
            update_data = json.loads(body)
        else:
            update_data = body

        print("**Parsed update data**")
        print(json.dumps(update_data, indent=2))

        # --- LA CLAVE ---
        # Usamos asyncio.run() para ejecutar nuestro código async
        # Esto funciona en Lambda (que es síncrona)
        # Y ahora también funciona en local (gracias a nest_asyncio)
        asyncio.run(process_update(update_data))

        return {"statusCode": 200, "body": json.dumps({"ok": True})}

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        import traceback
        traceback.print_exc()

        return {"statusCode": 500, "body": json.dumps({"ok": False, "error": str(e)})}
