import secrets
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser
import logging
import time

logger = logging.getLogger(__name__)

# Словарь для хранения токенов
TEMP_TOKENS = {}


def login_page(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html', {'user': request.user})

    # Генерация токена
    token = secrets.token_urlsafe(16)
    TEMP_TOKENS[token] = None  # Сохраняем токен

    # Формируем ссылку для бота
    bot_link = f"https://t.me/auth_angry_bot?start={token}"
    return render(request, 'login.html', {'bot_link': bot_link})

def clean_expired_tokens():
    """Удаляем токены старше 10 минут"""
    current_time = time.time()
    for token, created_time in list(TEMP_TOKENS.items()):
        if created_time is not None and current_time - created_time > 600:  # 10 минут
            del TEMP_TOKENS[token]

@csrf_exempt
def link_telegram(request):
    try:
        if request.method == 'POST':
            telegram_id = request.POST.get('telegram_id')
            telegram_username = request.POST.get('telegram_username')
            token = request.POST.get('token')

            logger.info(f"Получен запрос: telegram_id={telegram_id}, telegram_username={telegram_username}, token={token}")

            # Проверка токена
            if token in TEMP_TOKENS:
                user = CustomUser.objects.filter(telegram_id=telegram_id).first()
                if not user:
                    user = CustomUser.objects.create_user(
                        username=telegram_username or f'tg_user_{telegram_id}',
                        telegram_id=telegram_id,
                        telegram_username=telegram_username,
                        password=secrets.token_urlsafe(16),
                    )
                TEMP_TOKENS[token] = user
                logger.info(f"Пользователь {user.username} успешно связан с Telegram ID {telegram_id}")
                return JsonResponse({'status': 'ok'})

            # Ошибка: токен не найден
            logger.warning(f"Токен {token} не найден в TEMP_TOKENS.")
            return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=400)

        # Ошибка: неверный метод запроса
        logger.error("Получен неверный метод запроса.")
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    except Exception as e:
        # Логирование ошибок
        logger.error(f"Ошибка при обработке запроса: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)