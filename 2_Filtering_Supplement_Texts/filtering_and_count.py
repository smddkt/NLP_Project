import pandas as pd
import csv

# Define file paths
submission_corpus_file_path = 
comment_corpus_file_path = 
supplement_file_path = 
output_file_path = 

# Set this variable to True to enable detailed logging, False to disable
enable_detailed_logging = False

def format_number(num):
    return f"{num:,}"

def find_supplements_in_corpus(corpus_df, supplements, text_field, corpus_type):
    supplement_counts = {supplement[0]: 0 for supplement in supplements}
    output_data = []

    def log_and_check(x, supplement_variants, supplement_name, cell_idx, total_cells):
        x_lower = str(x).lower()
        for variant in supplement_variants:
            if variant in x_lower:
                output_data.append([supplement_name, x, corpus_type])
                supplement_counts[supplement_name] += 1
                if enable_detailed_logging:
                    print(f"Found '{variant}' in '{x_lower}'")
                return True
        if not enable_detailed_logging and cell_idx % 5000 == 0:
            print(f"Checked {format_number(cell_idx)} out of {format_number(total_cells)} cells")
        return False

    total_cells = len(corpus_df[text_field])
    for cell_idx, cell in enumerate(corpus_df[text_field]):
        for supplement in supplements:
            supplement_variants = [name.lower() for name in supplement if pd.notna(name)]
            log_and_check(cell, supplement_variants, supplement[0], cell_idx, total_cells)
    
    return supplement_counts, output_data

def main(submission_corpus_file_path, comment_corpus_file_path, supplement_file_path, output_file_path):
    try:
        # Read the submission and comment corpus CSV files
        submission_corpus_df = pd.read_csv(submission_corpus_file_path, quotechar='"', quoting=csv.QUOTE_ALL)
        comment_corpus_df = pd.read_csv(comment_corpus_file_path, quotechar='"', quoting=csv.QUOTE_ALL)
        
        # Determine the text field name in each corpus
        submission_text_field = 'processed_text' if 'processed_text' in submission_corpus_df.columns else 'processed_comment'
        comment_text_field = 'processed_text' if 'processed_text' in comment_corpus_df.columns else 'processed_comment'
        
        # Read the supplement list CSV file
        supplement_df = pd.read_csv(supplement_file_path, header=None, quotechar='"', quoting=csv.QUOTE_ALL)
        supplements = supplement_df.values.tolist()
        
        # Find supplements in both corpora
        submission_counts, submission_output_data = find_supplements_in_corpus(submission_corpus_df, supplements, submission_text_field, 'Submission')
        comment_counts, comment_output_data = find_supplements_in_corpus(comment_corpus_df, supplements, comment_text_field, 'Comment')
        
        # Combine the output data
        combined_output_data = submission_output_data + comment_output_data
        
        # Prepare the final output data
        output_data = []
        for supplement in supplements:
            supplement_name = supplement[0]
            submission_count = submission_counts.get(supplement_name, 0)
            comment_count = comment_counts.get(supplement_name, 0)
            total_count = submission_count + comment_count
            output_data.append([supplement_name, submission_count, comment_count, total_count])
        
        # Convert the counts to a DataFrame
        counts_df = pd.DataFrame(output_data, columns=['Supplement', 'Submission_Count', 'Comment_Count', 'Total_Count'])
        
        # Convert the combined output data to a DataFrame
        text_df = pd.DataFrame(combined_output_data, columns=['Supplement', 'Text', 'Corpus_Type'])
        
        # Merge the counts and text DataFrames
        result_df = pd.merge(counts_df, text_df, on='Supplement', how='outer')
        
        # Sort the result_df based on the order of supplements in the supplement list
        supplement_order = [supplement[0] for supplement in supplements]
        result_df['Supplement'] = pd.Categorical(result_df['Supplement'], categories=supplement_order, ordered=True)
        result_df = result_df.sort_values('Supplement')
        
        # Save the final DataFrame to CSV
        result_df.to_csv(output_file_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
        
        print(f"Output file saved successfully at {output_file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the main function with the defined file paths
main(submission_corpus_file_path, comment_corpus_file_path, supplement_file_path, output_file_path)
