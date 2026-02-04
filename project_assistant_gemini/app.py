import streamlit as st
import pandas as pd
from utils.gemini_handler import GeminiAssistant
import json

# Настройка страницы
st.set_page_config(
    page_title="Проектный консультант Gemini",
    page_icon="🎓",
    layout="wide"
)

# Инициализация ассистента
@st.cache_resource
def get_assistant():
    return GeminiAssistant()

assistant = get_assistant()

# Инициализация истории в session_state
if "history" not in st.session_state:
    st.session_state.history = []
if "current_task" not in st.session_state:
    st.session_state.current_task = "budget"

# Заголовок и описание
st.title("🎓 Проектный консультант для педагога")
st.markdown("""
ИИ-помощник на основе **Google Gemini Pro** для планирования образовательных проектов.
Выберите задачу и опишите ваш проект для получения персонализированных рекомендаций.
""")

# Боковая панель с выбором задачи
with st.sidebar:
    st.header("📋 Задачи проекта")
    
    task = st.radio(
        "Выберите тип задачи:",
        ["💰 Бюджетирование", "⚠️ Анализ рисков", "📊 Мониторинг", 
         "🎤 Презентация", "🚀 Инициация проекта"],
        index=0
    )
    
    # Маппинг выбора на тип задачи
    task_map = {
        "💰 Бюджетирование": "budget",
        "⚠️ Анализ рисков": "risks", 
        "📊 Мониторинг": "monitoring",
        "🎤 Презентация": "presentation",
        "🚀 Инициация проекта": "initiation"
    }
    
    st.session_state.current_task = task_map[task]
    
    st.divider()
    
    st.header("📁 Шаблоны")
    if st.button("📄 Бюджетная таблица"):
        st.session_state.template = "budget"
    if st.button("⚠️ Чек-лист рисков"):
        st.session_state.template = "risks"
    if st.button("🎯 Структура презентации"):
        st.session_state.template = "presentation"
    
    st.divider()
    
    # Очистка истории
    if st.button("🗑️ Очистить историю"):
        st.session_state.history = []
        st.rerun()

# Основная область
col1, col2 = st.columns([2, 1])

with col1:
    st.header(f"Задача: {task}")
    
    # Поле ввода с примером
    example_texts = {
        "budget": "Пример: 'Нужно создать бюджет для школьного медиацентра. Требуется: 3 ноутбука, камера, микрофоны, ПО для монтажа. Бюджет до 150 000 руб.'",
        "risks": "Пример: 'Определи риски для проекта школьного научного клуба. Включи: технические, кадровые, организационные риски.'",
        "presentation": "Пример: 'Нужна структура 7-минутной презентации проекта \"Экологический патруль\" для конкурса. Аудитория — городская администрация.'"
    }
    
    user_input = st.text_area(
        "Опишите вашу задачу:",
        value=example_texts.get(st.session_state.current_task, ""),
        height=150,
        key="user_input"
    )
    
    # Кнопки действий
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🚀 Получить решение", type="primary", use_container_width=True):
            if user_input and user_input != example_texts.get(st.session_state.current_task, ""):
                with st.spinner("Gemini анализирует задачу..."):
                    # Добавляем запрос в историю
                    st.session_state.history.append({
                        "role": "user", 
                        "content": user_input,
                        "task": st.session_state.current_task
                    })
                    
                    # Получаем ответ
                    response = assistant.generate_response(
                        user_input, 
                        st.session_state.current_task,
                        st.session_state.history
                    )
                    
                    # Добавляем ответ в историю
                    st.session_state.history.append({
                        "role": "assistant",
                        "content": response,
                        "task": st.session_state.current_task
                    })
                    
                    st.rerun()
    
    with col_btn2:
        if st.button("💾 Экспорт в Google Docs", use_container_width=True):
            st.info("Функция экспорта в разработке...")
    
    with col_btn3:
        if st.button("📥 Скачать шаблон", use_container_width=True):
            st.info("Выберите шаблон в боковой панели")

with col2:
    st.header("📝 История диалога")
    
    if st.session_state.history:
        for i, msg in enumerate(st.session_state.history[-5:]):  # Показываем последние 5 сообщений
            with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                # Обрезаем длинные сообщения для предпросмотра
                preview = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
                st.markdown(f"**{msg['task'].upper()}** - {msg['role'].title()}")
                st.markdown(preview)
                if st.button("📄 Показать полностью", key=f"show_{i}"):
                    st.session_state[f"show_full_{i}"] = not st.session_state.get(f"show_full_{i}", False)
                
                if st.session_state.get(f"show_full_{i}", False):
                    st.markdown(msg["content"])
    else:
        st.info("История диалога пуста. Начните общение!")

# Отображение последнего ответа
if st.session_state.history and st.session_state.history[-1]["role"] == "assistant":
    st.divider()
    st.header("💡 Решение от Gemini")
    
    last_response = st.session_state.history[-1]["content"]
    
    # Парсинг ответа для красивого отображения
    if "|" in last_response and "-" in last_response:  # Обнаружили таблицу Markdown
        # Пытаемся извлечь таблицу
        lines = last_response.split('\n')
        table_start = None
        table_end = None
        
        for i, line in enumerate(lines):
            if "|---" in line:
                table_start = i - 1
            elif table_start is not None and "---" not in line and "|" in line:
                table_end = i
        
        if table_start is not None and table_end is not None:
            table_lines = lines[table_start:table_end+1]
            table_md = "\n".join(table_lines)
            
            # Отображаем таблицу
            st.markdown("### 📊 Сгенерированная таблица")
            st.markdown(table_md)
            
            # Остальной текст
            other_text = "\n".join(lines[:table_start] + lines[table_end+1:])
            if other_text.strip():
                st.markdown("### 📝 Рекомендации")
                st.markdown(other_text)
    else:
        # Просто отображаем текст
        st.markdown(last_response)
    
    # Кнопки для работы с ответом
    col_copy, col_save = st.columns(2)
    with col_copy:
        if st.button("📋 Копировать ответ"):
            st.code(last_response, language="markdown")
            st.success("Ответ скопирован в буфер (используйте Ctrl+C)")
    
    with col_save:
        if st.button("💾 Сохранить в файл"):
            with open(f"рекомендации_{st.session_state.current_task}.md", "w", encoding="utf-8") as f:
                f.write(last_response)
            st.success(f"Файл сохранен: рекомендации_{st.session_state.current_task}.md")

# Информация о системе
with st.expander("ℹ️ О системе"):
    st.markdown("""
    **Технологии:**
    - Backend: Google Gemini Pro 1.5 API
    - Frontend: Streamlit (Python)
    - Контекст: 8192 токена
    - История: 6 последних сообщений
    
    **Особенности:**
    - Бесплатный API (до 60 запросов в минуту)
    - Поддержка мультимодальности (текст, изображения, PDF)
    - Интеграция с Google Workspace (в разработке)
    - Сохранение контекста диалога
    """)