import pandas as pd

# 절대 경로 설정
input_path_single = 'C:/Users/82109/Desktop/test/NLP_Project/전처리 스크립트, csv파일/df_single_sentiment.csv'
input_path_combination = 'C:/Users/82109/Desktop/test/NLP_Project/전처리 스크립트, csv파일/df_combination_sentiment.csv'
output_path_single = 'C:/Users/82109/Desktop/test/NLP_Project/전처리 스크립트, csv파일/supplement_sentiment_summary.csv'
output_path_combination = 'C:/Users/82109/Desktop/test/NLP_Project/전처리 스크립트, csv파일/combo_sentiment_summary.csv'
comparison_output_path = 'C:/Users/82109/Desktop/test/NLP_Project/전처리 스크립트, csv파일/comparison_sentiment_summary.csv'

# 데이터 불러오기 함수
def load_data(path):
    try:
        df = pd.read_csv(path, low_memory=False, encoding='utf-8')
        print(f"Successfully loaded data from {path}")
    except UnicodeDecodeError:
        df = pd.read_csv(path, low_memory=False, encoding='latin1')
        print(f"Loaded data from {path} with 'latin1' encoding")
    except FileNotFoundError:
        print(f"File not found: {path}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
    return df

df_single = load_data(input_path_single)
df_combination = load_data(input_path_combination)

# 별점 정보를 숫자로 변환하는 함수
def convert_sentiment_to_numeric(sentiment):
    if isinstance(sentiment, str):
        sentiment = sentiment.lower()
        if '1 star' in sentiment:
            return 1
        elif '2 stars' in sentiment:
            return 2
        elif '3 stars' in sentiment:
            return 3
        elif '4 stars' in sentiment:
            return 4
        elif '5 stars' in sentiment:
            return 5
    return None

# Sentiment 열을 숫자로 변환
df_single['Sentiment'] = df_single['Sentiment'].apply(convert_sentiment_to_numeric)
df_combination['Sentiment'] = df_combination['Sentiment'].apply(convert_sentiment_to_numeric)

# 결측값 제거
df_single.dropna(subset=['Sentiment'], inplace=True)
df_combination.dropna(subset=['Sentiment'], inplace=True)

# 단독 보조제별 감성 분석 결과 요약
single_summary = df_single.groupby('Supplement').agg(
    avg_sentiment=pd.NamedAgg(column='Sentiment', aggfunc='mean')
).reset_index()
print("Single Summary:")
print(single_summary.head())

# 보조제별 요약 결과 저장
single_summary.to_csv(output_path_single, index=False)
print(f"Supplement sentiment summary saved to '{output_path_single}'")

# 보조제 조합별 감성 분석 결과 요약
# supplement와 mentioned_supplements를 개별 행으로 분할
combination_expanded = []
for _, row in df_combination.iterrows():
    supplement = row['Supplement']
    mentioned_supplements = row['Mentioned_Supplements'].split(', ')
    sentiment = row['Sentiment']
    for mentioned in mentioned_supplements:
        combination_expanded.append({
            'Supplement': supplement,
            'Mentioned_Supplements': mentioned,
            'Sentiment': sentiment
        })

combination_expanded_df = pd.DataFrame(combination_expanded)

# 같은 보조제 조합이 여러 행에 등장할 경우 평균을 계산하여 통합
combination_summary = combination_expanded_df.groupby(['Supplement', 'Mentioned_Supplements']).agg(
    avg_sentiment=pd.NamedAgg(column='Sentiment', aggfunc='mean')
).reset_index()
print("Combination Summary:")
print(combination_summary.head())

# 보조제 조합별 결과 저장
combination_summary.to_csv(output_path_combination, index=False)
print(f"Combination sentiment summary saved to '{output_path_combination}'")

# 보조제별 평균 감성 점수와 보조제 조합별 평균 감성 점수를 비교
comparison_results = []

for _, combo_row in combination_summary.iterrows():
    supplement = combo_row['Supplement']
    mentioned_supplements = combo_row['Mentioned_Supplements']
    avg_combination_sentiment = combo_row['avg_sentiment']

    individual_sentiment = single_summary.loc[single_summary['Supplement'] == supplement, 'avg_sentiment'].values
    if len(individual_sentiment) > 0:
        avg_individual_sentiment = individual_sentiment[0]
        difference = avg_combination_sentiment - avg_individual_sentiment
        comparison_results.append({
            "Supplement": supplement,
            "Mentioned_Supplements": mentioned_supplements,
            "Average_Individual_Sentiment": avg_individual_sentiment,
            "Average_Combination_Sentiment": avg_combination_sentiment,
            "Difference": difference
        })

comparison_df = pd.DataFrame(comparison_results)
print("Comparison Results DataFrame:")
print(comparison_df.head())

comparison_df.to_csv(comparison_output_path, index=False)
print(f"Comparison sentiment summary saved to '{comparison_output_path}'")