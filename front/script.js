// Функция для сбора данных из формы поиска статей
function collectSearchData() {
    // Получаем значение authorCount и разделяем на min и max
    const authorCount = document.getElementById('filter-author-number').value.trim();
    let authors_count = null;
    
    if (authorCount) {
        // Предполагаем, что значение может быть в формате "min-max" или просто число
        if (authorCount.includes('-')) {
            const parts = authorCount.split('-');
            // Для DTO используем минимальное значение как authors_count
            authors_count = parseInt(parts[0]) || null;
        } else {
            // Если одно число, используем его как authors_count
            authors_count = parseInt(authorCount) || null;
        }
    }
    
    // Получаем страны коллаборации и преобразуем в массив
    const countriesValue = document.getElementById('filter-countries').value.trim();
    let collaboration_countries = [];
    if (countriesValue) {
        collaboration_countries = countriesValue.split(',')
            .map(country => country.trim())
            .filter(country => country.length > 0);
    }
    
    return {
        query: document.getElementById('search-input').value.trim(),
        filters: {
            authors: document.getElementById('filter-authors').value.trim() || null,
            journal_title: document.getElementById('filter-journal').value.trim() || null,
            article_title: document.getElementById('filter-title').value.trim() || null,
            year_from: document.getElementById('filter-year-from').value.trim() || null,
            year_to: document.getElementById('filter-year-to').value.trim() || null,
            article_text: document.getElementById('filter-entire-text').value.trim() || null,
            abstract: document.getElementById('filter-abstract').value.trim() || null,
            affiliation: document.getElementById('filter-affiliation').value.trim() || null,
            authors_count: authors_count || null,
            collaboration_countries: collaboration_countries || null
        }
    };
}

// Функция для сбора данных из формы анализа DOI
function collectDoiAnalysisData() {
    const doiInput = document.getElementById('analysis-input').value.trim();
    // Разделяем DOI по запятым и удаляем пустые значения
    const dois = doiInput.split(',')
        .map(doi => doi.trim())
        .filter(doi => doi.length > 0);
    
    return {
        dois: dois
    };
}

// Функция для отображения состояния загрузки
function showLoading(isLoading, buttonId) {
    const button = document.getElementById(buttonId);
    if (isLoading) {
        button.disabled = true;
        button.textContent = 'Загрузка...';
    } else {
        button.disabled = false;
        button.textContent = buttonId === 'search-articles-btn' ? 'Искать' : 'Анализировать';
    }
}

// Функция для отображения ошибок
function showError(message, containerId = 'results-container') {
    // Создаем элемент для отображения ошибки
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = 'red';
    errorDiv.style.margin = '10px 0';
    errorDiv.style.padding = '10px';
    errorDiv.style.border = '1px solid red';
    errorDiv.style.borderRadius = '4px';
    errorDiv.style.backgroundColor = '#ffe6e6';
    
    // Добавляем ошибку в указанный контейнер
    const container = document.getElementById(containerId);
    // Удаляем предыдущие ошибки, если есть
    const existingError = container.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    container.insertBefore(errorDiv, container.firstChild);
}

// Функция для отображения результатов поиска в таблице
function displaySearchResults(articles) {
    const tbody = document.querySelector('#results-table tbody');
    tbody.innerHTML = ''; // Очищаем таблицу
    
    if (!articles || articles.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell(0);
        cell.colSpan = 8;
        cell.textContent = 'Результаты не найдены';
        cell.style.textAlign = 'center';
        return;
    }
    
    // Заполняем таблицу результатами
    articles.forEach(article => {
        const row = tbody.insertRow();
        
        // Создаем ячейки в порядке, соответствующем заголовкам таблицы
        const fields = [
            article.title || '',
            (article.authors && Array.isArray(article.authors)) ? article.authors.map(a => `${a.name} ${a.surname}`).join(', ') : '',
            article.year || '',
            article.journal_full || '',
            article.publisher || '',
            article.citations || '',
            article.annual_citations || '',
            article.doi ? `<a href="https://doi.org/${article.doi}" target="_blank">${article.doi}</a>` : ''
        ];
        
        fields.forEach(field => {
            const cell = row.insertCell();
            cell.innerHTML = field;
        });
    });
}

// Функция для отображения результатов анализа DOI
function displayDoiAnalysisResults(results) {
    const resultsDiv = document.getElementById('analysis-results');
    
    if (!results) {
        resultsDiv.innerHTML = '<p>Нет результатов для отображения</p>';
        return;
    }
    
    // Создаем HTML для отображения результатов
    let html = '<h3>Результаты анализа DOI:</h3>';
    
    if (Array.isArray(results)) {
        html += '<ul>';
        results.forEach(result => {
            html += `<li>${JSON.stringify(result)}</li>`;
        });
        html += '</ul>';
    } else {
        html += `<pre>${JSON.stringify(results, null, 2)}</pre>`;
    }
    
    resultsDiv.innerHTML = html;
}

// Функция для валидации данных поиска
function validateSearchData(data) {
    // Проверяем, что хотя бы одно поле заполнено
    const hasQuery = data.query || data.authors || data.journal_title || data.article_title ||
                     data.year_from || data.year_to || data.article_text || data.abstract ||
                     data.affiliation || data.authors_number_min || data.authors_number_max || data.collaboration_countries;
    
    if (!hasQuery) {
        throw new Error('Пожалуйста, заполните хотя бы одно поле для поиска');
    }
    
    // Проверяем корректность диапазона годов
    if (data.year_from && data.year_to && parseInt(data.year_from) > parseInt(data.year_to)) {
        throw new Error('Год "С" не может быть больше года "По"');
    }
    
    return true;
}

// Функция для валидации данных анализа DOI
function validateDoiData(data) {
    if (!data.dois || data.dois.length === 0) {
        throw new Error('Пожалуйста, введите хотя бы один DOI для анализа');
    }
    
    // Проверяем формат DOI (простая проверка)
    const doiRegex = /^10\.\d{4,9}\/[-._;()/:A-Z0-9]+$/i;
    for (const doi of data.dois) {
        if (!doiRegex.test(doi)) {
            throw new Error(`Некорректный формат DOI: ${doi}`);
        }
    }
    
    return true;
}

// Функция для отправки данных поиска статей
async function searchArticles() {
    try {
        // Собираем данные
        const searchData = collectSearchData();
        
        // Валидируем данные
        validateSearchData(searchData);
        
        // Показываем состояние загрузки
        showLoading(true, 'search-articles-btn');
        
        // Отправляем запрос
        const response = await fetch('/api/v1/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(searchData)
        });
        
        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status} ${response.statusText}`);
        }
        
        const results = await response.json();
        
        // Удаляем сообщение об ошибке, если оно было
        const errorDiv = document.querySelector('#results-container .error-message');
        if (errorDiv) {
            errorDiv.remove();
        }
        
        // Отображаем результаты
        displaySearchResults(results.articles);
    } catch (error) {
        console.error('Ошибка при поиске статей:', error);
        showError(error.message, 'results-container');
    } finally {
        // Скрываем состояние загрузки
        showLoading(false, 'search-articles-btn');
    }
}

// Функция для отправки данных анализа DOI
async function analyzeDoi() {
    try {
        // Собираем данные
        const doiData = collectDoiAnalysisData();
        
        // Валидируем данные
        validateDoiData(doiData);
        
        // Показываем состояние загрузки
        showLoading(true, 'analyze-doi-btn');
        
        // Отправляем запрос
        const response = await fetch('/api/v1/search/analyze/doi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(doiData)
        });
        
        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status} ${response.statusText}`);
        }
        
        const results = await response.json();
        
        // Отображаем результаты
        displayDoiAnalysisResults(results);
    } catch (error) {
        console.error('Ошибка при анализе DOI:', error);
        showError(error.message, 'analysis-results');
    } finally {
        // Скрываем состояние загрузки
        showLoading(false, 'analyze-doi-btn');
    }
}

// Функция для переключения видимости фильтров
function toggleFilters() {
    const filtersContent = document.getElementById('filters-content');
    filtersContent.classList.toggle('active');
}

// Функция для инициализации обработчиков событий
function initializeEventListeners() {
    // Обработчик для кнопки поиска статей
    const searchButton = document.getElementById('search-articles-btn');
    if (searchButton) {
        searchButton.addEventListener('click', (event) => {
            event.preventDefault();
            searchArticles();
        });
    }
    
    // Обработчик для формы анализа DOI
    const analysisForm = document.getElementById('analysis-form');
    if (analysisForm) {
        analysisForm.addEventListener('submit', (event) => {
            event.preventDefault();
            analyzeDoi();
        });
    }
    
    // Обработчик для кнопки переключения фильтров
    const toggleButton = document.getElementById('toggle-filters');
    if (toggleButton) {
        toggleButton.addEventListener('click', toggleFilters);
    }
}

// Функция для переключения темы
function toggleTheme() {
    const body = document.body;
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    body.classList.toggle('dark-theme');
    
    // Сохраняем выбор темы в localStorage
    if (body.classList.contains('dark-theme')) {
        localStorage.setItem('theme', 'dark');
        themeText.textContent = 'Светлая тема';
        themeIcon.src = '/static/sun.png';
    } else {
        localStorage.setItem('theme', 'light');
        themeText.textContent = 'Тёмная тема';
        themeIcon.src = '/static/moon.png';
    }
}

// Функция для установки темы при загрузке страницы
function setInitialTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeText.textContent = 'Светлая тема';
        themeIcon.src = '/static/sun.png';
    } else {
        themeText.textContent = 'Тёмная тема';
        themeIcon.src = '/static/moon.png';
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    setInitialTheme();
    initializeEventListeners();
    
    // Добавляем обработчик для переключения темы
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});