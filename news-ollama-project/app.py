import os
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_folder='static') 

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "b04f614c7a654def93947716bc3e4bea")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

# ====================================================================
# NewsAPI를 호출하여 기사 목록을 가져옴
# ====================================================================

def fetch_news(query, api_key):
    """NewsAPI를 사용하여 최신 뉴스를 가져옵니다."""
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&pageSize=5&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 기사 내용만 추출하여 문자열로 결합
        articles = data.get("articles", [])

        news_content = []
        for article in articles:
            # 제목과 설명을 사용
            if article.get("title") and article['description']:
                news_content.append(f"TITLE: {article['title']}\nDESCRIPTION: {article['description']}\n---\n")

        return "".join(news_content), len(articles)
        
    except requests.exceptions.RequestException as e:
        app.logger.error(f"NewsAPI 호출 오류: {e}")
        return None, 0
    
# ====================================================================
# Ollama API를 호출하여 텍스트를 처리
# ====================================================================

def summarize_with_ollama(news_data, prompt_modifier=""):
    """Ollama 모델에게 뉴스 데이터를 요약하도록 요청합니다."""
    
    # 모델에 전달할 프롬프트 구성
    system_prompt = (
        "You are an expert news summarizer. Summarize the following news articles "
        "into a concise, easy-to-read list of 3 bullet points in Korean. "
        "Focus on the main themes and most important information. "
        f"{prompt_modifier}"
    )
    
    # Ollama API 요청 본문
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": news_data,
        "system": system_prompt,
        "stream": False # 스트리밍 없이 한번에 응답 받기
    }
    
    # Ollama API 엔드포인트
    ollama_url = f"{OLLAMA_HOST}/api/generate"
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=300) # 타임아웃 5분 설정
        response.raise_for_status()
        
        # Ollama 응답 파싱
        ollama_response = response.json()
        summary = ollama_response.get("response", "요약 생성에 실패했습니다.")
        
        return summary
        
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Ollama API 호출 오류: {e}")
        return f"Ollama 연결 또는 처리 오류: {e}. OLLAMA_HOST: {OLLAMA_HOST}, 모델: {OLLAMA_MODEL}"
    
# ====================================================================
# Flask 라우트
# ====================================================================

@app.route('/')
def index():
    """메인 페이지 렌더링"""
    return render_template('index.html') 

@app.route('/api/process', methods=['POST'])
def process_request():
    """사용자 요청을 받아 뉴스 가져오기 및 요약 처리를 수행합니다."""
    data = request.json
    query = data.get('query', 'AI') # 기본 검색어는 'AI'

    # 1. NewsAPI 호출 (이제 올바른 변수 NEWS_API_KEY를 전달합니다)
    news_data, num_articles = fetch_news(query, NEWS_API_KEY)

    if not news_data:
        return jsonify({
            "success": False, 
            "result": f"뉴스 검색에 실패했습니다. (검색어: {query})"
        })

    # 2. Ollama에게 요약 요청
    prompt_modifier = f"({num_articles}개의 기사 요약)"
    summary = summarize_with_ollama(news_data, prompt_modifier)

    return jsonify({
        "success": True,
        "query": query,
        "articles_count": num_articles,
        "news_snippet": news_data[:300] + "...", # 뉴스 원본 일부
        "result": summary
    })


if __name__ == '__main__':
    # Docker 환경을 위해 0.0.0.0 바인딩
    app.run(host='0.0.0.0', port=5000)