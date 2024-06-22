import pandas as pd
import csv

# Define file paths
supplement_list_file_path = 
categorized_corpus_file_path = 
other_supplements_file_path = 
keywords_file_path = 
sentiment_file_path = 
output_file_path = 

def extract_supplements(supplement_list_file_path):
    supplement_list_df = pd.read_csv(supplement_list_file_path, header=None, quotechar='"', quoting=csv.QUOTE_ALL)
    supplements = supplement_list_df[0].tolist()
    supplements_lower = [supplement.lower() for supplement in supplements]
    return supplements, supplements_lower

def split_keywords(keywords):
    if pd.isna(keywords):
        return "", "", ""
    parts = [part.strip() for part in keywords.split(",")]
    return (parts[0] if len(parts) > 0 else "",
            parts[1] if len(parts) > 1 else "",
            parts[2] if len(parts) > 2 else "")

def extract_related_supplements(other_supplements_df, supplements_lower):
    other_supplements_data = []
    for supplement_lower in supplements_lower:
        row = other_supplements_df[other_supplements_df['supplement'] == supplement_lower]
        if not row.empty:
            other_supplements = row['other_supplements'].values[0]
            other_supplements_data.append(other_supplements)
        else:
            other_supplements_data.append(None)
    return other_supplements_data

def split_and_assign_keywords(output_df, col_name, prefix):
    first_keyword = []
    second_keyword = []
    third_keyword = []
    
    for keywords in output_df[col_name]:
        first, second, third = split_keywords(keywords)
        first_keyword.append(first)
        second_keyword.append(second)
        third_keyword.append(third)
    
    output_df[f'First_{prefix}'] = first_keyword
    output_df[f'Second_{prefix}'] = second_keyword
    output_df[f'Third_{prefix}'] = third_keyword
    
    return output_df.drop(columns=[col_name])

def main(supplement_list_file_path, categorized_corpus_file_path, other_supplements_file_path, keywords_file_path, sentiment_file_path, output_file_path):
    try:
        supplements, supplements_lower = extract_supplements(supplement_list_file_path)
        
        output_df = pd.DataFrame({'Supplement': supplements})
        
        categorized_corpus_df = pd.read_csv(categorized_corpus_file_path, quotechar='"', quoting=csv.QUOTE_ALL)
        categorized_corpus_df.columns = [col.lower() for col in categorized_corpus_df.columns]
        categorized_corpus_df['supplement'] = categorized_corpus_df['supplement'].str.lower()
        
        supplement_col = 'supplement'
        submission_count_col = 'submission_count'
        comment_count_col = 'comment_count'
        total_count_col = 'total_count'
        
        submission_count_data = []
        comment_count_data = []
        total_count_data = []
        for supplement_lower in supplements_lower:
            row = categorized_corpus_df[categorized_corpus_df[supplement_col] == supplement_lower]
            if not row.empty:
                submission_count = row[submission_count_col].values[0]
                comment_count = row[comment_count_col].values[0]
                total_count = row[total_count_col].values[0]
                submission_count_data.append(submission_count)
                comment_count_data.append(comment_count)
                total_count_data.append(total_count)
            else:
                submission_count_data.append(None)
                comment_count_data.append(None)
                total_count_data.append(None)

        output_df['Submission_Count'] = submission_count_data
        output_df['Comment_Count'] = comment_count_data
        output_df['Total_Count'] = total_count_data
        
        other_supplements_df = pd.read_csv(other_supplements_file_path, quotechar='"', quoting=csv.QUOTE_ALL)
        other_supplements_df.columns = [col.lower() for col in other_supplements_df.columns]
        other_supplements_df['supplement'] = other_supplements_df['supplement'].str.lower()

        output_df['Other_Supplements'] = extract_related_supplements(other_supplements_df, supplements_lower)

        output_df = split_and_assign_keywords(output_df, 'Other_Supplements', 'Related_Supplement')
        
        keywords_df = pd.read_csv(keywords_file_path, quotechar='"', quoting=csv.QUOTE_ALL)
        keywords_df.columns = [col.lower() for col in keywords_df.columns]
        keywords_df['supplement'] = keywords_df['supplement'].str.lower()

        side_effects_data = []
        benefits_data = []
        for supplement_lower in supplements_lower:
            row = keywords_df[keywords_df['supplement'] == supplement_lower]
            if not row.empty:
                side_effects = row['side_effects'].values[0]
                benefits = row['benefits'].values[0]
                side_effects_data.append(side_effects)
                benefits_data.append(benefits)
            else:
                side_effects_data.append(None)
                benefits_data.append(None)

        output_df['Side_Effects'] = side_effects_data
        output_df['Benefits'] = benefits_data
        
        output_df = split_and_assign_keywords(output_df, 'Side_Effects', 'Neg_Keyword')
        output_df = split_and_assign_keywords(output_df, 'Benefits', 'Pos_Keyword')

        sentiment_df = pd.read_csv(sentiment_file_path, quotechar='"', quoting=csv.QUOTE_ALL)
        sentiment_df.columns = [col.lower() for col in sentiment_df.columns]

        # Initialize the sentiment lists
        first_sentiment = []
        second_sentiment = []
        third_sentiment = []

        # Check if the columns exist before iterating
        if 'first_related_supplement' in output_df.columns and 'second_related_supplement' in output_df.columns and 'third_related_supplement' in output_df.columns:
            for index, row in output_df.iterrows():
                supplement = row['Supplement'].lower()
                first_related = row['First_Related_Supplement'].lower() if row['First_Related_Supplement'] else ""
                second_related = row['Second_Related_Supplement'].lower() if row['Second_Related_Supplement'] else ""
                third_related = row['Third_Related_Supplement'].lower() if row['Third_Related_Supplement'] else ""

                first_sentiment_row = sentiment_df[(sentiment_df['supplement'] == supplement) & (sentiment_df['mentioned_supplements'] == first_related)]
                second_sentiment_row = sentiment_df[(sentiment_df['supplement'] == supplement) & (sentiment_df['mentioned_supplements'] == second_related)]
                third_sentiment_row = sentiment_df[(sentiment_df['supplement'] == supplement) & (sentiment_df['mentioned_supplements'] == third_related)]

                first_sentiment.append(first_sentiment_row['difference'].values[0] if not first_sentiment_row.empty else None)
                second_sentiment.append(second_sentiment_row['difference'].values[0] if not second_sentiment_row.empty else None)
                third_sentiment.append(third_sentiment_row['difference'].values[0] if not third_sentiment_row.empty else None)

            output_df['First_Sentiment_Difference'] = first_sentiment
            output_df['Second_Sentiment_Difference'] = second_sentiment
            output_df['Third_Sentiment_Difference'] = third_sentiment

        output_df.to_csv(output_file_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
        
        print(f"Output file saved successfully at {output_file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

main(supplement_list_file_path, categorized_corpus_file_path, other_supplements_file_path, keywords_file_path, sentiment_file_path, output_file_path)
