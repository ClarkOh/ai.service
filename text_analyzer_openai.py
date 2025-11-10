"""
OpenAI API를 사용한 텍스트 분석 및 요약 서비스
"""
import os
from openai import OpenAI
from pathlib import Path

class TextAnalyzer:
    """텍스트 분석 및 요약을 수행하는 클래스"""
    
    def __init__(self, api_key=None, model="gpt-4o-mini"):
        """
        TextAnalyzer 초기화
        
        Args:
            api_key (str): OpenAI API 키 (없으면 open.api.key.txt 파일에서 가져옴)
            model (str): 사용할 GPT 모델 (기본값: gpt-4o-mini)
        """
        # API 키 로드: 매개변수 -> 파일 -> 환경 변수 순서
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self._load_api_key_from_file()
        
        if not self.api_key:
            raise ValueError(
                "API 키가 필요합니다.\n"
                "1. open.api.key.txt 파일에 API 키를 저장하거나\n"
                "2. api_key 매개변수로 직접 전달하세요."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def _load_api_key_from_file(self):
        """
        open.api.key.txt 파일에서 API 키를 읽어옵니다.
        
        Returns:
            str: API 키 또는 None
        """
        key_file = Path("open.api.key.txt")
        
        if key_file.exists():
            try:
                with open(key_file, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
                    if api_key:
                        print(f"✓ open.api.key.txt 파일에서 API 키를 로드했습니다.")
                        return api_key
            except Exception as e:
                print(f"⚠ open.api.key.txt 파일 읽기 오류: {e}")
        
        return None
    
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"당신은 텍스트를 명확하고 간결하게 요약하는 전문가입니다. {language}로 응답합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"오류 발생: {str(e)}"
    
    def analyze_sentiment(self, text):
        """
        텍스트의 감정을 분석합니다.
        
        Args:
            text (str): 분석할 텍스트
        
        Returns:
            dict: 감정 분석 결과 (sentiment, confidence, explanation)
        """
        prompt = f"""다음 텍스트의 감정을 분석하고 JSON 형식으로 답변해주세요:

텍스트: {text}

다음 형식으로 응답해주세요:
{{
    "sentiment": "긍정/부정/중립",
    "confidence": "높음/중간/낮음",
    "explanation": "감정 분석에 대한 간단한 설명"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 텍스트의 감정을 정확하게 분석하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"오류 발생: {str(e)}"
    
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 텍스트에서 핵심 키워드를 정확하게 추출하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"오류 발생: {str(e)}"
    
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 텍스트의 주제를 체계적으로 분석하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"오류 발생: {str(e)}"


def main():
    """메인 함수 - 사용 예제"""
    
    # TextAnalyzer 초기화
    analyzer = TextAnalyzer()
    
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
    
    print("=" * 60)
    print("OpenAI 텍스트 분석 서비스")
    print("=" * 60)
    
    # 1. 텍스트 요약
    print("\n[1] 텍스트 요약 (짧게)")
    print("-" * 60)
    summary_short = analyzer.summarize(sample_text, max_length="short")
    print(summary_short)
    
    print("\n[2] 텍스트 요약 (보통)")
    print("-" * 60)
    summary_medium = analyzer.summarize(sample_text, max_length="medium")
    print(summary_medium)
    
    # 2. 감정 분석
    print("\n[3] 감정 분석")
    print("-" * 60)
    sentiment = analyzer.analyze_sentiment(sample_text)
    print(sentiment)
    
    # 3. 키워드 추출
    print("\n[4] 키워드 추출")
    print("-" * 60)
    keywords = analyzer.extract_keywords(sample_text, num_keywords=5)
    print(keywords)
    
    # 4. 주제 분석
    print("\n[5] 주제 분석")
    print("-" * 60)
    topics = analyzer.analyze_topics(sample_text)
    print(topics)
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

