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

from common.SECRETS import OPEN_AI_API_KEY
import openai


class OpenAPI:
    SUMMARY_MODEL = "text-davinci-002" # model to use for summarization
    MAX_TOKENS_DAVIN2 = 4000 # max tokens for davinci-002 is 4,000
    
    def __init__(self, api_key=OPEN_AI_API_KEY):
        self.api_key = api_key
        self.openai.api_key = api_key
    
    def summarize_text(self, text, max_resp_tokens=256, summary_prompt=0):
        """ 
        Simple function that takes string input and returns a summary of the text via OpenAI's API 
        
        A few ways we can prompt the model to write a summary:
            0 - "Summarize the following text: \n\n<text>"
            1 - "<text> \ntd;dr:" - https://medium.com/geekculture/a-paper-summarizer-with-python-and-gpt-3-2c718bc3bc88
            2 - "<text> \nSummary:"
            3 - "<text> \nSummary of the above text:"
            
        We can also vary the max tokens to be returned (this needs to be tuned as to not miss out important technical details)
            - vary depending on the length of the text?
            - set to specific number?
            - vary based on information density of text? - https://towardsdatascience.com/linguistic-complexity-measures-for-text-nlp-e4bf664bd660
        """
        if summary_prompt == 0:
            prompt = "Summarize the following text: \n\n" + text
        elif summary_prompt == 1:
            prompt = text + "\ntd;dr:"
        elif summary_prompt == 2:
            prompt = text + "\nSummary:"
        elif summary_prompt == 3:
            prompt = text + "\nSummary of the above text:"
        
        
        # Checks text size, returns error if larger than max tokens
        response = openai.Completion.create(
            model=self.SUMMARY_MODEL,
            prompt=prompt,
            max_tokens=max_resp_tokens,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        return response.choices[0].text
    
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
    