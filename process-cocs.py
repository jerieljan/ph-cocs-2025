import llm
import llm_gemini
import os
from pathlib import Path
import json
import jsonschema
from jsonschema import validate


def process_coc_file(file_path):
    model = llm.get_model("gemini-1.5-flash-002")

    reqs_json_spec = """
        {
          "party_name": "string",
          "nominees": [
            {
              "nominee_no": "string",
              "full_name": "string",
              "date_of_birth": "string or null",
              "place_of_birth": "string",
              "age": "integer",
              "sex": "string",
              "civil_status": "string",
              "spouses_name": "string or null",
              "citizenship_status": "string",
              "profession_occupation": "string",
              "residence": "string",
              "period_of_residence": "string",
              "voter_declaration_address": "string"
            },
            ...
          ]
        }
    """

    reqs_json_example = """
        {
          "party_name": "Example Party List",
          "nominees": [
            {
              "nominee_no": "01",
              "full_name": "Jane Doe",
              "date_of_birth": "January 1, 1980",
              "place_of_birth": "Some City",
              "age": 43,
              "sex": "Female",
              "civil_status": "Single",
              "spouses_name": null,
              "citizenship_status": "Natural-born Citizen",
              "profession_occupation": "Engineer",
              "residence": "Sample Address, City",
              "period_of_residence": "43 years",
              "voter_declaration_address": "Precinct No. 123A, Barangay 1, City"
            },
            {
              "nominee_no": "02",
              "full_name": "John Smith",
              "date_of_birth": "February 2, 1985",
              "place_of_birth": "Another City",
              "age": 38,
              "sex": "Male",
              "civil_status": "Married",
              "spouses_name": "Jane Smith",
              "citizenship_status": "Natural-born Citizen",
              "profession_occupation": "Teacher",
              "residence": "Another Sample Address, City",
              "period_of_residence": "38 years",
              "voter_declaration_address": "Precinct No. 456B, Barangay 2, City"
            }
          ]
        }
    """

    system_prompt = """Your capabilities lie in handling scanned documents and processing the data and information within them. Process the text and provide them as reports as per the instructions provided to you."""
    assistant_prompt = f"""
    You are provided a scanned copy of a public, government document on Certificates of Candidacy for a party list in the Philippines.
    Your task is to gather the details listed in the document and make it conform to the provided JSON specification.

    OUTPUT MUST BE IN JSON — DO NOT TREAT RESULT AS IF IT WERE MARKDOWN
    The first page contains information about the party list. This generally has the complete name of the party list.
    Succeeding pages should include details of each candidate or representative in the party list. 
    
    NOTES: 
    - "Name of Party / Sectoral / Coalition" can be skipped if it's the same as the party list name. Include it only if it's different.
    - Skip and ignore redacted or unclear information. Use an empty string if information is not provided or not applicable (e.g., Nominee is Single, so their spouse is "")
    - When data is considered "None", use "" instead.
    - Normalize all names with proper capitalization, except for acronyms like NCR.
    
    <|json_specification|>
    {reqs_json_spec}
    <|json_specification|>
    
    <|json_example|>
    {reqs_json_example}
    <|json_example|>
    
    """

    try:
        response = model.prompt(
            system=system_prompt,
            prompt=assistant_prompt,
            attachments=[llm.Attachment(path=file_path)])

        return response.text()
    except Exception as e:
        return f"Error processing {file_path}: {str(e)}"


def process_all_cocs(data_dir):
    processed_files = 0
    error_files = []
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_errors_dir = Path("output-errors")
    output_errors_dir.mkdir(exist_ok=True)

    # Define the JSON schema based on reqs_json_spec
    schema = {
        "type": "object",
        "properties": {
            "party_name": {"type": "string"},
            "nominees": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nominee_no": {"type": "string"},
                        "full_name": {"type": "string"},
                        "date_of_birth": {"type": ["string", "null"]},
                        "place_of_birth": {"type": "string"},
                        "age": {"type": "integer"},
                        "sex": {"type": "string"},
                        "civil_status": {"type": "string"},
                        "spouses_name": {"type": ["string", "null"]},
                        "citizenship_status": {"type": "string"},
                        "profession_occupation": {"type": "string"},
                        "residence": {"type": "string"},
                        "period_of_residence": {"type": "string"},
                        "voter_declaration_address": {"type": "string"}
                    },
                    "required": ["nominee_no", "full_name", "place_of_birth", "age", "sex", "civil_status", "citizenship_status", "profession_occupation", "residence", "period_of_residence", "voter_declaration_address"]
                }
            }
        },
        "required": ["party_name", "nominees"]
    }

    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_dir, filename)
            print(f"Processing: {filename}")

            result = process_coc_file(file_path)

            # Remove the first and last line (assuming they contain json``` and ```)
            result_lines = result.split('\n')
            if len(result_lines) > 2:
                result = '\n'.join(result_lines[1:-1])

            # Check: Validate JSON and schema
            try:
                result_json = json.loads(result)
                validate(instance=result_json, schema=schema)
                output_file = output_dir / f"{filename[:-4]}.json"
            except (json.JSONDecodeError, jsonschema.exceptions.ValidationError) as e:
                error_files.append(filename)
                print(f"Error: Invalid JSON or schema for {filename}: {str(e)}")
                output_file = output_errors_dir / f"{filename[:-4]}.json"
                result_json = {"error": str(e), "raw_output": result}

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result_json, f, indent=2, ensure_ascii=False)

            processed_files += 1
            print(f"Done: {filename}")

    print(f"\nProcessing complete.")
    print(f"Total files processed: {processed_files}")
    print(f"Total errors encountered: {len(error_files)}")
    if error_files:
        print("\nFiles with errors:")
        for error_file in error_files:
            print(f"- {error_file}")

if __name__ == "__main__":
    data_directory = "data/"
    process_all_cocs(data_directory)
