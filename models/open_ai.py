"""
Considerations for model chosen and setup:

    "For applications requiring a lot of understanding of the content, like summarization for 
    a specific audience and creative content generation, Davinci is going to produce the best results." - OpenAI docs

    "For text-davinci-002 the max length of the prompt you can send is 4,000 tokens" - slack channel

    Some ideas to get around 4,000 token limit: - slack channel
        1. Split up the text to < 4K chunks and then pass each one into your summarization prompt.      - https://github.com/shyamal-anadkat/eco-faqs/blob/main/faq_gen.py#L54
        2. Embed the documents & use semantic search to retrieve relevant parts of the corpus to 
            a search query; and then pass each of those into your summarization prompt.

    "The embedding is an information dense representation of the semantic meaning of a piece of 
    text. Each embedding is a vector of floating point numbers, such that the distance between 
    two embeddings in the vector space is correlated with semantic similarity between two inputs 
    in the original format."                                                                            - OpenAI docs

    "Semantic Search uses an models to provide scores for different blocks of text for how closely 
    they relate to a query."                                                                            - OpenAI docs
"""

import math
from common.SECRETS import API_KEY

import openai


class OpenAPI:
    SUMMARY_MODEL = "text-davinci-002" # model to use for summarization
    MAX_TOKENS_DAVIN2 = 4000 # max tokens for davinci-002 is 4,000 - https://beta.openai.com/docs/models/gpt-3
                             # this includes the prompt
    TOKENS_PER_CHAR = 4.45 # one token is roughly 4 characters
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        openai.api_key = api_key
        self.tokenizer = None
    
    def get_token_count(self, text, exact=True): # non-static method so that we dont load the tokenizer multiple times
        """
            Returns the number of tokens in text
            using heuristic of 4.45 tokens per character is a decent approximation
        """
        if exact:
            if self.tokenizer is None: # lazy load tokenizer because it takes a while
                from transformers import GPT2Tokenizer
                self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            res = self.tokenizer(text)
            return len(res["input_ids"])
        else:
            return math.ceil(len(text)/self.TOKENS_PER_CHAR) # one token is roughly 4 characters
    
    def summarize_text(self, text, max_resp_tokens=256, summary_prompt=0, bullet_points=False,
                        temperature=0.7,   
                        top_p=1,           
                        frequency_penalty=0.07, # should stay low to avoid just coming up with unrelated words
                        presence_penalty=0.2): # increases the number of topics covered in the summary
        """ 
        Simple function that takes string input and returns a summary of the text via OpenAI's API 
        
        A few ways we can prompt the model to write a summary:
            0 - "Summarize the following text: \n\n<text>"
            1 - "<text> \ntd;dr:" - https://medium.com/geekculture/a-paper-summarizer-with-python-and-gpt-3-2c718bc3bc88
            2 - "<text> \nSummary:"
            3 - "<text> \nSummary of the above text:"
            
        We can also specify if we want it as a bulleted list:
            
        We can also vary the max tokens to be returned (this needs to be tuned as to not miss out important technical details)
            - vary depending on the length of the text?
            - set to specific number?
            - vary based on information density of text? - https://towardsdatascience.com/linguistic-complexity-measures-for-text-nlp-e4bf664bd660
        
        """
        assert summary_prompt in [0, 1, 2, 3], "Invalid summary prompt"
        if summary_prompt == 0:
            prompt = "Summarize the following text: \n\n" + text + "\n"
        elif summary_prompt == 1:
            prompt = text + "\ntl;dr:\n" # most consitent results (no bullet points when told to)
        elif summary_prompt == 2:
            prompt = text + "\nSummary:\n" # this prompt sucks and tends to just make up stuff
        elif summary_prompt == 3:
            prompt = text + "\nSummary of the above text:\n" # second best but sometimes forces bullet points
            
        if bullet_points:
            prompt += "\n-"
        
        # ensuring prompt + max_resp_tokens does not exceed max tokens for davinci-002
        num_tokens_prompt = self.get_token_count(prompt)
        total_tokens = num_tokens_prompt + max_resp_tokens
        assert total_tokens < self.MAX_TOKENS_DAVIN2, f"Prompt + max_resp_tokens exceeds max tokens for davinci-002 \
                                                        (prompt: {num_tokens_prompt}, max_resp_tokens: {max_resp_tokens})"
        
        # Checks text size, returns error if larger than max tokens
        response = openai.Completion.create(
            model=self.SUMMARY_MODEL,
            prompt=prompt,
            max_tokens=total_tokens,    # max tokens to return
            temperature=0.7,            # temperature represents how random the result is (1.0 is deterministic)
            top_p=1,                    # top_p represents how much to sample from the top of the distribution (controls diversity, 0.5 excludes 50% of the distribution)
            frequency_penalty=0.07,     # frequency_penalty represents how much to penalize new tokens based on their existing frequency (decreases likelihood of repeating words)
            presence_penalty=0.2        # presence_penalty same as ^ but based on whether they appear in the text so far (increase likelihood of new topics)
            )
        return '-' + response.choices[0].text if bullet_points else response.choices[0].text
    
    def summarize_text_corpus(self, text_corpus,max_resp_tokens=256, summary_prompt=0, bullet_points=False,
                        temperature=0.7,   
                        top_p=1,           
                        frequency_penalty=0.07, # should stay low to avoid just coming up with unrelated words
                        presence_penalty=0.2):
        """
        Gets text summaries for multiple documents in a single query for efficiency
        """
        pass    
    
    def _chunk_text(self, text, chunk_size=MAX_TOKENS_DAVIN2):
        """Splits text into chunks of size chunk_size"""
        pass
    
    def semantic_search(self, query, documents):
        """Compares a query to a corpus of documents and returns the most relevant documents"""
        
        # get semantic scores for query
        
        # loop through documents and get semantic scores
        
        # compare query scores to document scores
        pass
    
    def get_semantics(self, document):
        """Returns the semantic score(s) of document(s) using OpenAI's API"""
        pass
    