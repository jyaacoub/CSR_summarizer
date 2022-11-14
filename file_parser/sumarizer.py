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

from file_reader.pdf_reader import pdf_reader
from file_parser.chunker import Chunker
from models.open_ai import OpenAPI_summarizer, OpenAPI_search
from models.token_counter import TokenCounter
from common.SECRETS import API_KEY

import pandas as pd
from tqdm import tqdm

class FileSummarizer:
    def __init__(self, pdf_path, api_key=API_KEY,
                        chunk_size=300, top_n=20):
        """
        Main class for summarizing a pdf file

        Args:
            pdf_path (str): the path to the pdf file
            top_n (int, optional): The top number of chunks to consider after search for summary. Defaults to 10.
        """
        self.pdf_content = pdf_reader(pdf_path) # looks like: {section: {"content":text, "pages": (int,int)}, ...}
        
        # getting rid of unwanted sections
        unwanted_sections = ['table of contents', 'appendix']
        for section in list(self.pdf_content.keys()):
            if section.lower() in unwanted_sections:
                del self.pdf_content[section]
        
        self.tokenizer = TokenCounter(exact_token_count=True)
        self.chunker = Chunker(token_counter=self.tokenizer, 
                               max_tokens=chunk_size)
        self.srch_mdl = OpenAPI_search(api_key=api_key,
                                       token_counter=self.tokenizer)
        self.sum_mdl = OpenAPI_summarizer(api_key=api_key,
                                          token_counter=self.tokenizer)
        self.top_n = top_n
    
    def chunk(self):
        # chunking each section
        self.pdf_chunked = pd.DataFrame(columns=['text', 'section', 'chunk_no'])
        for section in tqdm(self.pdf_content, desc="Chunking sections..."):
            chunks = self.chunker.chunk_sentence(self.pdf_content[section]['content'])
            # convert to dataframe
            df_section = pd.DataFrame({'text':chunks, 'section':section,
                                       'chunk_no':range(len(chunks))})
            
            # adding to main dataframe
            self.pdf_chunked = pd.concat([self.pdf_chunked, df_section])

        self.pdf_chunked.reset_index(drop=True, inplace=True)
        
    def chunk_and_search(self, query:str, capture_all_sections=False):
        if not hasattr(self, 'pdf_chunked'):
            self.chunk()
        
        # Using semantic search to rate the most relevant chunks according to the query
        if query:
            self.pdf_chunked_scores = self.srch_mdl.get_scores(self.pdf_chunked, query)
            self.pdf_chunked_scores.sort_values(by='scores', ascending=False)
        else:
            print("No query provided, all chunks will be equally considered")
            self.pdf_chunked_scores['scores'] = 1 # if no query, then all chunks are equally relevant
            
        # getting the top_n chunks
        if capture_all_sections:
            # capture all sections by looping through the chunks of each section until we reach n chunks
            # Sort of like in-order traversal of a tree where the branches are the different sections
            sections = list(self.pdf_content.keys())
            top_n_chunks = pd.DataFrame(columns=['text', 'section', 'chunk_no', 'scores'])
            for n in range(self.top_n):
                s_idx = n % len(sections)
                curr_section_name = sections[s_idx]
                
                # getting the ith chunk of the current section (i = n // len(sections))
                i = n // len(sections)
                
                curr_section = self.pdf_chunked_scores[self.pdf_chunked_scores['section'] 
                                                       == curr_section_name]
                
                # Check if we have reached the end of the section
                if i >= len(curr_section):
                    continue
                    
                # get the ith chunk of the current section
                ith_chunk = curr_section.iloc[i].to_frame().T
                # adding it to the top_n_chunks DF
                top_n_chunks = pd.concat([top_n_chunks, ith_chunk])
        else:
            # just get the top_n chunks
            top_n_chunks = self.pdf_chunked_scores.sort_values(
                                            by='scores', ascending=False).head(self.top_n)
            
        return top_n_chunks
    
    def summarize_file(self, query=None, capture_all_sections=False, inital_max_tokens=57):
        """
        Summarizes the loaded file using OpenAPI
        """
        self.query = query
        self.top_n_chunks = self.chunk_and_search(query, capture_all_sections)
            
        # Summarizing the top_n chunks
        self.sum_0 = pd.DataFrame(columns=['summary', 'section', 'chunk_no'])

        for _, row in tqdm(self.top_n_chunks.iterrows(), 
                            total=self.top_n_chunks.shape[0], 
                            desc="Summarizing chunks"):
            sum = self.sum_mdl.summarize_text(row['text'], 
                                    max_resp_tokens=inital_max_tokens, 
                                    summary_prompt=1, # tl;dr prompt is the best
                                    bullet_points=False)
            
            # adding to the dataframe
            self.sum_0 = self.sum_0.append({'summary': sum,
                                    'section': row.section,
                                    'chunk_no': row.chunk_no}, 
                                    ignore_index=True)
        
        # Summarizing the sections
        self.sum_1 = pd.DataFrame(columns=['summary', 'section'])
        for section in tqdm(self.sum_0.section.unique(), desc="Summarizing sections"):
            # combining all the summaries of the section
            section_text = self.sum_0[self.sum_0.section == 
                                      section].summary.str.cat(sep='\n')
            
            sum = self.sum_mdl.summarize_text(section_text, 
                                            max_resp_tokens=inital_max_tokens*2, # doubling max tokens
                                            summary_prompt=1, # tl;dr prompt is the best
                                            bullet_points=False)
            
            # adding to the dataframe
            self.sum_1 = self.sum_1.append({'summary': sum,
                                'section': section}, 
                                ignore_index=True)
                
        # Summarizing the whole file
        print("Getting final summary...")
        self.sum_final = self.sum_mdl.summarize_text(self.sum_1.summary.str.cat(sep='\n'),
                                                max_resp_tokens=inital_max_tokens*4, 
                                                summary_prompt=1, # tl;dr prompt is the best
                                                bullet_points=False)
        print("Done! Final summary:\n\n", self.sum_final)
        
        return self.sum_final

    def save_summaries(self, save_path):
        """
        Saves the chunked texts and the summaries to a excel file
        """
        self.top_n_chunks.to_excel(save_path + 'top_n_chunks.xlsx', index=False)
        self.sum_0.to_excel(save_path + 'sum_0.xlsx', index=False)
        self.sum_1.to_excel(save_path + 'sum_1.xlsx', index=False)
        
        # saving the final summary as a text file with query
        with open(save_path + 'sum_final.txt', 'w') as f:
            f.write("Query: " + self.query + '\n\n')
            f.write("Summary: \n")
            f.write(self.sum_final)
            
