import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

class GeminiAssistant:
    def __init__(self):
        # Настройка Gemini API с корректным ключом
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY не найден в .env файле")
        
        genai.configure(api_key=api_key)
        
        # Инициализация модели
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Настройка параметров генерации
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    
    def get_system_prompt(self, task_type):
        """Получение системного промпта"""
        base_prompt = """Ты — "Проектный навигатор", ИИ-помощник для педагогов. 
        Твоя задача — помогать в планировании и реализации образовательных проектов.
        Будь конкретным, практичным, предлагай готовые шаблоны и таблицы.
        Форматируй ответ с использованием Markdown."""
        
        task_prompts = {
            "budget": f"""{base_prompt}
            СФОКУСИРУЙСЯ НА:
            1. Создание реалистичных бюджетных таблиц
            2. Поиск источников финансирования (гранты, спонсоры)
            3. Советы по оптимизации расходов
            4. Шаблоны для Google Sheets
            
            Формат: краткий вывод → таблица → рекомендации""",
            
            "risks": f"""{base_prompt}
            СФОКУСИРУЙСЯ НА:
            1. Идентификация рисков по категориям
            2. Матрица вероятности/влияния
            3. Конкретные меры минимизации
            4. Чек-листы действий
            
            Используй таблицы и списки.""",
            
            "presentation": f"""{base_prompt}
            СФОКУСИРУЙСЯ НА:
            1. Структура презентации по времени
            2. Визуальные идеи
            3. Ключевые сообщения
            4. Ответы на вопросы
            
            Предлагай конкретные слайды."""
        }
        
        return task_prompts.get(task_type, base_prompt)
    
    def generate_response(self, user_input, task_type="general", history=None):
        """Основная функция генерации ответа"""
        try:
            # Формируем полный промпт
            system_prompt = self.get_system_prompt(task_type)
            
            # Добавляем историю если есть
            context = ""
            if history and len(history) > 0:
                for msg in history[-4:]:  # Берем последние 4 сообщения
                    role_prefix = "Пользователь: " if msg["role"] == "user" else "Ассистент: "
                    context += f"{role_prefix}{msg['content']}\n\n"
            
            full_prompt = f"{system_prompt}\n\n{context}Пользователь: {user_input}\n\nАссистент:"
            
            # Генерируем ответ
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            # Проверяем и возвращаем ответ
            if response and hasattr(response, 'text'):
                return response.text
            else:
                return "Не удалось получить ответ от Gemini API. Проверьте API ключ."
                
        except Exception as e:
            return f"Ошибка при генерации ответа: {str(e)}\n\nПроверьте:\n1. API ключ\n2. Интернет-соединение\n3. Лимиты Gemini API"
