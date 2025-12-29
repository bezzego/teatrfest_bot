"""Скрипт для автоматического обновления токенов AmoCRM через refresh token

Использование:
    python scripts/update_amocrm_tokens.py

Скрипт обновит токены для обоих аккаунтов AmoCRM (City1 - АТЛАНТ и City2 - ЭТАЖИ)
и выведет новые токены для обновления в .env файле.
"""
import asyncio
import sys
import os
import aiohttp
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from logger import setup_logger

logger = setup_logger(__name__)


async def refresh_amocrm_token(subdomain: str, client_id: str, client_secret: str, refresh_token: str, redirect_uri: str) -> dict:
    """Обновить токен доступа AmoCRM через refresh token
    
    Args:
        subdomain: Поддомен AmoCRM (например, tugolukov)
        client_id: Client ID из настроек интеграции
        client_secret: Client Secret из настроек интеграции
        refresh_token: Refresh token для обновления
        redirect_uri: Redirect URI из настроек интеграции
        
    Returns:
        Словарь с новыми access_token и refresh_token или None при ошибке
    """
    url = f"https://{subdomain}.amocrm.ru/oauth2/access_token"
    
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": redirect_uri
    }
    
    logger.info(f"Обновление токена для {subdomain}.amocrm.ru...")
    logger.debug(f"URL: {url}")
    logger.debug(f"Client ID (первые 20 символов): {client_id[:20]}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Токен успешно обновлен для {subdomain}")
                    return {
                        "access_token": result.get("access_token"),
                        "refresh_token": result.get("refresh_token"),
                        "expires_in": result.get("expires_in")
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка обновления токена для {subdomain}: статус {response.status}")
                    logger.error(f"Ответ: {error_text}")
                    
                    # Дополнительные рекомендации при ошибке 400
                    if response.status == 400:
                        logger.error("\n💡 Возможные причины ошибки:")
                        logger.error("   1. Неверный client_id - проверьте AMOCRM_CITY1_CLIENT_ID в .env")
                        logger.error("   2. Неверный client_secret - проверьте AMOCRM_CITY1_CLIENT_SECRET в .env")
                        logger.error("   3. Неверный redirect_uri - должен совпадать с настройками интеграции")
                        logger.error("   4. Истек refresh_token - требуется повторная авторизация через OAuth2")
                        logger.error("\n   Проверьте настройки интеграции в AmoCRM:")
                        logger.error(f"   https://{subdomain}.amocrm.ru/integrations/oauth")
                    
                    return None
    except Exception as e:
        logger.error(f"❌ Исключение при обновлении токена для {subdomain}: {e}", exc_info=True)
        return None


async def update_tokens():
    """Обновить токены для обоих аккаунтов AmoCRM"""
    logger.info("=" * 60)
    logger.info("ОБНОВЛЕНИЕ ТОКЕНОВ AMOCRM")
    logger.info("=" * 60)
    
    # Загружаем конфигурацию
    config = Config.load()
    
    results = {}
    
    # Обновляем токены для City1 (АТЛАНТ)
    logger.info("\n" + "=" * 60)
    logger.info("Обновление токенов для City1 (АТЛАНТ)")
    logger.info("=" * 60)
    logger.info(f"Subdomain: {config.amocrm_city1.subdomain}")
    
    city1_result = await refresh_amocrm_token(
        subdomain=config.amocrm_city1.subdomain,
        client_id=config.amocrm_city1.client_id,
        client_secret=config.amocrm_city1.client_secret,
        refresh_token=config.amocrm_city1.refresh_token,
        redirect_uri=config.amocrm_city1.redirect_uri
    )
    
    if city1_result:
        results['city1'] = city1_result
        logger.info(f"✅ Новый access_token (первые 50 символов): {city1_result['access_token'][:50]}...")
        logger.info(f"✅ Новый refresh_token (первые 50 символов): {city1_result['refresh_token'][:50]}...")
        logger.info(f"✅ Срок действия: {city1_result.get('expires_in', 'N/A')} секунд")
    else:
        logger.error("❌ Не удалось обновить токены для City1 (АТЛАНТ)")
        results['city1'] = None
    
    # Обновляем токены для City2 (ЭТАЖИ)
    logger.info("\n" + "=" * 60)
    logger.info("Обновление токенов для City2 (ЭТАЖИ)")
    logger.info("=" * 60)
    logger.info(f"Subdomain: {config.amocrm_city2.subdomain}")
    
    city2_result = await refresh_amocrm_token(
        subdomain=config.amocrm_city2.subdomain,
        client_id=config.amocrm_city2.client_id,
        client_secret=config.amocrm_city2.client_secret,
        refresh_token=config.amocrm_city2.refresh_token,
        redirect_uri=config.amocrm_city2.redirect_uri
    )
    
    if city2_result:
        results['city2'] = city2_result
        logger.info(f"✅ Новый access_token (первые 50 символов): {city2_result['access_token'][:50]}...")
        logger.info(f"✅ Новый refresh_token (первые 50 символов): {city2_result['refresh_token'][:50]}...")
        logger.info(f"✅ Срок действия: {city2_result.get('expires_in', 'N/A')} секунд")
    else:
        logger.error("❌ Не удалось обновить токены для City2 (ЭТАЖИ)")
        results['city2'] = None
    
    # Выводим результаты для обновления .env файла
    logger.info("\n" + "=" * 60)
    logger.info("РЕЗУЛЬТАТЫ ОБНОВЛЕНИЯ")
    logger.info("=" * 60)
    
    if results.get('city1'):
        logger.info("\n📝 Обновите следующие строки в .env файле для City1 (АТЛАНТ):")
        logger.info("-" * 60)
        logger.info(f"AMOCRM_CITY1_ACCESS_TOKEN={results['city1']['access_token']}")
        logger.info(f"AMOCRM_CITY1_REFRESH_TOKEN={results['city1']['refresh_token']}")
        logger.info("-" * 60)
    
    if results.get('city2'):
        logger.info("\n📝 Обновите следующие строки в .env файле для City2 (ЭТАЖИ):")
        logger.info("-" * 60)
        logger.info(f"AMOCRM_CITY2_ACCESS_TOKEN={results['city2']['access_token']}")
        logger.info(f"AMOCRM_CITY2_REFRESH_TOKEN={results['city2']['refresh_token']}")
        logger.info("-" * 60)
    
    # Проверяем, есть ли .env файл для автоматического обновления
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        logger.info(f"\n💡 Файл .env найден: {env_path}")
        logger.info("Вы можете обновить токены вручную, скопировав значения выше")
        logger.info("Или используйте опцию --update-env для автоматического обновления (будет создан .env.backup)")
    else:
        logger.warning(f"\n⚠️  Файл .env не найден: {env_path}")
        logger.info("Создайте файл .env и добавьте туда обновленные токены")
    
    # Итоговая статистика
    logger.info("\n" + "=" * 60)
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)
    logger.info(f"✅ Успешно обновлено: {success_count}/{total_count}")
    if success_count < total_count:
        logger.warning(f"⚠️  Не обновлено: {total_count - success_count}/{total_count}")
    logger.info("=" * 60)
    
    return results


async def update_env_file(results: dict):
    """Автоматически обновить .env файл с новыми токенами"""
    env_path = Path(__file__).parent.parent / ".env"
    backup_path = Path(__file__).parent.parent / ".env.backup"
    
    if not env_path.exists():
        logger.error(f"Файл .env не найден: {env_path}")
        return False
    
    try:
        # Создаем резервную копию
        import shutil
        shutil.copy(env_path, backup_path)
        logger.info(f"✅ Создана резервная копия: {backup_path}")
        
        # Читаем текущий .env файл
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Обновляем токены
        updated_lines = []
        for line in lines:
            updated = False
            
            # Обновляем City1 токены
            if results.get('city1'):
                if line.startswith('AMOCRM_CITY1_ACCESS_TOKEN='):
                    updated_lines.append(f"AMOCRM_CITY1_ACCESS_TOKEN={results['city1']['access_token']}\n")
                    updated = True
                elif line.startswith('AMOCRM_CITY1_REFRESH_TOKEN='):
                    updated_lines.append(f"AMOCRM_CITY1_REFRESH_TOKEN={results['city1']['refresh_token']}\n")
                    updated = True
            
            # Обновляем City2 токены
            if results.get('city2'):
                if line.startswith('AMOCRM_CITY2_ACCESS_TOKEN='):
                    updated_lines.append(f"AMOCRM_CITY2_ACCESS_TOKEN={results['city2']['access_token']}\n")
                    updated = True
                elif line.startswith('AMOCRM_CITY2_REFRESH_TOKEN='):
                    updated_lines.append(f"AMOCRM_CITY2_REFRESH_TOKEN={results['city2']['refresh_token']}\n")
                    updated = True
            
            if not updated:
                updated_lines.append(line)
        
        # Записываем обновленный файл
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        logger.info(f"✅ Файл .env успешно обновлен: {env_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении .env файла: {e}", exc_info=True)
        return False


async def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Обновление токенов AmoCRM')
    parser.add_argument(
        '--update-env',
        action='store_true',
        help='Автоматически обновить .env файл (создаст резервную копию)'
    )
    
    args = parser.parse_args()
    
    # Обновляем токены
    results = await update_tokens()
    
    # Если запрошено автоматическое обновление .env
    if args.update_env:
        logger.info("\n" + "=" * 60)
        logger.info("АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ .ENV ФАЙЛА")
        logger.info("=" * 60)
        await update_env_file(results)
    else:
        logger.info("\n💡 Для автоматического обновления .env файла используйте:")
        logger.info("   python scripts/update_amocrm_tokens.py --update-env")


if __name__ == "__main__":
    asyncio.run(main())

