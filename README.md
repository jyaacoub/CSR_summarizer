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
