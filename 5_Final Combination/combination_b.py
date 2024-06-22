import pandas as pd
import csv
import re

# Define file paths
combination_a_file_path =
sentiment_file_path = 
output_file_path = 

def remove_parentheses(text):
    return re.sub(r'\s*\([^)]*\)', '', text)

def round_to_nearest_half(num):
    return round(num * 2) / 2

def main(combination_a_file_path, sentiment_file_path, output_file_path):
    try:
        # Read the combination_a CSV file
        combination_a_df = pd.read_csv(combination_a_file_path, quotechar='"', quoting=csv.QUOTE_ALL)
        # Read the sentiment CSV file
        sentiment_df = pd.read_csv(sentiment_file_path, quotechar='"', quoting=csv.QUOTE_ALL)
        sentiment_df.columns = [col.lower() for col in sentiment_df.columns]
        sentiment_df['supplement'] = sentiment_df['supplement'].str.lower()
        
        # Initialize the sentiment difference lists
        first_sentiment_difference = []
        second_sentiment_difference = []
        third_sentiment_difference = []
        sentiment_rounded = []
        
        # Iterate through each row in combination_a_df
        for index, row in combination_a_df.iterrows():
            supplement = row['Supplement']
            first_related = remove_parentheses(row['First_Related_Supplement']) if pd.notna(row['First_Related_Supplement']) else ""
            second_related = remove_parentheses(row['Second_Related_Supplement']) if pd.notna(row['Second_Related_Supplement']) else ""
            third_related = remove_parentheses(row['Third_Related_Supplement']) if pd.notna(row['Third_Related_Supplement']) else ""
            
            supplement_lower = supplement.lower()
            first_related_lower = first_related.lower()
            second_related_lower = second_related.lower()
            third_related_lower = third_related.lower()
            
            first_sentiment_row = sentiment_df[(sentiment_df['supplement'] == supplement_lower) & (sentiment_df['mentioned_supplements'] == first_related_lower)]
            second_sentiment_row = sentiment_df[(sentiment_df['supplement'] == supplement_lower) & (sentiment_df['mentioned_supplements'] == second_related_lower)]
            third_sentiment_row = sentiment_df[(sentiment_df['supplement'] == supplement_lower) & (sentiment_df['mentioned_supplements'] == third_related_lower)]
            
            first_difference = first_sentiment_row['difference'].values[0] if not first_sentiment_row.empty else None
            second_difference = second_sentiment_row['difference'].values[0] if not second_sentiment_row.empty else None
            third_difference = third_sentiment_row['difference'].values[0] if not third_sentiment_row.empty else None
            
            first_sentiment_difference.append(first_difference)
            second_sentiment_difference.append(second_difference)
            third_sentiment_difference.append(third_difference)
            
            # Add single sentiment value rounded to the nearest half
            single_sentiment_row = sentiment_df[sentiment_df['supplement'] == supplement_lower]
            if not single_sentiment_row.empty:
                single_sentiment_value = single_sentiment_row['average_individual_sentiment'].values[0]
                sentiment_rounded.append(round_to_nearest_half(single_sentiment_value))
            else:
                sentiment_rounded.append(None)
        
        # Add the new sentiment difference columns to the combination_a_df
        combination_a_df['First_Sentiment_Difference'] = first_sentiment_difference
        combination_a_df['Second_Sentiment_Difference'] = second_sentiment_difference
        combination_a_df['Third_Sentiment_Difference'] = third_sentiment_difference
        combination_a_df['Sentiment_Rounded'] = sentiment_rounded
        
        # Reorder the columns to place sentiment differences next to their related supplements
        cols = list(combination_a_df.columns)
        new_order = ['Supplement', 'Submission_Count', 'Comment_Count', 'Total_Count', 'Sentiment_Rounded',
                     'First_Related_Supplement', 'First_Sentiment_Difference',
                     'Second_Related_Supplement', 'Second_Sentiment_Difference',
                     'Third_Related_Supplement', 'Third_Sentiment_Difference',
                     'First_Neg_Keyword', 'Second_Neg_Keyword', 'Third_Neg_Keyword',
                     'First_Pos_Keyword', 'Second_Pos_Keyword', 'Third_Pos_Keyword']
        for col in cols:
            if col not in new_order:
                new_order.append(col)
        
        combination_a_df = combination_a_df[new_order]
        
        # Save the final DataFrame to CSV
        combination_a_df.to_csv(output_file_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
        
        print(f"Output file saved successfully at {output_file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the main function with the defined file paths
main(combination_a_file_path, sentiment_file_path, output_file_path)
