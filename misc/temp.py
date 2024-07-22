import json
import uuid

def convert_to_jsonl(input_json):
    jsonl_output = []
    
    for item in input_json:
        # Add new fields
        item['id'] = str(uuid.uuid4())
        item['author'] = 'jason'
        
        # Convert to JSONL format
        jsonl_output.append(json.dumps(item))
    
    return '\n'.join(jsonl_output)

# Read the input JSON
with open('blog_jason_content.json', 'r') as f:
    input_data = json.load(f)

# Convert to JSONL
jsonl_data = convert_to_jsonl(input_data)

# Write the output JSONL
with open('output_jason.jsonl', 'w') as f:
    f.write(jsonl_data)

print("Conversion complete. Output written to output.jsonl")