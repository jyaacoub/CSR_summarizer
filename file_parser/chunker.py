"""
Used for smartly splitting up sections that are sent by the *file_reader*.
  - Here is where we might want to create further subsections from the sections given by `PDFReader` 
"""
from common.constants import CHAR_PER_TOKEN
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
    def __init__(self, max_tokens=2024, token_counter:TokenCounter=None):
        self.max_tokens = max_tokens # max number of tokens in a chunk
        self.token_counter = token_counter if token_counter is not None else TokenCounter()

    
    def chunk_sentence(self, text:str, exact=False):
        """
        cuttoff at last sentence before max_tokens

        Args:
            text (str): text to chunk
            exact (bool, optional): using gpt2 to get exact token counts. Defaults to False.

        Returns:
            list: list of chunks
        """
        
        # first check to see if we even need to chunk (is the text longer than max_tokens?)
        tkn_count = self.token_counter(text, exact=exact)
        
        if tkn_count < self.max_tokens:
            return [text]
        else: # chunk then pass remaining to be chunked again
            max_idx = self.max_tokens*CHAR_PER_TOKEN # use heuristic to get max index 
            # NOTE: the true max_idx could change depending on the text
            # to determine this algorithmically we would need to try smaller and smaller chunks 
            # until we get a chunk that is less than max_tokens (can be expensive)
            new_tkn_count = self.token_counter(text[:max_idx], exact=True)
            assert new_tkn_count <= self.max_tokens, \
                f"Chunker: Max index  is too large ({max_idx}: \
                    {new_tkn_count} > {self.max_tokens}). Heuristic method failed."
            
            # finding the last period in the first chunk < max_tokens
            period_idx = text.rfind('.', 0, )
            if period_idx == -1: # if no period found, then just cut off at max_tokens
                period_idx = max_idx
            return [text[:period_idx]] + self.chunk(text[period_idx:])