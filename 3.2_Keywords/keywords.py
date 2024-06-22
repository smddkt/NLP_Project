import pandas as pd
import csv
from collections import Counter
from nltk.corpus import wordnet as wn
import nltk

# WordNet 데이터 다운로드
nltk.download('wordnet')
nltk.download('omw-1.4')

# 파일 경로 정의
categorized_corpus_file_path =
supplement_list_file_path = 
keyword_list_file_path = 
output_file_path = 

# 동의어를 찾는 함수
def get_synonyms(word):
    synonyms = set()
    # 주어진 단어의 동의어를 WordNet에서 찾아서 수집
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            # 동의어를 모아서 set에 추가
            synonyms.add(lemma.name().replace('_', ' '))
    return synonyms

# 텍스트에서 키워드를 찾는 함수
def find_keywords(text, keywords):
    text_lower = text.lower()
    found_keywords = []
    for keyword in keywords:
        # 키워드의 동의어들을 수집
        keyword_synonyms = get_synonyms(keyword)
        keyword_synonyms.add(keyword.lower())
        for synonym in keyword_synonyms:
            # 텍스트에서 동의어가 포함되어 있는지 확인
            if synonym in text_lower:
                found_keywords.append(keyword)
                break
    return found_keywords

def main(categorized_corpus_file_path, supplement_list_file_path, keyword_list_file_path, output_file_path):
    try:
        # 분류된 코퍼스 CSV 파일 읽기
        categorized_corpus_df = pd.read_csv(categorized_corpus_file_path, quotechar='"', quoting=csv.QUOTE_ALL)

        # 키워드 목록 CSV 파일 읽기
        keyword_list_df = pd.read_csv(keyword_list_file_path, header=None, quotechar='"', quoting=csv.QUOTE_ALL)
        side_effects_keywords = keyword_list_df[0].dropna().tolist()
        benefits_keywords = keyword_list_df[1].dropna().tolist()
        
        # 키워드 목록 출력
        print("Side Effects Keywords:", side_effects_keywords)
        print("Benefits Keywords:", benefits_keywords)
        
        # 텍스트 필드 이름 찾기 (대소문자 구분 없음)
        text_field = None
        for col in categorized_corpus_df.columns:
            if col.lower() == 'text':
                text_field = col
                break
        
        if text_field is None:
            raise ValueError("No 'text' field found in the categorized corpus file")
        
        # 각 텍스트에서 부작용 및 효과 키워드 추출
        categorized_corpus_df['Side_Effects'] = categorized_corpus_df[text_field].apply(lambda x: find_keywords(x, side_effects_keywords))
        categorized_corpus_df['Benefits'] = categorized_corpus_df[text_field].apply(lambda x: find_keywords(x, benefits_keywords))
        
        # 부작용 및 효과 키워드의 빈도 계산을 위한 Counter 객체 생성
        side_effect_counts = Counter()
        benefit_counts = Counter()
        supplement_side_effect_counts = {}
        supplement_benefit_counts = {}
        
        for _, row in categorized_corpus_df.iterrows():
            supplement = row['Supplement']
            side_effects = row['Side_Effects']
            benefits = row['Benefits']
            
            if side_effects:
                side_effect_counts.update(side_effects)
                if supplement not in supplement_side_effect_counts:
                    supplement_side_effect_counts[supplement] = Counter()
                supplement_side_effect_counts[supplement].update(side_effects)
                
            if benefits:
                benefit_counts.update(benefits)
                if supplement not in supplement_benefit_counts:
                    supplement_benefit_counts[supplement] = Counter()
                supplement_benefit_counts[supplement].update(benefits)
        
        # 최종 출력 데이터를 준비
        output_data = []
        for supplement in supplement_side_effect_counts.keys() | supplement_benefit_counts.keys():
            side_effect_data = []
            if supplement in supplement_side_effect_counts:
                for keyword, count in supplement_side_effect_counts[supplement].items():
                    total_count = side_effect_counts[keyword]
                    side_effect_data.append((keyword, count, total_count))
            sorted_side_effects = sorted(side_effect_data, key=lambda x: x[1]/x[2], reverse=True)
            side_effect_str = ", ".join([f"{kw}({c}/{tc})" for kw, c, tc in sorted_side_effects])
            
            benefit_data = []
            if supplement in supplement_benefit_counts:
                for keyword, count in supplement_benefit_counts[supplement].items():
                    total_count = benefit_counts[keyword]
                    benefit_data.append((keyword, count, total_count))
            sorted_benefits = sorted(benefit_data, key=lambda x: x[1]/x[2], reverse=True)
            benefit_str = ", ".join([f"{kw}({c}/{tc})" for kw, c, tc in sorted_benefits])
            
            output_data.append([supplement, side_effect_str, benefit_str])
        
        # 출력 데이터를 데이터프레임으로 변환
        result_df = pd.DataFrame(output_data, columns=['Supplement', 'Side_Effects', 'Benefits'])
        
        # 최종 데이터프레임을 CSV 파일로 저장
        result_df.to_csv(output_file_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
        
        print(f"Output file saved successfully at {output_file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# 메인 함수 호출
main(categorized_corpus_file_path, supplement_list_file_path, keyword_list_file_path, output_file_path)
