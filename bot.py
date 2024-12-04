from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import logging

# Настройка токена и адреса вашего Django-сервера
BOT_TOKEN = '7961338814:AAHWEbaJLfcUpstN0tSdPIJih-klHgGhITI'
DJANGO_SERVER_URL = 'http://127.0.0.1:8000/auth/link_telegram/'

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    try:
        token = update.message.text.split(" ")[1]  # предполагается, что токен передается после команды /start
    except IndexError:
        await update.message.reply_text("Пожалуйста, укажите токен после команды /start.")
        logger.warning(f"Пользователь {user.id} вызвал команду /start без токена.")
        return

    try:
        # Отправка POST-запроса на сервер Django
        response = requests.post(DJANGO_SERVER_URL, data={
            'telegram_id': user.id,
            'telegram_username': user.username,
            'token': token,
        })

        # Проверка ответа
        if response.status_code == 200:
            try:
                response_data = response.json()  # Попытка получить JSON
                if response_data.get('status') == 'ok':
                    await update.message.reply_text(f"Ваш аккаунт {user.username} успешно связан!")
                    logger.info(f"Пользователь {user.id} успешно связал аккаунт.")
                else:
                    message = response_data.get('message', 'Неизвестная ошибка.')
                    await update.message.reply_text(f"Ошибка при связывании аккаунта: {message}")
                    logger.error(f"Ошибка при связывании: {message}")
            except ValueError:
                await update.message.reply_text("Ошибка: сервер вернул некорректный ответ.")
                logger.error(f"Некорректный ответ от сервера: {response.text}")
        else:
            await update.message.reply_text(f"Ошибка при связывании аккаунта. Код: {response.status_code}")
            logger.error(f"Ошибка при запросе: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        await update.message.reply_text("Произошла ошибка при подключении к серверу.")
        logger.error(f"Ошибка запроса к серверу Django: {e}", exc_info=True)

def main():
    """
    Основная функция для запуска бота.
    """
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler('start', start))

    # Запускаем бота
    logger.info("Бот запущен.")
    application.run_polling()

if __name__ == '__main__':
    main()
