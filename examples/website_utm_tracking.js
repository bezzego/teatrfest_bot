/**
 * Пример JavaScript кода для сайта
 * Извлекает UTM метки из URL и передает их в ссылку Telegram бота
 * 
 * Инструкция:
 * 1. Добавьте этот код на ваш сайт (в <head> или перед закрывающим </body>)
 * 2. Замените BOT_USERNAME на ваш username бота
 * 3. Замените данные проекта (city, project, show_datetime) на актуальные
 */

(function() {
    'use strict';
    
    // Конфигурация
    const BOT_USERNAME = 'theatrfest_help_bot';
    const STORAGE_KEY = 'teatrfest_utm_params';
    const STORAGE_EXPIRY = 24 * 60 * 60 * 1000; // 24 часа в миллисекундах
    
    /**
     * Извлекает UTM параметры из URL
     */
    function getUTMParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const utmParams = {};
        
        // Список UTM параметров для извлечения
        const utmKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
        
        utmKeys.forEach(key => {
            const value = urlParams.get(key);
            if (value) {
                utmParams[key] = value;
            }
        });
        
        // Также извлекаем yandex_id и roistat_visit, если они есть
        const yandexId = urlParams.get('yandex_id') || urlParams.get('_ym_uid');
        if (yandexId) {
            utmParams['yandex_id'] = yandexId;
        }
        
        const roistatVisit = urlParams.get('roistat_visit');
        if (roistatVisit) {
            utmParams['roistat_visit'] = roistatVisit;
        }
        
        return Object.keys(utmParams).length > 0 ? utmParams : null;
    }
    
    /**
     * Сохраняет UTM параметры в localStorage
     */
    function saveUTMParams(params) {
        if (!params || Object.keys(params).length === 0) {
            return;
        }
        
        const data = {
            params: params,
            timestamp: Date.now()
        };
        
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
            console.log('UTM параметры сохранены:', params);
        } catch (e) {
            console.error('Ошибка сохранения UTM параметров:', e);
        }
    }
    
    /**
     * Получает сохраненные UTM параметры из localStorage
     */
    function getSavedUTMParams() {
        try {
            const data = localStorage.getItem(STORAGE_KEY);
            if (!data) {
                return null;
            }
            
            const parsed = JSON.parse(data);
            
            // Проверяем, не истекли ли данные (24 часа)
            if (Date.now() - parsed.timestamp > STORAGE_EXPIRY) {
                localStorage.removeItem(STORAGE_KEY);
                return null;
            }
            
            return parsed.params;
        } catch (e) {
            console.error('Ошибка чтения UTM параметров:', e);
            return null;
        }
    }
    
    /**
     * Генерирует ссылку на Telegram бота с UTM метками
     * @param {string} city - Город
     * @param {string} project - Название проекта/спектакля
     * @param {string} showDatetime - Дата и время в формате "2026-02-13 19:00"
     */
    function generateBotLink(city, project, showDatetime) {
        // Получаем UTM параметры (сначала из URL, потом из сохраненных)
        let utmParams = getUTMParams();
        
        if (!utmParams) {
            utmParams = getSavedUTMParams();
        } else {
            // Сохраняем новые UTM параметры
            saveUTMParams(utmParams);
        }
        
        // Кодируем данные для deep link
        const linkData = {
            city: city,
            project: project,
            show_datetime: showDatetime,
            utm_source: utmParams?.utm_source || '',
            utm_medium: utmParams?.utm_medium || '',
            utm_campaign: utmParams?.utm_campaign || '',
            utm_term: utmParams?.utm_term || '',
            utm_content: utmParams?.utm_content || '',
            yandex_id: utmParams?.yandex_id || '',
            roistat_visit: utmParams?.roistat_visit || ''
        };
        
        // Кодируем в base64
        const encoded = btoa(JSON.stringify(linkData));
        
        // Формируем ссылку
        return `https://t.me/${BOT_USERNAME}?start=${encoded}`;
    }
    
    /**
     * Обновляет ссылку на кнопке "Получить скидку"
     */
    function updateBotButton() {
        // Находим все кнопки с классом или data-атрибутом для бота
        const buttons = document.querySelectorAll('[data-bot-link], .bot-link, a[href*="t.me/' + BOT_USERNAME + '"]');
        
        buttons.forEach(button => {
            // Получаем данные проекта из data-атрибутов или из конфигурации
            const city = button.dataset.city || 'Москва'; // Замените на актуальный город
            const project = button.dataset.project || 'Спектакль'; // Замените на актуальный проект
            const showDatetime = button.dataset.showDatetime || '2026-02-13 19:00'; // Замените на актуальную дату
            
            // Генерируем ссылку с UTM метками
            const botLink = generateBotLink(city, project, showDatetime);
            
            // Обновляем href кнопки
            button.href = botLink;
            
            console.log('Ссылка на бота обновлена:', botLink);
        });
    }
    
    // Инициализация при загрузке страницы
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            // Извлекаем и сохраняем UTM параметры из URL
            const utmParams = getUTMParams();
            if (utmParams) {
                saveUTMParams(utmParams);
            }
            
            // Обновляем ссылки на кнопках
            updateBotButton();
        });
    } else {
        // Страница уже загружена
        const utmParams = getUTMParams();
        if (utmParams) {
            saveUTMParams(utmParams);
        }
        updateBotButton();
    }
    
    // Экспортируем функцию для использования в других скриптах
    window.TeatrFestBot = {
        generateBotLink: generateBotLink,
        updateBotButton: updateBotButton,
        getUTMParams: getUTMParams,
        getSavedUTMParams: getSavedUTMParams
    };
    
})();

/**
 * Пример использования в HTML:
 * 
 * <a href="#" 
 *    class="bot-link" 
 *    data-city="Самара" 
 *    data-project="Двое на качелях" 
 *    data-show-datetime="2026-02-13 19:00">
 *    Получить скидку 300 ₽
 * </a>
 * 
 * Или программно:
 * 
 * const link = window.TeatrFestBot.generateBotLink('Самара', 'Двое на качелях', '2026-02-13 19:00');
 * console.log(link);
 */

