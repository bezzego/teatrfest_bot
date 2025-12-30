# Отслеживание UTM меток при переходе с сайта в бот

## Как это работает

Когда пользователь переходит на сайт по ссылке с UTM метками (например, `https://site.com/?utm_source=yandex&utm_medium=cpc`), эти метки нужно:

1. **Извлечь из URL** при загрузке страницы
2. **Сохранить** в localStorage браузера (на 24 часа)
3. **Передать в deep link** бота при клике на кнопку "Получить скидку"

## Реализация на сайте

### Вариант 1: Использование готового скрипта

1. Добавьте файл `website_utm_tracking.js` на ваш сайт
2. Подключите его в `<head>` или перед `</body>`:

```html
<script src="/path/to/website_utm_tracking.js"></script>
```

3. Добавьте кнопку с data-атрибутами:

```html
<a href="#" 
   class="bot-link" 
   data-city="Самара" 
   data-project="Двое на качелях" 
   data-show-datetime="2026-02-13 19:00">
   Получить скидку 300 ₽
</a>
```

### Вариант 2: Ручная реализация

Если у вас уже есть JavaScript на сайте, используйте этот код:

```javascript
// Извлекаем UTM параметры из URL
function getUTMParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const params = {};
    
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach(key => {
        const value = urlParams.get(key);
        if (value) params[key] = value;
    });
    
    return Object.keys(params).length > 0 ? params : null;
}

// Сохраняем в localStorage
function saveUTMParams(params) {
    if (params) {
        localStorage.setItem('teatrfest_utm', JSON.stringify({
            params: params,
            timestamp: Date.now()
        }));
    }
}

// Генерируем ссылку на бота
function generateBotLink(city, project, showDatetime) {
    const utmParams = getUTMParams() || 
        JSON.parse(localStorage.getItem('teatrfest_utm') || '{}').params || {};
    
    const linkData = {
        city: city,
        project: project,
        show_datetime: showDatetime,
        utm_source: utmParams.utm_source || '',
        utm_medium: utmParams.utm_medium || '',
        utm_campaign: utmParams.utm_campaign || '',
        utm_term: utmParams.utm_term || '',
        utm_content: utmParams.utm_content || ''
    };
    
    const encoded = btoa(JSON.stringify(linkData));
    return `https://t.me/theatrfest_help_bot?start=${encoded}`;
}

// При загрузке страницы
window.addEventListener('DOMContentLoaded', function() {
    const utmParams = getUTMParams();
    if (utmParams) {
        saveUTMParams(utmParams);
    }
    
    // Обновляем ссылку на кнопке
    const button = document.querySelector('.bot-link');
    if (button) {
        button.href = generateBotLink(
            button.dataset.city,
            button.dataset.project,
            button.dataset.showDatetime
        );
    }
});
```

## Что происходит в боте

1. Пользователь переходит по ссылке с UTM метками на сайт
2. На сайте UTM метки сохраняются в localStorage
3. Пользователь нажимает кнопку "Получить скидку"
4. Ссылка на бота формируется с UTM метками в deep link
5. В боте UTM метки извлекаются и сохраняются в БД пользователя
6. При создании сделки в AmoCRM UTM метки можно передать в кастомные поля

## Проверка работы

1. Откройте сайт с UTM метками: `https://site.com/?utm_source=yandex&utm_medium=cpc`
2. Проверьте в консоли браузера (F12): должны быть сохранены UTM параметры
3. Нажмите на кнопку "Получить скидку"
4. Проверьте ссылку: она должна содержать закодированные параметры
5. В боте проверьте логи: должны быть видны UTM метки при обработке `/start`

## Важные моменты

- UTM метки сохраняются на 24 часа (можно изменить в коде)
- Если пользователь перейдет на другую страницу сайта без UTM меток, старые метки все равно будут использованы
- Если пользователь откроет сайт в новой вкладке с новыми UTM метками, они перезапишут старые
- Для каждого проекта/спектакля нужно указывать правильные данные (city, project, show_datetime)

