import asyncio
import json

from telegram import Bot, Update

from telegram_agent_aws.config import settings
from telegram_agent_aws.infrastructure.telegram.handlers import handle_photo, handle_text, handle_voice


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


async def lambda_handler(event, context):
    """
    AWS Lambda handler for Telegram webhook.

    The event contains the API Gateway payload with the Telegram update in the body.
    """
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

        # --- INICIO DEL ARREGLO ---
        # Comprobar si ya hay un bucle de eventos en ejecución (como el de Uvicorn)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None  # No hay bucle en ejecución

        if loop and loop.is_running():
            # Estamos en un entorno async (ej. Uvicorn), usamos 'await'
            print("--- Running in async loop (await) ---")
            await process_update(update_data)
        else:
            # Estamos en un entorno sync (ej. AWS Lambda), usamos 'asyncio.run'
            print("--- Running in sync context (asyncio.run) ---")
            asyncio.run(process_update(update_data))
        # --- FIN DEL ARREGLO ---

        return {"statusCode": 200, "body": json.dumps({"ok": True})}

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        import traceback

        traceback.print_exc()

        return {"statusCode": 500, "body": json.dumps({"ok": False, "error": str(e)})}
