import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# CSV 파일 로드
try:
    df = pd.read_csv('Submissions_Edit.csv')
    print("CSV 파일이 성공적으로 로드되었습니다.")
except FileNotFoundError:
    print("CSV 파일을 찾을 수 없습니다. 파일 경로를 확인하세요.")
    exit()

# NLTK 리소스 다운로드
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# 불용어 리스트 및 원형 복원기 초기화
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# 24개의 보조제 목록과 불릴 수 있는 다른 이름을 딕셔너리 형태로 저장
supplements = {
    "melatonin": ["melatonin"],
    "5-htp": ["5-htp", "5 hydroxytryptophan", "5 hydroxy tryptophan"],
    "valerian root": ["valerian root", "valerian"],
    "lemon balm": ["lemon balm", "lemonbalm"],
    "lavender": ["lavender"],
    "passion flower": ["passion flower", "passionflower"],
    "chamomile": ["chamomile"],
    "ashwagandha": ["ashwagandha"],
    "kava": ["kava"],
    "hops": ["hops", "hop"],
    "skullcap": ["skullcap"],
    "california poppy": ["california poppy", "california", "poppy"],
    "magnolia bark": ["magnolia bark", "magnolia"],
    "mulungu": ["mulungu"],
    "cbd oil": ["cbd oil", "cbd"],
    "black seed oil": ["black seed oil", "blackseed"],
    "magnesium": ["magnesium"],
    "calcium": ["calcium"],
    "zinc": ["zinc"],
    "potassium": ["potassium"],
    "glycine": ["glycine"],
    "l-tryptophan": ["tryptophan"], #토큰화할 때 l과 tryptophan이 분리되므로 tryptophan으로만 검색함.
    "theanine": ["theanine"],
    "amanita": ["amanita"],
    "vitamin d": ["vitamin d", "vitamind"]
}

def preprocess(text_content):
    # 공백과 개행 문자 정리
    text_content = re.sub(r'\s+', ' ', text_content)  # 모든 공백(개행 포함)을 공백 한 칸으로 치환
    text_content = text_content.strip()  # 문자열 양 끝의 공백 제거
    
    # URL 제거
    text_content = re.sub(r'https?://\S+|www\.\S+', '', text_content)
    
    # HTML 태그 제거
    text_content = re.sub(r'<.*?>', '', text_content)
    
    # 이메일 주소 제거
    text_content = re.sub(r'\S+@\S+', '', text_content)
    
    # 소문자 변환
    text_content = text_content.lower()
    
    # 숫자 및 단위 보존
    text_content = re.sub(r'(\d+(?:\.\d+)?\s*(?:mg|ml|pills?|capsules?|tablets?|oz|mcg))', r' \1 ', text_content)
    
    # 토큰화
    words = word_tokenize(text_content)
    
    # 불용어 및 비문자 제거 (숫자 및 단위는 보존)
    words = [word for word in words if (word.isalpha() or re.match(r'\d+(?:\.\d+)?|mg|ml|pills?|capsules?|tablets?|oz|mcg', word)) and word not in stop_words]
    
    # 원형 복원 (숫자 및 단위는 그대로 유지)
    words = [lemmatizer.lemmatize(word) if word.isalpha() else word for word in words]
    
    return ' '.join(words)



# 용량 및 관련 약물/보조제 추출 함수
def extract_dosage_and_supplement(text_content):
    pattern = re.compile(r'(\d+(?:\.\d+)?\s*(mg|ml|pills?|capsules?|tablets?|oz|mcg))')
    matches = pattern.findall(text_content)
    
    supplements_found = set()
    for supplement, aliases in supplements.items():
        for alias in aliases:
            if alias in text_content:
                supplements_found.add(supplement)
    
    # 용량과 관련된 약물/보조제를 함께 반환
    dosage_info = []
    for match in matches:
        dosage_info.append((match[0], match[1], ', '.join(supplements_found) if supplements_found else "unknown"))

    return dosage_info

# 데이터프레임의 텍스트 컬럼 전처리 및 용량 추출
if 'text' in df.columns:  
    df['processed_text'] = df['text'].apply(preprocess) 
    df['dosages'] = df['processed_text'].apply(extract_dosage_and_supplement)
    print("전처리 및 용량 추출이 완료되었습니다.")
    
    # 전처리된 데이터 및 용량 정보를 새로운 CSV 파일로 저장
    df.to_csv('processed_insomnia_submissions_with_dosages.csv', index=False)
    print("전처리된 데이터와 용량 정보가 'processed_insomnia_submissions_with_dosages.csv' 파일로 저장되었습니다.")
else:
    print("컬럼 'text'가 데이터프레임에 없습니다. CSV 파일의 컬럼 이름을 확인하세요.")