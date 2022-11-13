# %%
from file_reader.pdf_reader import pdf_reader
from file_parser.chunker import Chunker
from models.open_ai import OpenAPI_summarizer, OpenAPI_search
from models.token_counter import TokenCounter
from common.constants import GOOGLE_CSR

import pandas as pd
from tqdm import tqdm

# %%
tkn = TokenCounter(exact_token_count=True)
chunker = Chunker(token_counter=tkn, max_tokens=250)
srch_mdl = OpenAPI_search(token_counter=tkn)
sum_mdl = OpenAPI_summarizer(token_counter=tkn)
top_n = 10
QRYS = ['environment', 
        'renewable energy', 
        'greenhouse gas (ghg) emmissions']


# %%
pdf_content = pdf_reader(GOOGLE_CSR) # looks like: {section: {"content":text, "pages": (int,int)}, ...}

# %% chunking the content
pdf_chunked = pd.DataFrame(columns=['text', 'section', 'chunk_no'])

for section in pdf_content:
    print('chunking section:', section)
    chunks = chunker.chunk_sentence(pdf_content[section]['content'])
    # convert to dataframe
    df_section = pd.DataFrame({'text':chunks, 'section':section,
                               'chunk_no':range(len(chunks))})
    pdf_chunked = pd.concat([pdf_chunked, df_section])

pdf_chunked.reset_index(drop=True, inplace=True)
    
# %% semantic search
pdf_chunked_scores = srch_mdl.get_scores(pdf_chunked, QRYS[1]).sort_values(by='scores', ascending=False)


# %%
