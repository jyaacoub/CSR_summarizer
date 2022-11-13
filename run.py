# %%
from file_reader.pdf_reader import pdf_reader
from file_parser.chunker import Chunker
from file_parser.sumarizer import FileSummarizer
from models.open_ai import OpenAPI_summarizer, OpenAPI_search
from models.token_counter import TokenCounter
from common.constants import GOOGLE_CSR

import pandas as pd
from tqdm import tqdm

# %%
# tkn = TokenCounter(exact_token_count=True)
# chunker = Chunker(token_counter=tkn, max_tokens=300)
# srch_mdl = OpenAPI_search(token_counter=tkn)
# sum_mdl = OpenAPI_summarizer(token_counter=tkn)
# top_n = 10
QRYS = ['environment', 
        'renewable energy', 
        'greenhouse gas (ghg) emmissions']


# %%
fs = FileSummarizer(GOOGLE_CSR)

# %%
top_chunks_0 = fs.chunk_and_search(QRYS[0])
top_chunks_1 = fs.chunk_and_search(QRYS[1])
top_chunks_2 = fs.chunk_and_search(QRYS[2])

# %% Saving chunks to csv
top_chunks_0.drop(columns=['emb']).to_excel('data/chunk_search/chunks_0.xlsx')
top_chunks_1.drop(columns=['emb']).to_excel('data/chunk_search/chunks_1.xlsx')
top_chunks_2.drop(columns=['emb']).to_excel('data/chunk_search/chunks_2.xlsx')


# %%
