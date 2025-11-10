"""
Google Gemini API를 사용한 텍스트 분석 및 요약 서비스
무료 티어로 사용 가능! (결제 정보 불필요)
"""
import os
import google.generativeai as genai
from pathlib import Path

class GeminiTextAnalyzer:
    """Google Gemini를 사용한 텍스트 분석 및 요약 클래스"""
    
    def __init__(self, api_key=None, model="gemini-2.5-flash"):
        """
        GeminiTextAnalyzer 초기화
        
        Args:
            api_key (str): Google Gemini API 키 (없으면 gemini.api.key.txt 파일에서 가져옴)
            model (str): 사용할 Gemini 모델 (기본값: gemini-2.5-flash)
        """
        # API 키 로드: 매개변수 -> 파일 -> 환경 변수 순서
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self._load_api_key_from_file()
        
        if not self.api_key:
            raise ValueError(
                "API 키가 필요합니다.\n"
                "1. gemini.api.key.txt 파일에 API 키를 저장하거나\n"
                "2. api_key 매개변수로 직접 전달하세요."
            )
        
        # Gemini API 설정
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        
        # 안전 설정 (제한 완화)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    
    def _load_api_key_from_file(self):
        """
        gemini.api.key.txt 파일에서 API 키를 읽어옵니다.
        
        Returns:
            str: API 키 또는 None
        """
        key_file = Path("gemini.api.key.txt")
        
        if key_file.exists():
            try:
                with open(key_file, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
                    if api_key:
                        print(f"[OK] API key loaded from key file")
                        return api_key
            except Exception as e:
                print(f"[WARNING] Error reading gemini.api.key.txt: {e}")
        
        return None
    
    def _generate_content(self, prompt):
        """
        Gemini API 호출 헬퍼 함수
        
        Args:
            prompt (str): 프롬프트
            
        Returns:
            str: 생성된 텍스트
        """
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def summarize(self, text, language="한국어", max_length="medium"):
        """
        텍스트를 요약합니다.
        
        Args:
            text (str): 요약할 텍스트
            language (str): 요약 언어 (기본값: 한국어)
            max_length (str): 요약 길이 (short, medium, long)
        
        Returns:
            str: 요약된 텍스트
        """
        length_prompts = {
            "short": "3문장 이내로",
            "medium": "5-7문장 정도로",
            "long": "상세하게 여러 문단으로"
        }
        
        length_instruction = length_prompts.get(max_length, length_prompts["medium"])
        
        prompt = f"""다음 텍스트를 {language}로 {length_instruction} 요약해주세요:

{text}

요약:"""
        
        return self._generate_content(prompt)
    
    def analyze_sentiment(self, text):
        """
        텍스트의 감정을 분석합니다.
        
        Args:
            text (str): 분석할 텍스트
        
        Returns:
            str: 감정 분석 결과
        """
        prompt = f"""다음 텍스트의 감정을 분석하고 JSON 형식으로 답변해주세요:

텍스트: {text}

다음 형식으로 응답해주세요:
{{
    "sentiment": "긍정/부정/중립",
    "confidence": "높음/중간/낮음",
    "explanation": "감정 분석에 대한 간단한 설명"
}}"""
        
        return self._generate_content(prompt)
    
    def extract_keywords(self, text, num_keywords=5):
        """
        텍스트에서 핵심 키워드를 추출합니다.
        
        Args:
            text (str): 분석할 텍스트
            num_keywords (int): 추출할 키워드 개수
        
        Returns:
            str: 추출된 키워드 목록
        """
        prompt = f"""다음 텍스트에서 가장 중요한 키워드 {num_keywords}개를 추출해주세요:

{text}

키워드를 쉼표로 구분하여 나열해주세요."""
        
        return self._generate_content(prompt)
    
    def analyze_topics(self, text):
        """
        텍스트의 주제를 분석합니다.
        
        Args:
            text (str): 분석할 텍스트
        
        Returns:
            str: 주제 분석 결과
        """
        prompt = f"""다음 텍스트의 주요 주제들을 분석하고, 각 주제에 대해 간단히 설명해주세요:

{text}

주제 분석:"""
        
        return self._generate_content(prompt)
    
    def translate(self, text, target_language="영어"):
        """
        텍스트를 번역합니다.
        
        Args:
            text (str): 번역할 텍스트
            target_language (str): 목표 언어
        
        Returns:
            str: 번역된 텍스트
        """
        prompt = f"""다음 텍스트를 {target_language}로 자연스럽게 번역해주세요:

{text}

번역:"""
        
        return self._generate_content(prompt)
    
    def expand_text(self, text):
        """
        짧은 텍스트를 더 상세하게 확장합니다.
        
        Args:
            text (str): 확장할 텍스트
        
        Returns:
            str: 확장된 텍스트
        """
        prompt = f"""다음 짧은 텍스트를 더 상세하고 풍부하게 확장해주세요:

{text}

확장된 내용:"""
        
        return self._generate_content(prompt)


def main():
    """메인 함수 - 사용 예제"""
    
    print("=" * 60)
    print("Google Gemini Text Analysis Service")
    print("Free Tier Available!")
    print("=" * 60)
    
    # GeminiTextAnalyzer 초기화
    try:
        analyzer = GeminiTextAnalyzer()
    except ValueError as e:
        print(f"\n[ERROR] {e}")
        print("\nSetup Instructions:")
        print("1. Visit: https://makersuite.google.com/app/apikey")
        print("2. Generate API Key")
        print("3. Create gemini.api.key.txt in project folder")
        print("4. Paste API key in first line")
        return
    
    # 예제 텍스트
    sample_text = """
    인공지능 기술의 발전은 우리 사회에 큰 변화를 가져오고 있습니다. 
    특히 자연어 처리 분야에서는 GPT와 같은 대규모 언어 모델이 등장하면서 
    기계가 인간의 언어를 이해하고 생성하는 능력이 크게 향상되었습니다. 
    이러한 기술은 번역, 요약, 질의응답 등 다양한 분야에서 활용되고 있으며, 
    앞으로도 더욱 발전할 것으로 기대됩니다. 하지만 동시에 윤리적 문제와 
    일자리 대체 등의 우려도 함께 제기되고 있어, 책임 있는 기술 개발과 
    활용이 중요합니다.
    """
    
    # 1. Text Summary
    print("\n[1] Text Summary (Short)")
    print("-" * 60)
    summary_short = analyzer.summarize(sample_text, max_length="short", language="Korean")
    print(summary_short)
    
    print("\n[2] Text Summary (Medium)")
    print("-" * 60)
    summary_medium = analyzer.summarize(sample_text, max_length="medium", language="Korean")
    print(summary_medium)
    
    # 2. Sentiment Analysis
    print("\n[3] Sentiment Analysis")
    print("-" * 60)
    sentiment = analyzer.analyze_sentiment(sample_text)
    print(sentiment)
    
    # 3. Keyword Extraction
    print("\n[4] Keyword Extraction")
    print("-" * 60)
    keywords = analyzer.extract_keywords(sample_text, num_keywords=5)
    print(keywords)
    
    # 4. Topic Analysis
    print("\n[5] Topic Analysis")
    print("-" * 60)
    topics = analyzer.analyze_topics(sample_text)
    print(topics)
    
    # 5. Translation
    print("\n[6] Translation to English")
    print("-" * 60)
    translation = analyzer.translate(sample_text[:100], target_language="English")
    print(translation)
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("Tip: Free tier limits - 15 RPM, 1500 RPD")
    print("=" * 60)


if __name__ == "__main__":
    main()

