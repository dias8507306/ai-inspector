from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from PIL import Image
import numpy as np
from typing import Optional

app = FastAPI(title="Multi-Modal AI Inspector")

# CORS - разрешаем всё для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Папка для загрузок
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== ТЕКСТ ==========
class TextRequest(BaseModel):
    text: str

@app.post("/api/analyze/text")
async def analyze_text(request: TextRequest):
    """Анализ текста на AI-генерацию"""
    print(f"📝 Получен текст: {request.text[:50]}...")
    
    text = request.text.lower()
    
    # AI маркеры
    ai_markers = [
        "следует отметить", "кроме того", "более того",
        "необходимо подчеркнуть", "в заключение", "в рамках",
        "представляет собой", "является", "данный подход"
    ]
    
    marker_count = sum(1 for marker in ai_markers if marker in text)
    
    # Эвристический анализ
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    
    ai_prob = 0.3 + (marker_count * 0.1)
    
    if sentences > 0:
        avg_len = len(words) / sentences
        if avg_len > 15:
            ai_prob += 0.2
    
    ai_prob = min(0.95, max(0.05, ai_prob))
    
    result = {
        "type": "text",
        "text_preview": request.text[:100] + "..." if len(request.text) > 100 else request.text,
        "text_length": len(request.text),
        "words_count": len(words),
        "is_ai_generated": ai_prob > 0.6,
        "ai_probability": round(ai_prob, 4),
        "human_probability": round(1 - ai_prob, 4),
        "confidence": round(0.5 + abs(ai_prob - 0.5), 4),
        "details": {
            "ai_markers_found": marker_count,
            "avg_sentence_length": round(len(words) / max(sentences, 1), 1) if sentences > 0 else 0,
            "analysis_method": "heuristic_text_analysis"
        }
    }
    
    print(f"📊 Результат текста: AI={ai_prob:.1%}")
    return result

# ========== ИЗОБРАЖЕНИЯ ==========
@app.post("/api/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """Анализ изображения на AI-генерацию"""
    print(f"🖼️ Получено изображение: {file.filename}")
    
    # Проверяем тип файла
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
        raise HTTPException(status_code=400, detail="Поддерживаются только изображения: PNG, JPG, JPEG, GIF, BMP, WEBP")
    
    # Сохраняем файл
    file_path = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))
    
    try:
        # Читаем содержимое файла
        contents = await file.read()
        
        # Сохраняем
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Анализируем изображение
        result = await _analyze_image_file(file_path, file.filename)
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка анализа изображения: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")
    
    finally:
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)

async def _analyze_image_file(file_path: str, filename: str) -> dict:
    """Анализ файла изображения"""
    try:
        # Открываем изображение
        img = Image.open(file_path)
        
        # Базовый анализ
        width, height = img.size
        file_size = os.path.getsize(file_path) / 1024  # KB
        
        # Простые эвристики для AI-изображений
        ai_score = 0.3
        
        # 1. Проверка на слишком идеальное разрешение
        if width * height > 4000000:  # >4MP
            ai_score += 0.2
        
        # 2. Проверка формата (AI часто в PNG)
        if filename.lower().endswith('.png'):
            ai_score += 0.1
        
        # 3. Анализ цвета
        try:
            img_array = np.array(img)
            if len(img_array.shape) == 3:  # RGB изображение
                # Среднее отклонение цветов
                color_std = np.std(img_array, axis=(0, 1))
                avg_std = np.mean(color_std)
                if avg_std < 20:  # Низкая вариативность цвета
                    ai_score += 0.15
        except:
            pass  # Пропускаем если не можем проанализировать
        
        ai_prob = min(0.9, ai_score)
        
        indicators = []
        if ai_prob > 0.6:
            indicators.append("Высокая вероятность AI-генерации")
        if width * height > 4000000:
            indicators.append("Высокое разрешение")
        if filename.lower().endswith('.png'):
            indicators.append("Формат PNG")
        
        result = {
            "type": "image",
            "filename": filename,
            "is_ai_generated": ai_prob > 0.6,
            "ai_probability": round(ai_prob, 4),
            "human_probability": round(1 - ai_prob, 4),
            "confidence": round(0.4 + abs(ai_prob - 0.5) * 0.5, 4),
            "details": {
                "resolution": f"{width}x{height}",
                "file_size_kb": round(file_size, 2),
                "format": img.format,
                "mode": img.mode,
                "analysis_method": "basic_image_analysis",
                "indicators": indicators
            }
        }
        
        print(f"📊 Результат изображения {filename}: AI={ai_prob:.1%}, {width}x{height}")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка обработки изображения: {e}")
        raise

# ========== ВИДЕО ==========
@app.post("/api/analyze/video")
async def analyze_video(file: UploadFile = File(...)):
    """Анализ видео на AI-генерацию"""
    print(f"🎥 Получено видео: {file.filename}")
    
    # Проверяем тип файла
    allowed_extensions = ('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm')
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Поддерживаются только видео: {', '.join(allowed_extensions)}"
        )
    
    # Сохраняем файл
    file_path = os.path.join(UPLOAD_DIR, os.path.basename(file.filename))
    
    try:
        # Читаем содержимое файла
        contents = await file.read()
        
        # Сохраняем
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Простой анализ видео
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        ext = file.filename.lower().split('.')[-1]
        
        # Эвристики для AI-видео
        ai_score = 0.3
        
        # Проверка формата
        if ext in ['mp4', 'webm']:
            ai_score += 0.1
        
        # Проверка размера
        if file_size_mb > 100:  # Очень большое
            ai_score += 0.2
        elif file_size_mb < 1:   # Очень маленькое
            ai_score += 0.15
        
        ai_prob = min(0.85, ai_score)
        
        result = {
            "type": "video",
            "filename": file.filename,
            "is_ai_generated": ai_prob > 0.6,
            "ai_probability": round(ai_prob, 4),
            "human_probability": round(1 - ai_prob, 4),
            "confidence": round(0.3, 4),
            "details": {
                "file_size_mb": round(file_size_mb, 2),
                "file_extension": ext,
                "analysis_method": "basic_video_analysis",
                "note": "Для точного анализа видео требуется OpenCV"
            }
        }
        
        print(f"📊 Результат видео {file.filename}: AI={ai_prob:.1%}, {file_size_mb:.1f}MB")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка анализа видео: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")
    
    finally:
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)

# ========== ИНФОРМАЦИОННЫЕ ENDPOINTS ==========
@app.get("/")
async def root():
    return {
        "service": "Multi-Modal AI Inspector",
        "version": "1.0.0",
        "endpoints": {
            "analyze_text": "POST /api/analyze/text",
            "analyze_image": "POST /api/analyze/image",
            "analyze_video": "POST /api/analyze/video",
            "docs": "GET /docs"
        },
        "status": "running",
        "uploads_dir": UPLOAD_DIR
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "uploads_dir_exists": os.path.exists(UPLOAD_DIR)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Multi-Modal AI Inspector запущен!")
    print("📡 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("📁 Папка загрузок:", UPLOAD_DIR)
    uvicorn.run(app, host="0.0.0.0", port=8000)
