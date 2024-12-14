import json

# Function to read, process, and save a JSONL file




import random
import re


def extract_information(text):
    # Regex patterns
    number_pattern = r'\b\d+\b'         # Match standalone numbers
    percentage_pattern = r'\d+%'        # Match numbers with a % sign
    price_pattern = r'\$\d+'            # Match numbers with a $ sign
    
    # Extract data
    percentages = re.findall(percentage_pattern, text)
    prices = re.findall(price_pattern, text)
    numbers = re.findall(number_pattern, text)
    
    # Clean extracted data
    percentages = [int(p[:-1]) for p in percentages]  # Remove '%' and convert to int
    prices = [int(p[1:]) for p in prices]            # Remove '$' and convert to int
    
    # Remove numbers that are part of prices or percentages
    numbers = [int(n) for n in numbers if int(n) not in prices and f"{n}%" not in percentages]
    
    return numbers, prices, percentages


def is_prime(num):
    """Check if a number is a prime number."""
    if num <= 1:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def next_prime(n):
    """Find the next prime number after n."""
    prime = n + 1
    while not is_prime(prime):
        prime += 1
    return prime
def price_decimal(p):
    p = float(p)
    p = p + round(random.uniform(0, 1), 2)
    return p

def convert_lists(numbers , prices , percentages):
    numbers2 , prices2 , percentages2 = numbers , prices , percentages
    
    
    for i in range(len(numbers2)):
        numbers2[i] = next_prime(numbers2[i])
    for i in range(len(percentages2)):
        percentages2[i] = next_prime(percentages2[i])
        
    for i in range(len(prices2)):
        prices2[i] = price_decimal(prices2[i])
        
        
    return numbers2 , prices2 , percentages2
    
def replace_values_in_text(text, numbers, prices, percentages, numbers2, prices2, percentages2):
    """Replace values in the original text with their transformed counterparts."""
    # Replace percentages
    for old, new in zip(percentages, percentages2):
        text = text.replace(f"{old}%", f"{new}%")
    
    # Replace prices
    
    placeholders_dollar = [f"__DOLLAR_PLACEHOLDER_{i}__" for i in range(len(prices))]
    for old, placeholder in zip(prices, placeholders_dollar):
        text = text.replace(f"${old}", placeholder)

    # Step 2: Replace standalone numbers with placeholders
    placeholders_number = [f"__NUMBER_PLACEHOLDER_{i}__" for i in range(len(prices))]
    for old, placeholder in zip(prices, placeholders_number):
        pattern = rf"\b{old}\b"  # Match standalone numbers
        text = re.sub(pattern, placeholder, text)

    # Step 3: Replace placeholders with new values
    for placeholder, new in zip(placeholders_dollar, prices2):
        text = text.replace(placeholder, f"${new}")

    for placeholder, new in zip(placeholders_number, prices2):
        text = text.replace(placeholder, str(new))
    # Replace numbers
    for old, new in zip(numbers, numbers2):
        # Ensure we only replace standalone numbers, not parts of other strings
        text = re.sub(rf'\b{old}\b', str(new), text)
    
    return text
def update_answers(text):

    # Define the regular expression patterns
    expression_pattern = r"<<(.*?)="  # Match everything between '<<' and '='
    result_pattern = r"<<.*?=(.*?)>>"      # Match everything between '=' and '>>'

    # Extract expressions and old results
    expressions = re.findall(expression_pattern, text)
    old_results = re.findall(result_pattern, text)
    new_expressions = expressions
    # Display the results
    print("Expressions:", expressions)
    print("Old Results:", old_results)
    
    new_results = []

    for i in range(len(new_expressions)):
        result = eval(new_expressions[i])
        
        new_results.append(result)
        old_number = old_results[i]
        for j in range(i+1 , len(new_expressions)):
            updated_expression = re.sub(rf'\b{old_number}\b', str(new_results[i]), new_expressions[j])
            new_expressions[j] = updated_expression
            
    new_results = list(map(lambda x: str(x), new_results))
    new_results = [str(round(float(result), 2)) for result in new_results]
    
    
    for i in range(len(old_results)):
        old = old_results[i]
        new = new_results[i]
        expression = expressions[i]
        new_expression = new_expressions[i]

        # Replace old result with new result
        text = re.sub(rf'\b{old}\b', str(new), text)

        # Replace old expression with new expression (with the new result)
        text = re.sub(rf'{expression} = {old}', f'{new_expression} = {new}', text)
    
    return text
def prime_decimal_replace(row):
    data = row
    question = data['question']
    answer = data['answer']
    numbers, prices, percentages = extract_information(question)
    print("old questions : " , question)
    print("old answer : " , answer)

    print("Numbers:", numbers)
    print("Prices:", prices)
    print("Percentages:", percentages)

    n1 = list(numbers) 
    pr1 = list(prices) 
    per1 = list(percentages)
    numbers2 , prices2 , percentages2 = convert_lists(n1 , pr1 , per1)

    print("numbers" , numbers ,"prices", prices ,"percentages", percentages)
    print("new numbers" , numbers2 ,"new prices", prices2  ,"new percentages", percentages2)

    new_question = replace_values_in_text(question, numbers, prices, percentages, numbers2, prices2, percentages2)
    new_answer = replace_values_in_text(answer, numbers, prices, percentages, numbers2, prices2, percentages2)

    print("new question : ",new_question)
    print("new answer : ",new_answer)

    updated_new_answer = update_answers(new_answer)
    print(" updated_new_answer : ",updated_new_answer)

    data['question'] = new_question
    data['answer'] = updated_new_answer
    return data

def process_jsonl(input_file, output_file, processing_function):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
           try:
                # Parse the JSONL line into a Python dictionary
                row = json.loads(line.strip())
                
                # Apply the processing function to the row
                processed_row = processing_function(row)
                
                # Write the processed row back to the output file as JSONL
                outfile.write(json.dumps(processed_row) + '\n')
           except Exception as e:
                # Log the error and skip this row
                print(f"Error processing line {line}: {e}")
                continue

# Example processing function


# File paths
input_file = 'grade_school_math\data\example_model_solutions.jsonl'
output_file = 'example_model_solutions_output.jsonl'

# Process the JSONL file
process_jsonl(input_file, output_file, prime_decimal_replace)
