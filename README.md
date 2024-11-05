# PH COCS 2024

*A quick experiment to parse Certificates of Candidacy using LLMs*

## Usage

- Examine data at: https://comelec.gov.ph/?r=2025NLE/COC2025
  - I used `REDACTED CERTIFICATE OF NOMINATION AND CERTIFICATE OF ACCEPTANCE OF NOMINATION OF PARTY-LIST
GROUP`, for example.
- Extract the URLs, pass it onto `| grep href | sort | uniq | sed -n 's/.*<a href="\([^"]*\)".*/\1/p' > cocs-urls.txt`
- `wget --content-disposition -i cocs-urls.txt` to get all PDFs. Place them in `data/`
- Setup your Python `venv`
- Setup `llm`
  - `pipx install llm`
  - `llm install llm-gemini`
  - `llm keys set gemini` (provide your Gemini API key)
- Run `process-cocs.py`.

NOTE: Given several hundreds of COCs and their documents in PDF scans, expect around 3,000 – 5,000 input tokens per query.
This will cost you quite a bit of money unless you opt for affordable models like `gemini-1.5-flash-002`.