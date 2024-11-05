import llm
import llm_gemini
import os
from pathlib import Path


def process_coc_file(file_path):
    model = llm.get_model("gemini-1.5-flash-002")

    system_prompt = """Your capabilities lie in handling scanned documents and processing the data and information within them. Process the text and provide them as reports as per the instructions provided to you."""
    assistant_prompt = """
    You are provided a scanned copy of a public, government document on Certificates of Candidacy for a party list in the Philippines.
    Your task is to gather the details listed in the document.

    The first page contains information about the party list. This generally has the complete name of the party list. List this as the primary heading.
    Succeeding pages should include details of each candidate or representative in the party list. Information should include, but not limited to the following:
    - Nominee No.
    - Full Name
    - Date of Birth
    - Place of Birth
    - Name of Party / Sectoral / Coalition
    - Age
    - Sex
    - Civil Status
    - Citizenship Status
    - Profession / Occupation
    - Residence
    - Period of Residence in the Philippines
    - Voter Declaration (Address)

    NOTE: "Name of Party / Sectoral / Coalition" can be skipped if it's the same as the party list name. Include it only if it's different.

    The desired output should be in Markdown, with candidate names as subheadings and their details within them, listed in the succeeding pages that is dedicated per candidate. The first heading can be dedicated to the party list itself and its information, usually presented on the first page.

    Skip and ignore redacted or unclear information.

    Normalize all names with proper capitalization, except for acronyms like NCR.
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

    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_dir, filename)
            print(f"Processing: {filename}")

            result = process_coc_file(file_path)

            output_file = output_dir / f"{filename[:-4]}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)

            if result.startswith("Error"):
                error_files.append(filename)
                print(f"Error encountered: {filename}")
            else:
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
    data_directory = "data-resume/"
    process_all_cocs(data_directory)
