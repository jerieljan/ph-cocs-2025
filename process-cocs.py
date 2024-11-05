import llm
import llm_gemini

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

## Example

```
# Pilipino Party (PP)

## Atty. Juan dela Cruz

- Full Name: Juan dela Cruz
- Date of Birth: January 1, 1960
[...]
"""

response = model.prompt(
    system=system_prompt,
    prompt=assistant_prompt,
    attachments=[llm.Attachment(path="data/2. PPP.pdf")])

print(response)
