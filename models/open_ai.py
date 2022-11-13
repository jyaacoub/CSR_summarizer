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

from common.SECRETS import API_KEY
from common.constants import CHAR_PER_TOKEN
from models.token_counter import TokenCounter

import openai
from openai.embeddings_utils import get_embedding, cosine_similarity

import math, time
import pandas as pd
from tqdm import tqdm

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

class OpenAPI:
    def __init__(self, api_key:str=API_KEY, token_counter:TokenCounter=None):
        self.api_key = api_key
        openai.api_key = api_key
        self.token_counter = token_counter if token_counter is not None else TokenCounter() # allows for sharing of same tokenizer
        
    def get_token_count(self, text, exact=None):
        return self.token_counter(text, exact)

class OpenAPI_search(OpenAPI):
    EMBEDDING_DOC_MODEL = "text-search-curie-doc-001" # using curie for efficiency (davinci is more accurate but way slower)
    EMBEDDING_QRY_MODEL = "text-search-curie-query-001"
    
    MAX_TOKENS = 2048 # max tokens for embedding model
    def __init__(self, api_key:str=API_KEY, token_counter:TokenCounter=None):
        super().__init__(api_key, token_counter)
    
    
    def get_scores(self, snippets:(pd.DataFrame or list), query:str):
        """
        returns the similarity scores for each snippet with the query.

        Args:
            snippets (pd.DataFrame): snippets to search through as a dataframe with column "text"
            query (str): the query text used to match the most relevant text
        """
        # making sure token count is within the max token limit
        tkn_count = self.get_token_count(query)
        assert tkn_count <= self.MAX_TOKENS, \
            f"Query token count ({tkn_count}) exceeds max token limit ({self.MAX_TOKENS})"
            
        pbar = tqdm(total=len(snippets), desc=f"Getting embeddings; Will take under ~{len(snippets)}s...")
        # Getting the embeddings
        @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
        def completion_with_backoff(text):
            res = get_embedding(text, engine=self.EMBEDDING_DOC_MODEL)
            tqdm.update(pbar, 1)
            return res
                
        snippets['emb'] = snippets.text.apply(completion_with_backoff)
        pbar.close()
        q_emb = get_embedding(query, engine=self.EMBEDDING_QRY_MODEL)
        
        # Determining similarity between query and each text snippet by embedding vector
        snippets['scores'] = snippets.emb.apply(lambda x: cosine_similarity(x, q_emb))
        
        # dropping the embeddings
        snippets.drop(columns=['emb'], inplace=True)
        
        return snippets
    
    def semantic_search(self, snippets:(pd.DataFrame or list), query:str, top_n): # example: https://github.com/openai/openai-cookbook/blob/main/examples/Semantic_text_search_using_embeddings.ipynb
        """Gets the most relevant text from a document based on a query

        Args:
            snippets (pd.Series or list): Text snippets to search through
            query (str): the query text used to match the most relevant text
            
        Returns:
            pd.DataFrame: dataframe sorted by relevance score with columns: text, embedding, similarity
        """
        snippets = pd.DataFrame(snippets, columns=["text"]) if not isinstance(snippets, pd.DataFrame) else snippets
        
        snippets = self.get_scores(snippets, query)
        
        # Sorting by similarity and returning result
        return snippets.sort_values(by='scores', ascending=False).head(top_n)

class OpenAPI_summarizer(OpenAPI):
    SUMMARY_MODEL = "text-davinci-002" # model to use for summarization
    MAX_TOKENS = 4000 # max tokens for SUMMARY MODEL (davinci-002) - https://beta.openai.com/docs/models/gpt-3
    # NOTE: Max tokens includes the prompt
    
    def __init__(self, api_key:str=API_KEY, token_counter:TokenCounter=None):
        super().__init__(api_key, token_counter)
    
    def summarize_text(self, text, max_resp_tokens=256, 
                        summary_prompt=0, bullet_points=False,
                        temp=0.7,   
                        top_p=1,           
                        freq_penalty=0.07, # should stay low to avoid just coming up with unrelated words
                        pres_penalty=0.2): # increases the number of topics covered in the summary
        """        
        Simple function that takes string input and returns a summary of the text via OpenAI's API 
        
        A few ways we can prompt the model to write a summary (`summary_prompt`):
            0 - "Summarize the following text: \\n\\n<text>"
            1 - "<text> \\ntl;dr:"
            2 - "<text> \\nSummary:"
            3 - "<text> \\nSummary of the above text:"
            
        Args:
            `text` (str): text to summarize
            `max_resp_tokens` (int, optional): max number of tokens for the summary. Defaults to 256.
            `bullet_points` (bool, optional): If True, will foce the summary to be in the form of bullet points. Defaults to False.
            
            `temp` (float, optional): temperature represents how random the result is (1.0 is deterministic). Defaults to 0.7.
            `top_p` (float, optional): top_p represents how much to sample from the top of the distribution (controls diversity, 
                0.5 excludes 50% of the distribution). Defaults to 1.
            `freq_penalty` (float, optional): frequency_penalty represents how much to penalize new tokens based on their existing 
                frequency (decreases likelihood of repeating words). Defaults to 0.07.
            `pres_penalty` (float, optional): presence_penalty similar to frequency but based on whether they appear in the text so far 
                (increases likelihood of new topics). Defaults to 0.2.
                
        returns:
            str: summary of text
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
        assert total_tokens < self.MAX_TOKENS, f"Prompt + max_resp_tokens exceeds max tokens for davinci-002 \
                                                        (prompt: {num_tokens_prompt}, max_resp_tokens: {max_resp_tokens})"
        
        # Checks text size, returns error if larger than max tokens
        response = openai.Completion.create(
            model=self.SUMMARY_MODEL,
            prompt=prompt,
            max_tokens=total_tokens,        # max tokens to return
            temperature=temp,               # temperature represents how random the result is (1.0 is deterministic)
            top_p=top_p,                    # top_p represents how much to sample from the top of the distribution (controls diversity, 0.5 excludes 50% of the distribution)
            frequency_penalty=freq_penalty, # frequency_penalty represents how much to penalize new tokens based on their existing frequency (decreases likelihood of repeating words)
            presence_penalty=pres_penalty   # presence_penalty same as ^ but based on whether they appear in the text so far (increase likelihood of new topics)
            )
        return '-' + response.choices[0].text if bullet_points else response.choices[0].text
    
    def summarize_texts(self, texts, max_resp_tokens=256, summary_prompt=0, bullet_points=False,
                        temperature=0.7,   
                        top_p=1,           
                        frequency_penalty=0.07, # should stay low to avoid just coming up with unrelated words
                        presence_penalty=0.2):
        """
        Gets text summaries for multiple documents in a single query for efficiency
        #TODO: implement this (https://github.com/shyamal-anadkat/eco-faqs/blob/main/faq_gen.py#L54)
        """
        pass
    