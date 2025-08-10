

document.addEventListener('DOMContentLoaded', function () {
    console.log("🚀 main.js: DOMContentLoaded");

    
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    const scrollToBottomBtn = document.getElementById('scrollToBottomBtn');

    if (scrollToTopBtn) {
        scrollToTopBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    if (scrollToBottomBtn) {
        scrollToBottomBtn.addEventListener('click', function () {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        });
    }

    
    if (typeof window.STATS_DATA === 'undefined' ||
        !window.STATS_DATA.hourly ||
        !window.STATS_DATA.weekly ||
        !window.STATS_DATA.city) {
        console.error("❌ main.js: Данные статистики не найдены в window.STATS_DATA");
        alert("Не удалось загрузить данные для графиков.");
        return;
    }

    const refreshBtn = document.getElementById('refreshBtn');
    const refreshModal = document.getElementById('refreshModal');
    const refreshClose = refreshModal ? refreshModal.querySelector('.close') : null;
    const refreshStatus = document.getElementById('refreshStatus');
    const refreshMessage = document.getElementById('refreshMessage');

    if (refreshBtn) {
        refreshBtn.addEventListener('click', function () {
            console.log("🔄 main.js: Нажата кнопка 'Обновить данные'");

            
            refreshBtn.disabled = true;
            refreshBtn.textContent = '⏳ Обновление...';

            
            if (refreshModal) {
                refreshModal.style.display = 'flex';
                if (refreshStatus) refreshStatus.textContent = '⏳ Запуск...';
                if (refreshMessage) refreshMessage.textContent = '';
            }

            
            fetch('/run-main-py', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                console.log("✅ main.js: Ответ от /run-main-py:", data);
                if (refreshStatus) refreshStatus.textContent = data.status === 'success' ? '✅ Готово!' : '❌ Ошибка';
                if (refreshMessage) refreshMessage.textContent = data.message || 'Нет сообщения';
            })
            .catch(error => {
                console.error("❌ main.js: Ошибка при вызове /run-main-py:", error);
                if (refreshStatus) refreshStatus.textContent = '❌ Ошибка';
                if (refreshMessage) {
                    if (error.message) {
                        refreshMessage.textContent = error.message;
                    } else {
                        refreshMessage.textContent = 'Не удалось связаться с сервером.';
                    }
                }
            })
            .finally(() => {
                
                refreshBtn.disabled = false;
                refreshBtn.textContent = '🔄 Обновить данные';
            });
        });
    }

    if (refreshClose) {
        refreshClose.addEventListener('click', function () {
            if (refreshModal) refreshModal.style.display = 'none';
        });
    }

    if (refreshModal) {
        refreshModal.addEventListener('click', function (event) {
            if (event.target === refreshModal) {
                refreshModal.style.display = 'none';
            }
        });
    }

    const hourlyStatsData = window.STATS_DATA.hourly;
    const weeklyStatsData = window.STATS_DATA.weekly;
    const cityStatsData = window.STATS_DATA.city;

    console.log("📊 main.js: Данные для графиков загружены:");
    console.log("   - Почасовая активность:", hourlyStatsData);
    console.log("   - Активность по дням недели:", weeklyStatsData);
    console.log("   - Активность по городам:", cityStatsData);

    
    const hourlyCtx = document.getElementById('hourlyActivityChart');
    if (hourlyCtx) {
        console.log("📊 main.js: Создаём график по часам...");
        new Chart(hourlyCtx, {
            type: 'bar',
            data: {
                labels: hourlyStatsData.map(item => `${item.hour}:00`),
                datasets: [{
                    label: 'Количество уникальных пользователей',
                    data: hourlyStatsData.map(item => item.count),
                    backgroundColor: 'rgba(76, 117, 163, 0.7)',
                    borderColor: 'rgba(76, 117, 163, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Часы суток (МСК)' },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Количество пользователей' },
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
        console.log("✅ main.js: График по часам создан.");
    } else {
        console.error("❌ main.js: Элемент canvas для графика по часам не найден.");
    }

    
    const weeklyCtx = document.getElementById('weeklyActivityChart');
    if (weeklyCtx) {
        console.log("📊 main.js: Создаём график по дням недели...");
        new Chart(weeklyCtx, {
            type: 'bar',
            data: {
                labels: weeklyStatsData.map(item => item.day_name),
                datasets: [{
                    label: 'Количество уникальных пользователей',
                    data: weeklyStatsData.map(item => item.count),
                    backgroundColor: 'rgba(46, 204, 113, 0.7)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Дни недели' },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Количество пользователей' },
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
        console.log("✅ main.js: График по дням недели создан.");
    } else {
        console.error("❌ main.js: Элемент canvas для графика по дням недели не найден.");
    }

    
    const cityCtx = document.getElementById('cityActivityChart');
    if (cityCtx) {
        console.log("📊 main.js: Создаём график по городам...");
        new Chart(cityCtx, {
            type: 'bar',
            data: {
                labels: cityStatsData.map(item => item.city_name),
                datasets: [{
                    label: 'Количество уникальных пользователей',
                    data: cityStatsData.map(item => item.count),
                    backgroundColor: 'rgba(155, 89, 182, 0.7)',
                    borderColor: 'rgba(155, 89, 182, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: { display: true, text: 'Количество пользователей' },
                        ticks: { stepSize: 1 }
                    },
                    y: {
                        title: { display: true, text: 'Города' },
                        grid: { display: false }
                    }
                }
            }
        });
        console.log("✅ main.js: График по городам создан.");
    } else {
        console.error("❌ main.js: Элемент canvas для графика по городам не найден.");
    }
});
