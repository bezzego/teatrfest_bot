"""Скрипт для обмена кода авторизации на токены AmoCRM

Использование:
    python scripts/exchange_auth_code.py

Скрипт обменивает код авторизации на access_token и refresh_token
"""
import asyncio
import sys
import os
import aiohttp
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import setup_logger

logger = setup_logger(__name__)


async def exchange_auth_code(subdomain: str, client_id: str, client_secret: str, auth_code: str, redirect_uri: str):
    """Обменять код авторизации на токены
    
    Args:
        subdomain: Поддомен AmoCRM
        client_id: Client ID
        client_secret: Client Secret
        auth_code: Код авторизации
        redirect_uri: Redirect URI
    """
    url = f"https://{subdomain}.amocrm.ru/oauth2/access_token"
    
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri
    }
    
    logger.info(f"Обмен кода авторизации для {subdomain}.amocrm.ru...")
    logger.debug(f"URL: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Токены успешно получены для {subdomain}")
                    return {
                        "access_token": result.get("access_token"),
                        "refresh_token": result.get("refresh_token"),
                        "expires_in": result.get("expires_in")
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка обмена кода: статус {response.status}")
                    logger.error(f"Ответ: {error_text}")
                    return None
    except Exception as e:
        logger.error(f"❌ Исключение при обмене кода: {e}", exc_info=True)
        return None


async def main():
    """Главная функция"""
    logger.info("=" * 60)
    logger.info("ОБМЕН КОДА АВТОРИЗАЦИИ НА ТОКЕНЫ AMOCRM (АТЛАНТ)")
    logger.info("=" * 60)
    
    # Данные для АТЛАНТ
    subdomain = "tugolukov"
    client_id = "f161382c-13bc-43be-899e-35b4c723f4b9"
    client_secret = "o1kzAqJJJVtSU3PyitXHknZTlkLfpjpfYmwWRkpTPPD1zusud4J5if0XMfmn7Cu0"
    auth_code = "def50200a680b0f8896f97f1a18c08aafc18b618834335a4db3771ef55b7ae3089f2289800bda3dbc9640f2bc0a8f8c30e96c61e59b67fc2e7fda95a1ba5022944148e778edcdb4b282902bfdd9a2bf7215ae42c8b64abcfc5d55f9d6913a5a43daafd31b8af0c2ab646b071b2a5e206dd3a5a818d968c2c415a3a91fd4b40082c185f1ed30604de62c9ab77ac43ecd6202983b9a7ef24270db1f84aa0bfeb979d044796c27fa093bd1ecf6d9f8dc23bd4f88bda4776832bea56e047e4392221831c2adf7b18ca11669aa8599358c5762b330863506a8c2fe33801b010872d483699f8da9cfc7d463897d02e56f1a413eb7731a255565440297b30e570c401b33e93ef9fcb9bf439593e5cc6ee1a3c5364de35a594dcbe968f7cfc09a27393bdff9e7d6346dbf020570470a7e5b6e003b1e652335462aeab1a753cd0b42b4c278ecbc53abf24d2c58eede65b80d833eced6b1fde547bd4f1673394e61fb8168aecebcfb255b9ea7bca933fc9f61087d15e4dbfb74424321c11b23e402c3c9c3a74842c8cdd531bf1836ba0c0fe4140c9a1620aa05eaf8a933f5abf29e5ebe31ef0a96a70ace040dc1047f258867bdee243e71b1f8ed62aa1e96a4941b1c57c3859a4af6afbf562208a00222f1415b9ef7927045bae483044276aa57742"
    
    # Redirect URI нужно указать тот же, что был при получении кода
    # Обычно это https://ya.ru или другой URI из настроек интеграции
    redirect_uri = "https://ya.ru"  # Замените на ваш redirect_uri если отличается
    
    logger.info(f"Subdomain: {subdomain}")
    logger.info(f"Client ID: {client_id[:20]}...")
    logger.info(f"Redirect URI: {redirect_uri}")
    
    result = await exchange_auth_code(subdomain, client_id, client_secret, auth_code, redirect_uri)
    
    if result:
        logger.info("\n" + "=" * 60)
        logger.info("✅ ТОКЕНЫ УСПЕШНО ПОЛУЧЕНЫ")
        logger.info("=" * 60)
        logger.info("\n📝 Обновите следующие строки в .env файле:")
        logger.info("-" * 60)
        logger.info(f"AMOCRM_CITY1_CLIENT_ID={client_id}")
        logger.info(f"AMOCRM_CITY1_CLIENT_SECRET={client_secret}")
        logger.info(f"AMOCRM_CITY1_ACCESS_TOKEN={result['access_token']}")
        logger.info(f"AMOCRM_CITY1_REFRESH_TOKEN={result['refresh_token']}")
        logger.info("-" * 60)
        logger.info(f"\n✅ Access token (первые 50 символов): {result['access_token'][:50]}...")
        logger.info(f"✅ Refresh token (первые 50 символов): {result['refresh_token'][:50]}...")
        logger.info(f"✅ Срок действия: {result.get('expires_in', 'N/A')} секунд")
    else:
        logger.error("\n❌ Не удалось получить токены. Проверьте:")
        logger.error("   1. Код авторизации не истек (действителен 20 минут)")
        logger.error("   2. Redirect URI совпадает с настройками интеграции")
        logger.error("   3. Client ID и Client Secret правильные")


if __name__ == "__main__":
    asyncio.run(main())

