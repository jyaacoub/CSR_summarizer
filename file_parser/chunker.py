"""
Used for smartly splitting up sections that are sent by the *file_reader*.
  - Here is where we might want to create further subsections from the sections given by `PDFReader` 
"""
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Embedding, LSTM, Concatenate, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

from common.constants import CHAR_PER_TOKEN
from models.open_ai import OpenAPI_search, OpenAPI_summarizer
from models.token_counter import TokenCounter

"""
Chunks text into smaller sections that are less than max_tokens in length
Cutoff needs to be chosen to preserve semantic meaning of the text
    - Cutoff will be at the end of a sentence?
    - end of a paragraph?
I found this resource that might be helpful on how to determine this: https://towardsdatascience.com/nlp-splitting-text-into-sentences-7bbce222ef17
Args:
    text (str): Long string that needs to be chunked

Returns:
    list: list of strings that are the chunks of text
"""

class Chunker:
    def __init__(self, max_tokens=min(OpenAPI_search.MAX_TOKENS, OpenAPI_summarizer.MAX_TOKENS), 
                        token_counter:TokenCounter=None):
        self.max_tokens = max_tokens # max number of tokens in a chunk
        self.token_counter = token_counter if token_counter is not None else TokenCounter()

    
    def chunk_sentence(self, text:str):
        """
        cuttoff at last sentence before max_tokens

        Args:
            text (str): text to chunk

        Returns:
            list: list of chunks
        """
        
        # first check to see if we even need to chunk (is the text longer than max_tokens?)
        tkn_count = self.token_counter(text, exact=True)
        
        if tkn_count < self.max_tokens:
            return [text]
        else: # chunk then pass remaining to be chunked again
            max_idx = int(self.max_tokens*CHAR_PER_TOKEN) # use heuristic to get max index 
            
            # the true max_idx could change depending on the text so we need to check token count again
            tkn_count = self.token_counter(text[:max_idx], exact=True)
            tkns_remaining = tkn_count - self.max_tokens
            while tkns_remaining >= 0: # while we are still over the max_tokens
                # decrease using heuristic and tokens remaining
                max_idx -= CHAR_PER_TOKEN*tkns_remaining if tkns_remaining > 0 else CHAR_PER_TOKEN
                max_idx = int(max_idx)
                tkn_count = self.token_counter(text[:max_idx], exact=True)
                tkns_remaining = tkn_count - self.max_tokens
            
            assert tkn_count <= self.max_tokens, \
                f"Chunker: Max index  is too large ({max_idx}: \
                    {tkn_count} > {self.max_tokens}). Heuristic method failed."
            
            # finding the last period in the first chunk < max_tokens
            period_idx = text.rfind('.', 0, max_idx)
            assert period_idx < max_idx, 'Error: No period found in first chunk?'
            if period_idx == -1: # if no period found, then just cut off at max_tokens
                period_idx = max_idx
            period_idx += 1 # add 1 to include the period in the chunk
            return [text[:period_idx]] + self.chunk_sentence(text[period_idx:])