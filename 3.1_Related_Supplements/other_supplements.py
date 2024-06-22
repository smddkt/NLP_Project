import pandas as pd
import csv
from collections import Counter

# Define file paths
categorized_corpus_file_path = r"E:\최민준\학교 관련\3학년 2학기 (2024-3월)\텍스트정보처리론\reddit\subreddits23\output_counts.csv"
supplement_list_file_path = r"E:\최민준\학교 관련\3학년 2학기 (2024-3월)\텍스트정보처리론\reddit\subreddits23\Supplements_List.csv"
output_file_path = r'E:\최민준\학교 관련\3학년 2학기 (2024-3월)\텍스트정보처리론\reddit\subreddits23\output_other_supplements.csv'

def main(categorized_corpus_file_path, supplement_list_file_path, output_file_path):
    try:
        # Read the categorized corpus CSV file
        categorized_corpus_df = pd.read_csv(categorized_corpus_file_path, quotechar='"', quoting=csv.QUOTE_ALL)
        
        # Read the supplement list CSV file
        supplement_list_df = pd.read_csv(supplement_list_file_path, header=None, quotechar='"', quoting=csv.QUOTE_ALL)
        
        # Find the 'text' field name (case-insensitive)
        text_field = None
        for col in categorized_corpus_df.columns:
            if col.lower() == 'text':
                text_field = col
                break
        
        if text_field is None:
            raise ValueError("No 'text' field found in the categorized corpus file")
        
        # Create a list of supplements and their variants
        supplement_variants = {}
        for row in supplement_list_df.itertuples(index=False):
            main_supplement = row[0].lower()
            variants = [str(item).lower() for item in row if pd.notna(item)]
            for variant in variants:
                supplement_variants[variant] = main_supplement
        
        # Function to find other mentioned supplements in a text
        def find_other_supplements(text, current_supplement):
            text_lower = text.lower()
            mentioned_supplements = []
            for variant, main_supplement in supplement_variants.items():
                if variant in text_lower and main_supplement != current_supplement:
                    mentioned_supplements.append(main_supplement)
            return mentioned_supplements
        
        # Create a dictionary to store counts of co-occurrences
        supplement_co_occurrences = {sup[0].lower(): Counter() for sup in supplement_list_df.itertuples(index=False)}
        
        # Populate the co-occurrence dictionary and count total occurrences
        supplement_total_counts = Counter(categorized_corpus_df['Supplement'].str.lower())
        for _, row in categorized_corpus_df.iterrows():
            current_supplement = row['Supplement'].lower()
            mentioned_supplements = find_other_supplements(row[text_field], current_supplement)
            supplement_co_occurrences[current_supplement].update(mentioned_supplements)
        
        # Create a list for the output data
        output_data = []
        for supplement, co_occurrence in supplement_co_occurrences.items():
            if co_occurrence:
                co_occurrence_strs = []
                for supp, count in co_occurrence.items():
                    supp_total_count = supplement_total_counts[supp]
                    co_occurrence_strs.append((supp.capitalize(), count, supp_total_count))
                sorted_co_occurrence_strs = sorted(co_occurrence_strs, key=lambda x: x[1] / x[2], reverse=True)
                co_occurrence_str = ", ".join([f"{supp}({count}/{total_count})" for supp, count, total_count in sorted_co_occurrence_strs if count > 0])
                output_data.append([supplement.capitalize(), co_occurrence_str])
        
        # Convert the output data to a DataFrame
        result_df = pd.DataFrame(output_data, columns=['Supplement', 'Other_Supplements'])
        
        # Save the final DataFrame to CSV
        result_df.to_csv(output_file_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
        
        print(f"Output file saved successfully at {output_file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the main function with the defined file paths
main(categorized_corpus_file_path, supplement_list_file_path, output_file_path)
