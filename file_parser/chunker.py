"""
Used for smartly splitting up sections that are sent by the *file_reader*.
  - Here is where we might want to create further subsections from the sections given by `PDFReader` 
"""
from common.constants import CHAR_PER_TOKEN

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
    def __init__(self, max_tokens=2024):
        self.max_tokens = max_tokens # max number of tokens in a chunk
        self.chunked_list = []


        """
        Cuts off a chunk at every '.' and stores it in chunked_list as well as returns the list
        """
    def chunk_sentence(self, text:str):
        # first check to see if we even need to chunk (is the text longer than max_tokens?)
        if len(text) / CHAR_PER_TOKEN <= self.max_tokens:
            return [text]
        self.chunked_list = text.split('.')
        print("chunked text:")
        print(self.chunked_list)
        return self.chunked_list

        pass
    