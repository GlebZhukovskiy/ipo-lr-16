// Функция для безопасного получения CSRF-токена из куки Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Показ Bootstrap Alert уведомлений на ходу
function showNotification(message, type = 'success') {
    const container = document.querySelector('.container.mt-3');
    if (!container) return;

    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show shadow-sm" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    container.insertAdjacentHTML('afterbegin', alertHtml);
}

// ТВОЙ КОД ДЛЯ ВЗАИМОДЕЙСТВИЯ С API ДЛЯ 21 ЛАБЫ
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Демонстрация асинхронной загрузки списка продуктов из API (Console Log)
    // Показываем спиннер (если бы рендерили весь каталог на JS)
    console.log("Загрузка данных из API...");
    
    fetch('/api/products/')
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сервера при обращении к API');
            return response.json();
        })
        .then(data => {
            console.log('Успешно получены продукты из API DRF:', data);
        })
        .catch(error => {
            console.error('Ошибка работы с API:', error);
            showNotification('Не удалось загрузить дополнительные данные из API.', 'danger');
        });
});

// 2. Асинхронное добавление в корзину через API
function asyncAddToCart(productId) {
    const csrftoken = getCookie('csrftoken');
    
    // Имитируем старт загрузки (Спиннер на кнопке)
    const btn = document.getElementById(`add-btn-${productId}`);
    let originalText = "";
    if (btn) {
        originalText = btn.innerHTML;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Добавление...`;
        btn.disabled = true;
    }

    fetch('/api/cart-items/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            product: productId,
            quantity: 1
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка при добавлении');
        return response.json();
    })
    .then(data => {
        showNotification('Товар успешно добавлен в корзину через API!', 'success');
    })
    .catch(err => {
        showNotification('Произошла ошибка при добавлении в корзину.', 'danger');
    })
    .finally(() => {
        // Возвращаем кнопку в исходное состояние
        if (btn) {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });
}