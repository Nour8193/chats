import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiAssistant:
    def __init__(self):
        # Настройка Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Конфигурация модели
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # Инициализация модели
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # История диалога
        self.history = []
    
    def get_system_prompt(self, task_type):
        """Получение системного промпта в зависимости от задачи"""
        prompts = {
            "budget": """Ты — эксперт по бюджетированию образовательных проектов. Твоя задача:
1. Помогать создавать реалистичные сметы для школьных проектов
2. Предлагать источники финансирования (гранты, краудфандинг, спонсоры)
3. Давать советы по экономии средств
4. Создавать таблицы в формате Markdown

Всегда структурируй ответ: сначала краткий вывод, затем детали в таблицах, затем рекомендации.""",
            
            "risks": """Ты — риск-менеджер с опытом в образовании. Твоя задача:
1. Выявлять потенциальные риски проектов
2. Оценивать вероятность и влияние
3. Предлагать конкретные меры минимизации
4. Создавать чек-листы действий

Используй матрицу рисков и предоставляй практические рекомендации.""",
            
            "presentation": """Ты — специалист по презентациям и сторителлингу. Твоя задача:
1. Создавать структуру презентации для разных аудиторий
2. Предлагать визуальные идеи
3. Готовить тезисы для выступления
4. Продумывать ответы на сложные вопросы

Фокус на образовательных проектах для школьной аудитории."""
        }
        return prompts.get(task_type, "Ты — помощник педагога в реализации проектов.")
    
    def generate_response(self, user_input, task_type="general", history=None):
        """Генерация ответа с учетом истории"""
        system_prompt = self.get_system_prompt(task_type)
        
        # Формирование полного промпта с историей
        full_prompt = f"{system_prompt}\n\n"
        
        if history:
            for msg in history[-6:]:  # Берем последние 6 сообщений для контекста
                role = "Пользователь" if msg["role"] == "user" else "Ассистент"
                full_prompt += f"{role}: {msg['content']}\n\n"
        
        full_prompt += f"Пользователь: {user_input}\n\nАссистент:"
        
        # Генерация ответа
        response = self.model.generate_content(full_prompt)
        
        return response.text