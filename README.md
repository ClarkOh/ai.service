# AI 텍스트 분석/요약 서비스

Python과 OpenAI API 또는 Google Gemini API를 사용한 텍스트 분석 및 요약 서비스입니다.

## 🎯 두 가지 버전 제공

| 버전 | 파일명 | 특징 | 비용 |
|------|--------|------|------|
| **OpenAI** | `text_analyzer_openai.py` | 고성능, 안정적 | 유료 (결제 필요) 💳 |
| **Gemini** | `text_analyzer_gemini.py` | 무료 티어, 빠른 시작 | 무료! 🎉 |

**추천:**
- 🧪 **테스트/학습**: Gemini 버전 사용 (무료!)
- 🚀 **프로덕션**: OpenAI 버전 사용 (더 안정적)

## 기능

### 공통 기능 (양쪽 버전 모두 지원)
1. **텍스트 요약**: 긴 텍스트를 짧게, 보통, 길게 세 가지 옵션으로 요약
2. **감정 분석**: 텍스트의 긍정/부정/중립 감정 분석
3. **키워드 추출**: 텍스트에서 핵심 키워드 추출
4. **주제 분석**: 텍스트의 주요 주제 파악

### Gemini 버전 추가 기능
5. **번역**: 다양한 언어로 번역
6. **텍스트 확장**: 짧은 텍스트를 상세하게 확장

## 설치 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 API 키를 설정하세요:

```env
# OpenAI 사용 시
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Gemini 사용 시
GEMINI_API_KEY=your-gemini-key-here
```

#### 🔑 OpenAI API 키 발급 (유료)
1. [OpenAI Platform](https://platform.openai.com/)에 로그인
2. API Keys 메뉴로 이동
3. "Create new secret key" 클릭
4. **결제 정보 등록 필수** (최소 $5 충전)
5. 생성된 키를 `.env` 파일에 추가

#### 🔑 Gemini API 키 발급 (무료!)
1. [Google AI Studio](https://makersuite.google.com/app/apikey)에 접속
2. Google 계정으로 로그인
3. "Get API Key" 클릭
4. **결제 정보 불필요!** 바로 사용 가능
5. 생성된 키를 `.env` 파일에 추가

## 사용 방법

### 기본 실행

#### OpenAI 버전 (유료)
```bash
python text_analyzer_openai.py
```

#### Gemini 버전 (무료 추천! 🎉)
```bash
python text_analyzer_gemini.py
```

예제 텍스트로 모든 기능을 자동으로 테스트합니다.

### 코드에서 사용하기

#### OpenAI 버전
```python
from text_analyzer_openai import TextAnalyzer

# TextAnalyzer 초기화
analyzer = TextAnalyzer()

# 텍스트 요약
text = "요약할 긴 텍스트..."
summary = analyzer.summarize(text, max_length="short")
print(summary)

# 감정 분석
sentiment = analyzer.analyze_sentiment(text)
print(sentiment)

# 키워드 추출
keywords = analyzer.extract_keywords(text, num_keywords=5)
print(keywords)

# 주제 분석
topics = analyzer.analyze_topics(text)
print(topics)
```

#### Gemini 버전
```python
from text_analyzer_gemini import GeminiTextAnalyzer

# GeminiTextAnalyzer 초기화
analyzer = GeminiTextAnalyzer()

# 텍스트 요약
text = "요약할 긴 텍스트..."
summary = analyzer.summarize(text, max_length="short")
print(summary)

# 감정 분석
sentiment = analyzer.analyze_sentiment(text)
print(sentiment)

# 키워드 추출
keywords = analyzer.extract_keywords(text, num_keywords=5)
print(keywords)

# 주제 분석
topics = analyzer.analyze_topics(text)
print(topics)

# 번역 (Gemini 전용)
translation = analyzer.translate(text, target_language="영어")
print(translation)

# 텍스트 확장 (Gemini 전용)
expanded = analyzer.expand_text("짧은 텍스트")
print(expanded)
```

## API 상세 설명

### OpenAI - TextAnalyzer 클래스

#### `__init__(api_key=None, model="gpt-4o-mini")`
- `api_key`: OpenAI API 키 (선택사항, 환경 변수에서 자동으로 로드)
- `model`: 사용할 GPT 모델
  - `gpt-4o-mini`: 빠르고 저렴 (권장)
  - `gpt-4o`: 더 정확하지만 비쌈
  - `gpt-3.5-turbo`: 가장 저렴

### Gemini - GeminiTextAnalyzer 클래스

#### `__init__(api_key=None, model="gemini-2.5-flash")`
- `api_key`: Gemini API 키 (선택사항, gemini.api.key.txt에서 자동으로 로드)
- `model`: 사용할 Gemini 모델
  - `gemini-2.5-flash`: 최신 빠른 모델 (기본값, 무료 티어) ⭐
  - `gemini-2.5-pro`: 최신 강력한 모델 (무료 티어)
  - `gemini-2.0-flash`: 안정적인 이전 버전
  - `gemini-flash-latest`: 자동으로 최신 플래시 모델 사용

### 공통 메서드

#### `summarize(text, language="한국어", max_length="medium")`
텍스트를 요약합니다.
- `text`: 요약할 텍스트
- `language`: 요약 언어 (한국어, 영어 등)
- `max_length`: 요약 길이
  - `"short"`: 3문장 이내
  - `"medium"`: 5-7문장
  - `"long"`: 상세한 여러 문단

#### `analyze_sentiment(text)`
텍스트의 감정을 분석합니다.
- 반환값: JSON 형식의 감정 분석 결과

#### `extract_keywords(text, num_keywords=5)`
핵심 키워드를 추출합니다.
- `num_keywords`: 추출할 키워드 개수

#### `analyze_topics(text)`
텍스트의 주요 주제를 분석합니다.

### Gemini 전용 메서드

#### `translate(text, target_language="영어")`
텍스트를 다른 언어로 번역합니다.

#### `expand_text(text)`
짧은 텍스트를 더 상세하게 확장합니다.

## 비용 안내

### OpenAI API (유료)
사용량에 따라 과금됩니다:
- **gpt-4o-mini**: 
  - 입력: $0.15 / 1M 토큰
  - 출력: $0.60 / 1M 토큰
- **gpt-4o**:
  - 입력: $2.50 / 1M 토큰
  - 출력: $10.00 / 1M 토큰

대략 1,000자의 한글 텍스트는 약 600-800 토큰 정도입니다.

### Google Gemini API (무료! 🎉)
**무료 티어 제공:**
- 결제 정보 등록 불필요
- **제한사항:**
  - 분당 15회 요청 (RPM)
  - 일일 1,500회 요청 (RPD)
- 개인 프로젝트/학습용으로 충분!

**비교:**
- OpenAI $5로 약 2,500~5,000회 요약
- Gemini는 무료로 매일 1,500회 가능!

## 에러 처리

API 호출 중 에러가 발생하면 에러 메시지를 반환합니다. 주요 에러:
- **인증 오류**: API 키가 잘못되었거나 만료됨
- **할당량 초과**: API 사용 한도 초과
- **요청 오류**: 입력 텍스트가 너무 길거나 형식이 잘못됨

## 라이선스

MIT License

## 문의

이슈가 있으면 GitHub Issues에 등록해주세요.

