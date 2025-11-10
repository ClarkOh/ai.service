"""
사용 가능한 Gemini 모델 확인 스크립트
"""
import google.generativeai as genai
from pathlib import Path

# API 키 로드
key_file = Path("gemini.api.key.txt")
if key_file.exists():
    with open(key_file, 'r', encoding='utf-8') as f:
        api_key = f.read().strip()
    print("[OK] API key loaded\n")
else:
    print("[ERROR] gemini.api.key.txt file not found")
    exit(1)

# API 설정
genai.configure(api_key=api_key)

print("=" * 60)
print("Available Gemini Models:")
print("=" * 60)

try:
    models = genai.list_models()
    
    generate_models = []
    for model in models:
        # generateContent를 지원하는 모델만 필터링
        if 'generateContent' in model.supported_generation_methods:
            generate_models.append(model)
            print(f"\nModel: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Methods: {', '.join(model.supported_generation_methods)}")
    
    print("\n" + "=" * 60)
    print(f"Total: {len(generate_models)} models support generateContent")
    print("=" * 60)
    
    if generate_models:
        print("\nRecommended models:")
        for model in generate_models[:3]:  # 처음 3개만 표시
            print(f"  - {model.name}")

except Exception as e:
    print(f"[ERROR] {e}")

