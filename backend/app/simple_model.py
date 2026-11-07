import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os
import re

class SimpleAIModel:
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.ai_indicators = [
            "следует отметить", "кроме того", "более того",
            "необходимо подчеркнуть", "в заключение", "в рамках",
            "представляет собой", "является", "данный подход",
            "значительный прогресс", "высокая степень", "эффективное решение"
        ]
        self.initialized = False
    
    def initialize(self):
        """Инициализация модели - быстро и просто"""
        print("🤖 Инициализация AI детектора...")
        
        try:
            # Пробуем загрузить сохранённую модель
            if os.path.exists("ai_model.pkl"):
                with open("ai_model.pkl", 'rb') as f:
                    self.vectorizer, self.model = pickle.load(f)
                print("📦 Модель загружена из файла")
            else:
                print("📊 Создаём быструю модель...")
                self._create_quick_model()
                
            self.initialized = True
            print("✅ AI детектор готов к работе!")
            
        except Exception as e:
            print(f"⚠️ Ошибка инициализации: {e}")
            print("🔄 Использую эвристический метод...")
            self.initialized = True  # Всё равно отмечаем как готовый
    
    def _create_quick_model(self):
        """Создаём быструю модель на небольшом наборе данных"""
        # Минимальный набор данных для быстрого старта
        ai_texts = [
            "следует отметить важность данного вопроса",
            "кроме того необходимо учитывать аспекты",
            "в заключение можно сказать что результаты",
            "в рамках исследования был применен подход",
            "данный метод представляет собой решение"
        ]
        
        human_texts = [
            "привет как дела у меня все нормально",
            "вчера смотрел фильм вообще огонь",
            "не знаю что делать все валится",
            "пойду погуляю на улице хорошая погода",
            "этот проект реально крутой нравится"
        ]
        
        # Векторизация
        self.vectorizer = TfidfVectorizer(max_features=100)
        texts = ai_texts + human_texts
        X = self.vectorizer.fit_transform(texts)
        
        # Простая модель
        self.model = LogisticRegression(random_state=42)
        y = [1] * len(ai_texts) + [0] * len(human_texts)
        self.model.fit(X, y)
        
        # Сохраняем
        with open("ai_model.pkl", 'wb') as f:
            pickle.dump((self.vectorizer, self.model), f)
    
    def predict(self, text: str):
        """Предсказание для текста"""
        if not self.initialized:
            return self._fallback_prediction(text)
        
        try:
            # Проверка AI маркеров
            ai_markers = self._count_ai_markers(text)
            
            # Если есть векторная модель, используем её
            if self.vectorizer and self.model:
                X = self.vectorizer.transform([text])
                ai_prob = self.model.predict_proba(X)[0][1]
                
                # Корректировка на маркеры
                marker_bonus = ai_markers * 0.15
                final_prob = min(0.95, ai_prob + marker_bonus)
                
                return {
                    "ai_probability": float(final_prob),
                    "human_probability": 1 - float(final_prob),
                    "is_ai_generated": final_prob > 0.55,
                    "confidence": 0.6 + (final_prob - 0.5) * 0.4,
                    "model_type": "ml_model",
                    "ai_markers": ai_markers
                }
            else:
                # Только эвристики
                return self._heuristic_prediction(text)
                
        except Exception as e:
            print(f"⚠️ Ошибка предсказания: {e}")
            return self._heuristic_prediction(text)
    
    def _count_ai_markers(self, text: str) -> int:
        """Считаем AI маркеры в тексте"""
        text_lower = text.lower()
        count = 0
        for marker in self.ai_indicators:
            if marker in text_lower:
                count += 1
        return count
    
    def _heuristic_prediction(self, text: str):
        """Эвристическое предсказание"""
        ai_markers = self._count_ai_markers(text)
        words = text.split()
        
        # Базовая вероятность
        base_prob = 0.3
        
        # Добавляем за маркеры
        base_prob += ai_markers * 0.15
        
        # Добавляем за длинные предложения
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        if sentences:
            avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_len > 15:
                base_prob += 0.2
            elif avg_len > 10:
                base_prob += 0.1
        
        # Ограничиваем диапазон
        final_prob = max(0.05, min(0.95, base_prob))
        
        return {
            "ai_probability": final_prob,
            "human_probability": 1 - final_prob,
            "is_ai_generated": final_prob > 0.5,
            "confidence": 0.4 + abs(final_prob - 0.5) * 0.3,
            "model_type": "heuristic",
            "ai_markers": ai_markers
        }
    
    def _fallback_prediction(self, text: str):
        """Запасной вариант"""
        return {
            "ai_probability": 0.5,
            "human_probability": 0.5,
            "is_ai_generated": False,
            "confidence": 0.3,
            "model_type": "fallback",
            "ai_markers": 0
        }

# Создаём глобальный экземпляр
ai_model = SimpleAIModel()
