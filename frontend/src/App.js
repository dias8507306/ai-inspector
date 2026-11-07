import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [activeTab, setActiveTab] = useState("text");
  const [text, setText] = useState("");
  const [image, setImage] = useState(null);
  const [video, setVideo] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Анализ текста
  const analyzeText = async () => {
    if (!text.trim()) {
      alert("Введите текст для анализа");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const response = await axios.post(`${API_BASE}/api/analyze/text`, {
        text: text,
      });
      setResult(response.data);
    } catch (err) {
      setError("Ошибка при анализе текста: " + (err.message || "неизвестная ошибка"));
    }
    
    setLoading(false);
  };

  // Анализ изображения
  const analyzeImage = async () => {
    if (!image) {
      alert("Выберите изображение");
      return;
    }
    
    setLoading(true);
    setError("");
    
    const formData = new FormData();
    formData.append("file", image);
    
    try {
      const response = await axios.post(`${API_BASE}/api/analyze/image`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setResult(response.data);
    } catch (err) {
      setError("Ошибка при анализе изображения: " + (err.message || "неизвестная ошибка"));
    }
    
    setLoading(false);
  };

  // Анализ видео
  const analyzeVideo = async () => {
    if (!video) {
      alert("Выберите видео");
      return;
    }
    
    setLoading(true);
    setError("");
    
    const formData = new FormData();
    formData.append("file", video);
    
    try {
      const response = await axios.post(`${API_BASE}/api/analyze/video`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setResult(response.data);
    } catch (err) {
      setError("Ошибка при анализе видео: " + (err.message || "неизвестная ошибка"));
    }
    
    setLoading(false);
  };

  // Сброс формы
  const resetForm = () => {
    setText("");
    setImage(null);
    setVideo(null);
    setResult(null);
    setError("");
  };

  return (
    <div className="app">
      <header>
        <h1>🔍 AI Inspector</h1>
        <p>Multi-Modal AI Detector - Анализ текста, фото и видео</p>
      </header>

      <div className="tabs">
        <button 
          className={activeTab === "text" ? "active" : ""}
          onClick={() => { setActiveTab("text"); resetForm(); }}
        >
          📝 Текст
        </button>
        <button 
          className={activeTab === "image" ? "active" : ""}
          onClick={() => { setActiveTab("image"); resetForm(); }}
        >
          🖼️ Изображение
        </button>
        <button 
          className={activeTab === "video" ? "active" : ""}
          onClick={() => { setActiveTab("video"); resetForm(); }}
        >
          🎥 Видео
        </button>
      </div>

      <div className="input-area">
        {activeTab === "text" && (
          <div className="text-input">
            <textarea
              placeholder="Введите текст для анализа на AI-генерацию..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={8}
            />
            <button onClick={analyzeText} disabled={loading || !text.trim()}>
              {loading ? "Анализ..." : "Анализировать текст"}
            </button>
          </div>
        )}

        {activeTab === "image" && (
          <div className="file-input">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setImage(e.target.files[0])}
            />
            {image && (
              <div className="file-preview">
                <p>Выбрано: {image.name}</p>
                <img src={URL.createObjectURL(image)} alt="Preview" height="150" />
              </div>
            )}
            <button onClick={analyzeImage} disabled={loading || !image}>
              {loading ? "Анализ..." : "Анализировать изображение"}
            </button>
          </div>
        )}

        {activeTab === "video" && (
          <div className="file-input">
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setVideo(e.target.files[0])}
            />
            {video && (
              <div className="file-preview">
                <p>Выбрано: {video.name}</p>
                <video src={URL.createObjectURL(video)} height="150" controls />
              </div>
            )}
            <button onClick={analyzeVideo} disabled={loading || !video}>
              {loading ? "Анализ..." : "Анализировать видео"}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="error">
          <h3>❌ Ошибка</h3>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="result">
          <h2>📊 Результат анализа {result.type === "text" ? "текста" : result.type === "image" ? "изображения" : "видео"}</h2>
          
          <div className={result.is_ai_generated ? "result-ai" : "result-human"}>
            <h3>{result.is_ai_generated ? "🤖 Вероятно AI" : "👨‍💻 Вероятно человек"}</h3>
            
            <div className="probability-bar">
              <div className="probability-labels">
                <span>Человек: {(result.human_probability * 100).toFixed(1)}%</span>
                <span>AI: {(result.ai_probability * 100).toFixed(1)}%</span>
              </div>
              <div className="probability-track">
                <div 
                  className="probability-fill"
                  style={{ width: `${result.ai_probability * 100}%` }}
                ></div>
              </div>
            </div>
            
            <p><strong>Достоверность:</strong> {(result.confidence * 100).toFixed(1)}%</p>
            
            {result.type === "text" && (
              <>
                <p><strong>Длина текста:</strong> {result.text_length} символов</p>
                <p><strong>Количество слов:</strong> {result.words_count}</p>
                {result.details && (
                  <div className="details">
                    <p><strong>AI-маркеров найдено:</strong> {result.details.ai_markers_found}</p>
                    <p><strong>Средняя длина предложения:</strong> {result.details.avg_sentence_length} слов</p>
                  </div>
                )}
              </>
            )}
            
            {(result.type === "image" || result.type === "video") && (
              <>
                <p><strong>Файл:</strong> {result.filename}</p>
                {result.details && (
                  <div className="details">
                    {result.details.resolution && <p><strong>Разрешение:</strong> {result.details.resolution}</p>}
                    {result.details.file_size_kb && <p><strong>Размер:</strong> {result.details.file_size_kb} KB</p>}
                    {result.details.file_size_mb && <p><strong>Размер:</strong> {result.details.file_size_mb} MB</p>}
                    {result.details.format && <p><strong>Формат:</strong> {result.details.format}</p>}
                    <p><strong>Метод анализа:</strong> {result.details.analysis_method}</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
