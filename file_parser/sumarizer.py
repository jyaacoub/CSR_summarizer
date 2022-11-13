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
from file_parser.chunker import Chunker
from models.open_ai import OpenAPI_summarizer, OpenAPI_search

import pandas as pd

class FileSummarizer:
    def __init__(self, pdf_path, top_n=10):
        """
        Main class for summarizing a pdf file

        Args:
            pdf_path (str): the path to the pdf file
            top_n (int, optional): The top number of chunks to consider after search for summary. Defaults to 10.
        """
        self.pdf_content = pdf_reader(pdf_path) # looks like: {section: {"content":text, "pages": (int,int)}, ...}
        
        self.chunker = Chunker(min(OpenAPI_search.MAX_TOKENS, 
                                   OpenAPI_summarizer.MAX_TOKENS))
        self.srch_mdl = OpenAPI_search()
        self.sum_mdl = OpenAPI_summarizer(tokenizer=self.srch_mdl.load_tokenizer())
        self.top_n = top_n
        
        
    def chunk_and_search(self, query:str, capture_all_sections=False):
        
        # chunking each section
        self.pdf_content_chunked = pd.DataFrame(columns=['text', 'section', 'chunk_no'])
        
        for section in self.pdf_content:
            chunks = self.chunker.chunk(self.pdf_content[section]['content'])
            # convert to dataframe
            df_section = pd.DataFrame({'text':chunks, 'section':section,'chunk_no':range(len(chunks))})
            
            # adding to main dataframe
            self.pdf_content_chunked = pd.concat([self.pdf_content_chunked, df_section])

        # Using semantic search to rate the most relevant chunks according to the query
        if query:
            self.pdf_content_chunked = self.srch_mdl.get_scores(self.pdf_content_chunked, query)
            self.pdf_content_chunked.sort_values(by='scores', ascending=False)
        else:
            self.pdf_content_chunked['score'] = 1 # if no query, then all chunks are equally relevant
            
        # getting the top_n chunks
        if capture_all_sections:
            # capture all sections by looping through the chunks of each section until we reach n chunks
            # Sort of like in-order traversal of a tree where the branches are the different sections
            sections = list(self.pdf_content.keys())
            top_n_chunks = []
            for n in range(self.top_n):
                s_idx = n % len(sections)
                curr_section = sections[s_idx]
                
                # getting the ith chunk of the current section (i = n // len(sections))
                i = n // len(sections)
                
                # Check if we have reached the end of the section
                if i >= len(self.pdf_content_chunked[self.pdf_content_chunked['section'] == curr_section]):
                    continue
                    
                # get the ith chunk of the current section
                top_n_chunks.append(self.pdf_content_chunked[self.pdf_content_chunked['section'] == curr_section].iloc[i])
        else:
            # just get the top_n chunks
            top_n_chunks = self.pdf_content_chunked.sort_values(by='score', ascending=False).head(self.top_n)
    
    def summarize_file(self, query=None, capture_all_sections=False):
        """
        Summarizes the loaded file using OpenAPI
        """
        top_n_chunks = self.chunk_and_search(query, capture_all_sections)
            
        # TODO: Summarizing the top_n chunks
        
        # TODO: Summarizing the sections
        
        # TODO: Summarizing the whole file
        
        return ''

