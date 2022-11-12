# CSR_summarizer
A tool to extract meaningful information from long CSR reports.


# file structure
- *common*: folder for all common variables such as api keys
  - `SECRETS.py`: file containing secrete keys (DO NOT COMMIT THIS; added to gitignore)
- *file_parser*: folder for all parsing needs
  - `chunker.py`: used for smartly splitting up sections that are sent by the *file_reader*.
  - `sumarizer.py`: see description below
- *file_reader*: For all reading/formating needs.
  - `pdf_reader.py`: see below
- *models*: For all the models that we use in the project
  - `open_ai.py` contains wrapper class for openAPI.


# Tasks
- `PDFReader` class: to read in PDF and get sections
  - Get sections from outline metadata
    - Look for keywords (e.g.: climate, environment, etc...)
  - If no sections -> scan first few pages for them
    - No need to do this for the hackathon we will just hardcode this for now
- `OpenAPI` class: a wrapper class for interatacting with the Open AI models
  - Specific to our needs of sumarization we will need GPT-3 access
  - Might need to use a fine-tuned model that emphasizes numbers?
- `Summarizer` class: uses `OpenAPI` to summarize pdfs
  - Here is where we might want to create futher subsections from the sections given by `PDFReader`
  - Keeps track of the summary trace (sort of like this: https://openaipublic.blob.core.windows.net/recursive-book-summ/website/index.html)
- `run.py` script: main script for taking in PDFs.
