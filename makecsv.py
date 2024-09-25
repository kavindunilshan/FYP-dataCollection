# Load the CSV file
input_file = './csv/input/Brazil Cities.csv'  # Replace with your actual file path
output_file = 'csv/output/converted_csv_file.csv'

# Open the input file and convert semicolons to commas
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        # Replace semicolons with commas
        outfile.write(line.replace(';', ','))

print(f"File has been converted and saved as {output_file}")
