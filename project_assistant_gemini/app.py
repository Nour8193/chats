import streamlit as st
import os
from dotenv import load_dotenv
from utils.gemini_handler import GeminiAssistant

# Загрузка переменных окружения
load_dotenv()

# Настройка страницы
st.set_page_config(
    page_title="🎓 Проектный навигатор Gemini",
    page_icon="📊",
    layout="wide"
)

# Заголовок
st.title("🎓 Проектный навигатор для педагога")
st.markdown("""
ИИ-помощник на основе **Google Gemini Pro** для планирования образовательных проектов.
""")

# Инициализация сессионных переменных
if "history" not in st.session_state:
    st.session_state.history = []
if "assistant" not in st.session_state:
    try:
        st.session_state.assistant = GeminiAssistant()
        st.success("✅ Gemini API подключен успешно!")
    except Exception as e:
        st.error(f"❌ Ошибка инициализации Gemini: {e}")

# Боковая панель
with st.sidebar:
    st.header("⚙️ Настройки")
    
    # Проверка API ключа
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.success("✅ API ключ найден")
    else:
        st.error("❌ API ключ не найден в .env файле")
        st.info("Создайте файл .env с содержимым: GEMINI_API_KEY=ваш_ключ")
    
    st.divider()
    
    st.header("📋 Выбор задачи")
    task_type = st.selectbox(
        "Тип задачи:",
        ["💰 Бюджетирование", "⚠️ Анализ рисков", "📊 Мониторинг", "🎤 Презентация", "🚀 Инициация"]
    )
    
    # Маппинг
    task_map = {
        "💰 Бюджетирование": "budget",
        "⚠️ Анализ рисков": "risks",
        "📊 Мониторинг": "monitoring",
        "🎤 Презентация": "presentation",
        "🚀 Инициация": "initiation"
    }
    
    current_task = task_map[task_type]
    
    st.divider()
    
    if st.button("🗑️ Очистить историю", type="secondary"):
        st.session_state.history = []
        st.rerun()

# Основная область
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Задача: {task_type}")
    
    # Примеры запросов
    examples = {
        "budget": "Пример: 'Создай бюджет для школьного медиацентра: 3 ноутбука, камера, микрофоны, ПО. Бюджет до 150 000 руб.'",
        "risks": "Пример: 'Проанализируй риски для IT-клуба: технические, кадровые, организационные.'",
        "presentation": "Пример: 'Нужна структура 5-минутной презентации для конкурса. Аудитория — администрация города.'"
    }
    
    # Поле ввода
    user_input = st.text_area(
        "📝 Опишите вашу задачу:",
        value=examples.get(current_task, "Опишите ваш проект..."),
        height=120,
        key="input"
    )
    
    # Кнопка генерации
    if st.button("🚀 Сгенерировать решение", type="primary", use_container_width=True):
        if user_input and user_input != examples.get(current_task, ""):
            # Добавляем в историю
            st.session_state.history.append({
                "role": "user",
                "content": user_input,
                "task": current_task
            })
            
            # Показываем индикатор загрузки
            with st.spinner("Gemini анализирует..."):
                try:
                    # Получаем ответ
                    response = st.session_state.assistant.generate_response(
                        user_input=user_input,
                        task_type=current_task,
                        history=st.session_state.history
                    )
                    
                    # Добавляем ответ в историю
                    st.session_state.history.append({
                        "role": "assistant",
                        "content": response,
                        "task": current_task
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Ошибка: {e}")

with col2:
    st.subheader("📜 История диалога")
    if st.session_state.history:
        for i, msg in enumerate(st.session_state.history):
            if msg["role"] == "user":
                st.markdown(f"**👤 Вы:** {msg['content'][:80]}...")
            else:
                st.markdown(f"**🤖 Ассистент:** {msg['content'][:100]}...")
            st.divider()
    else:
        st.info("Здесь будет история вашего диалога")

# Отображение последнего ответа
if st.session_state.history and st.session_state.history[-1]["role"] == "assistant":
    st.divider()
    st.subheader("💡 Решение от Gemini")
    
    last_response = st.session_state.history[-1]["content"]
    
    # Отображаем ответ с форматированием
    st.markdown(last_response)
    
    # Кнопки для работы с ответом
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Копировать", use_container_width=True):
            st.code(last_response, language="markdown")
            
    with col2:
        if st.button("💾 Сохранить в файл", use_container_width=True):
            filename = f"gemini_рекомендации_{current_task}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(last_response)
            st.success(f"Сохранено в {filename}")
    
    with col3:
        if st.button("🔄 Новый запрос", use_container_width=True):
            st.rerun()

# Футер с информацией
st.divider()
with st.expander("ℹ️ Информация о системе"):
    st.markdown("""
    ### Технологии:
    - **Модель:** Google Gemini Pro 1.5
    - **Интерфейс:** Streamlit (Python)
    - **Контекст:** 2048 токенов
    - **История:** 4 последних сообщения
    
    ### Инструкция по настройке:
    1. Получите API ключ на [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
    2. Создайте файл `.env` в папке проекта
    3. Добавьте строку: `GEMINI_API_KEY=ваш_ключ_здесь`
    4. Запустите: `streamlit run app.py`
    
    ### Ограничения:
    - Бесплатный лимит: 60 запросов в минуту
    - Для учебных проектов достаточно
    - Поддержка русского языка: отличная
    """)
