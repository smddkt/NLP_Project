import pandas as pd
import csv

# Define file paths
categorized_corpus_file_path = 
supplement_list_file_path = 
output_file_path = 

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
        
        # Create a list for the output data
        output_data = []
        for _, row in categorized_corpus_df.iterrows():
            current_supplement = row['Supplement'].lower()
            text = row[text_field]
            mentioned_supplements = find_other_supplements(text, current_supplement)
            if mentioned_supplements:  # Only include rows with at least one mentioned supplement
                mentioned_supplements_str = ", ".join(set(mentioned_supplements))
                output_data.append([row['Supplement'], text, mentioned_supplements_str])
        
        # Convert the output data to a DataFrame
        result_df = pd.DataFrame(output_data, columns=['Supplement', 'Text', 'Mentioned_Supplements'])
        
        # Save the final DataFrame to CSV
        result_df.to_csv(output_file_path, index=False, quotechar='"', quoting=csv.QUOTE_ALL)
        
        print(f"Output file saved successfully at {output_file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the main function with the defined file paths
main(categorized_corpus_file_path, supplement_list_file_path, output_file_path)
