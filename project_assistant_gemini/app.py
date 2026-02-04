import streamlit as st
import google.generativeai as genai
import os
import time

# Настройка страницы
st.set_page_config(
    page_title="🎓 Проектный навигатор Gemini",
    page_icon="📊",
    layout="wide"
)

st.title("🎓 Проектный навигатор для педагога")
st.markdown("ИИ-помощник для планирования образовательных проектов на основе Google Gemini")

# Секция для ввода API ключа
with st.sidebar:
    st.header("🔑 Настройки API")
    
    # Вариант 1: Ввод ключа в интерфейсе
    api_key = st.text_input(
        "Введите API ключ Gemini:",
        type="password",
        help="Получите на https://aistudio.google.com/app/apikey"
    )
    
    # Вариант 2: Из переменной окружения
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.success("✅ API ключ принят!")
            
            # Показываем доступные модели
            st.divider()
            st.header("🤖 Доступные модели")
            
            try:
                models = genai.list_models()
                available_models = []
                for model in models:
                    if 'generateContent' in model.supported_generation_methods:
                        available_models.append(model.name)
                
                selected_model = st.selectbox(
                    "Выберите модель:",
                    available_models,
                    index=0 if available_models else None
                )
                
                # Сохраняем в сессию
                st.session_state.selected_model = selected_model
                st.info(f"Выбрана: {selected_model}")
                
            except Exception as e:
                st.warning(f"Не удалось получить список моделей: {e}")
                st.session_state.selected_model = "gemini-pro"  # По умолчанию
            
        except Exception as e:
            st.error(f"❌ Ошибка настройки API: {e}")
    else:
        st.warning("⚠️ Введите API ключ для начала работы")
    
    st.divider()
    
    # Выбор задачи
    st.header("📋 Задачи")
    task_type = st.selectbox(
        "Выберите тип задачи:",
        ["💰 Бюджетирование", "⚠️ Анализ рисков", "🎤 Презентация", "📊 Мониторинг", "🚀 Инициация"]
    )
    
    # Кнопка очистки
    if st.button("🗑️ Очистить чат"):
        if "messages" in st.session_state:
            st.session_state.messages = []
        st.rerun()

# Инициализация истории чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# Основной интерфейс чата
st.header("💬 Чат с ИИ-ассистентом")

# Показываем историю сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Опишите вашу задачу..."):
    if not api_key:
        st.error("⚠️ Сначала введите API ключ в боковой панели!")
        st.stop()
    
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Генерируем ответ
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Определяем системный промпт в зависимости от задачи
            system_prompts = {
                "💰 Бюджетирование": """Ты — эксперт по бюджету образовательных проектов. Твоя задача:
1. Создавать детальные сметы в табличном формате Markdown
2. Предлагать источники финансирования (гранты, спонсоры, краудфандинг)
3. Давать советы по оптимизации расходов
4. Предлагать план привлечения средств

Формат ответа: краткий вывод → таблица → рекомендации → план действий.""",
                
                "⚠️ Анализ рисков": """Ты — риск-менеджер образовательных проектов. Твоя задача:
1. Выявлять потенциальные риски по категориям
2. Оценивать вероятность и влияние
3. Предлагать конкретные меры минимизации
4. Создавать чек-листы действий

Используй таблицы и списки. Будь практичным.""",
                
                "🎤 Презентация": """Ты — специалист по презентациям. Твоя задача:
1. Создавать структуру презентации по времени
2. Предлагать визуальные идеи
3. Готовить ключевые сообщения
4. Продумывать ответы на вопросы

Фокус на образовательных проектах."""
            }
            
            system_prompt = system_prompts.get(task_type, "Ты — помощник педагога в реализации проектов.")
            
            # Формируем полный промпт
            full_prompt = f"""{system_prompt}

Контекст задачи: {task_type}

Вопрос пользователя: {prompt}

Пожалуйста, дай развернутый, структурированный ответ с практическими рекомендациями."""
            
            # Используем правильную модель
            model_name = st.session_state.get("selected_model", "gemini-pro")
            
            # Создаем модель
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2000,
                }
            )
            
            # Генерируем ответ
            response = model.generate_content(full_prompt)
            
            # Проверяем ответ
            if response and hasattr(response, 'text'):
                full_response = response.text
            else:
                full_response = "Не удалось получить ответ. Попробуйте другой запрос."
            
        except Exception as e:
            full_response = f"Ошибка: {str(e)}\n\nИспользуемая модель: {st.session_state.get('selected_model', 'gemini-pro')}"
        
        # Отображаем ответ
        message_placeholder.markdown(full_response)
    
    # Добавляем ответ в историю
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Дополнительные функции
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📋 Пример запроса: Бюджет"):
        example = "Создай бюджет для школьного экологического проекта: посадка 20 деревьев, уборка территории, экологические листовки. Бюджет: 25 000 руб."
        st.chat_input("", value=example, key="example1")

with col2:
    if st.button("📋 Пример запроса: Риски"):
        example = "Проанализируй риски для проекта 'Школьный медиацентр': оборудование, команда, контент. Предложи план минимизации."
        st.chat_input("", value=example, key="example2")

with col3:
    if st.button("📋 Пример запроса: Презентация"):
        example = "Нужна структура 5-минутной презентации проекта 'Умная теплица' для конкурса. Аудитория: инвесторы."
        st.chat_input("", value=example, key="example3")

# Информационная панель
with st.expander("ℹ️ Информация и инструкции"):
    st.markdown("""
    ## 🚀 Быстрый старт:
    
    1. **Получите API ключ** на [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. **Введите ключ** в поле слева
    3. **Выберите задачу** и опишите ваш проект
    4. **Получите готовые решения** от ИИ
    
    ## 📊 Примеры запросов:
    
    ### Бюджетирование:
    ```
    Создай бюджет для IT-клуба: 5 ноутбуков, проектор, ПО. 
    Бюджет: 300 000 руб. Учти гранты и спонсоров.
    ```
    
    ### Анализ рисков:
    ```
    Какие риски у онлайн-курса для школьников? 
    Предложи матрицу рисков и план действий.
    ```
    
    ### Презентация:
    ```
    Структура презентации проекта "Робототехника для всех" 
    на 7 минут для родительского собрания.
    ```
    
    ## ⚙️ Техническая информация:
    - **Модель по умолчанию:** gemini-pro
    - **Максимальный ответ:** 2000 токенов
    - **Поддержка языков:** Русский, Английский
    - **Лимиты:** 60 запросов/минута (бесплатно)
    
    ## 🔧 Устранение неполадок:
    
    Если вы видите ошибку 404:
    1. Убедитесь, что ключ API действителен
    2. Попробуйте другую модель из списка
    3. Проверьте интернет-соединение
    
    Самые стабильные модели:
    - `models/gemini-pro`
    - `models/gemini-1.0-pro`
    """)

# Тестовый скрипт для проверки API
with st.expander("🧪 Тест API"):
    if st.button("Проверить подключение к Gemini"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                
                # Пробуем разные модели
                test_models = ["gemini-pro", "gemini-1.0-pro"]
                working_model = None
                
                for model_name in test_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content("Ответь 'Готов к работе!'")
                        if response.text:
                            working_model = model_name
                            st.success(f"✅ Модель {model_name} работает!")
                            break
                    except:
                        continue
                
                if working_model:
                    st.info(f"Рекомендуемая модель: {working_model}")
                    st.session_state.selected_model = working_model
                else:
                    st.error("❌ Ни одна из тестовых моделей не работает. Проверьте API ключ.")
                    
            except Exception as e:
                st.error(f"Ошибка подключения: {e}")
        else:
            st.warning("Введите API ключ для теста")
