"""
Used for smartly splitting up sections that are sent by the *file_reader*.
  - Here is where we might want to create further subsections from the sections given by `PDFReader` 
"""
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import Embedding, LSTM, Concatenate, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

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

    #Cuts off a chunk at every '.' and return the chunked list
    def chunk_sentence(self, text:str):
        # first check to see if we even need to chunk (is the text longer than max_tokens?)
        if len(text) / CHAR_PER_TOKEN <= self.max_tokens:
            return [text]
        chunked_list = text.split('.')
        print("chunked text:")
        print(chunked_list)
        return chunked_list

        pass
    
    #Cuts off a chunk at every ".\n", which detects the end of a paragraph and returns the chunked list
    #If a paragraph is too large to not be parsed, 
    def chunk_paragraph(self, text:str):
         # first check to see if we even need to chunk (is the text longer than max_tokens?)
        if len(text) / CHAR_PER_TOKEN <= self.max_tokens:
            return [text]

        pass