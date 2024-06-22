import pandas as pd
from transformers import pipeline, BertTokenizer, BertForSequenceClassification
import torch
from tqdm import tqdm

# 절대 경로 설정
input_path_single = 
input_path_combination = 
output_path_single = 
output_path_combination = 
comparison_output_path = 

# 데이터 불러오기 함수
def load_data(path):
    try:
        df = pd.read_csv(path, low_memory=False, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(path, low_memory=False, encoding='latin1')
    except FileNotFoundError:
        print(f"File not found: {path}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
    return df

df_single = load_data(input_path_single)
df_combination = load_data(input_path_combination)

# 같은 보조제 이름을 가진 텍스트 중 max_samples개만 랜덤으로 선택
def sample_supplements(df, supplement_col='Supplement', max_samples=1000):
    grouped = df.groupby(supplement_col)
    sampled_df = grouped.apply(lambda x: x.sample(n=min(len(x), max_samples), random_state=42))
    sampled_df.reset_index(drop=True, inplace=True)
    return sampled_df

df_single_sampled = sample_supplements(df_single)

# 감성 분석 파이프라인 초기화
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# 최대 시퀀스 길이 설정
max_length = 512

def preprocess_text(text):
    encoded_input = tokenizer(text, truncation=True, padding='max_length', max_length=max_length, return_tensors="pt")
    return encoded_input

# 감성 분석 수행 함수
def perform_sentiment_analysis(df, df_name):
    texts = df['Text'].tolist()
    results = []
    cache = {}
    for idx, text in tqdm(enumerate(texts), total=len(texts), desc=f"Processing {df_name}"):
        if text in cache:
            sentiment, score = cache[text]
            print("skipped already analized text")
        else:
            inputs = preprocess_text(text)
            with torch.no_grad():
                outputs = model(**inputs)
            scores = outputs[0][0].softmax(dim=0)
            label = torch.argmax(scores).item()
            sentiment = model.config.id2label[label]
            score = scores[label].item()
            cache[text] = (sentiment, score)
        results.append({"label": sentiment, "score": score})
        if (idx + 1) % 100 == 0:  # 100개 단위로 진행 상황 출력
            print(f"\n{df_name} ({idx + 1} / {len(texts)})")
    df['Sentiment'] = [result['label'] for result in results]
    df['Score'] = [result['score'] for result in results]
    return df

df_single = perform_sentiment_analysis(df_single_sampled, "df_single")
df_combination = perform_sentiment_analysis(df_combination, "df_combination")

# 감성 분석 결과를 저장하여 확인
df_single.to_csv(output_path_single, index=False)
df_combination.to_csv(output_path_combination, index=False)
