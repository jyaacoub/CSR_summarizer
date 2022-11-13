from common.constants import CHAR_PER_TOKEN
import math

class TokenCounter:    
    def __init__(self, tokenizer=None, exact_token_count=True):
        """
        Counts the number of tokens in a text defined by OpenAI's GPT2 tokenizer 
        or a heuristic of 4.45 tokens per character
            
        Args:
            tokenizer (_type_, optional): _description_. Defaults to None.
            `exact_token_count` (bool, optional): if True, will uses a expensive gpt2 tokenizer to get exact token count for text. 
                Uses a heuristic of 4.45 tokens per character if False. Defaults to False.
        """
        self.tokenizer = tokenizer
        self.exact_token_count = exact_token_count
        
    def _load_tokenizer(self, tokenizer=None):
        if tokenizer is None:
            from transformers import GPT2Tokenizer
            self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        else:
            self.tokenizer = tokenizer
        return self.tokenizer
    
    def __call__(self, text, exact=None): # non-static method so that we dont load the tokenizer multiple times
        """
            Returns the number of tokens in text
            using heuristic of 4.45 tokens per character is a decent approximation
        """
        if exact or self.exact_token_count:
            if self.tokenizer is None: # lazy load tokenizer because it takes a while
                self._load_tokenizer()
            res = self.tokenizer(text)
            return len(res["input_ids"]) # we dont care about the embedding just the number of tokens
        else:
            return math.ceil(len(text)/CHAR_PER_TOKEN) # one token is roughly 4 characters