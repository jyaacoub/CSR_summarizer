"""
uses `OpenAPI` to summarize pdfs
  - Here is where we might want to create futher subsections from the sections given by `PDFReader` (see `chunker.py`)
  - Keeps track of the summary trace (sort of like this: https://openaipublic.blob.core.windows.net/recursive-book-summ/website/index.html)

Considerations for generating a file summary:

OpenAPI_summarizer.summarize_text():
    We can vary the max tokens to be returned (tuned as to not miss out important technical details but also not be too long of a summary)
        - vary depending on the length of the text?
        - set to specific number?
        - vary based on information density of text? - https://towardsdatascience.com/linguistic-complexity-measures-for-text-nlp-e4bf664bd660
"""

from file_reader import pdf_reader

class FileSummarizer:
    def __init__(self, pdf_path):
        self.pdf_contents = pdf_reader(pdf_path) # dictionary of sections and their contents
        
        
    def summarize_file(self, text):
        """
        Summarizes a file using OpenAPI
        """
        pass

