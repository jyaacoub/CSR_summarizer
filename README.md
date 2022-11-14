# CSR_summarizer
We utilize the text completion functionality of the OpenAI API to simplify lengthy CSR reports and extract relevant information.

For this we use the API to create text embeddings for semantic search, and then query the API to get summaries for the most relevant text snippets. The final result is a trace of summaries to a final overall summary. This allows users to quickly gather a high level overview of the report and, if they need to, also follow the trace back to the original text to get the details.

# Video Overview

https://user-images.githubusercontent.com/50300488/201576204-c6d69cfe-1b59-45f9-ab60-f51c52c14629.mp4


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
