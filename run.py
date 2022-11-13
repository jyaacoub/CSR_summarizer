# %%
from file_reader.pdf_reader import pdf_reader
from file_parser.chunker import Chunker
from models.open_ai import OpenAPI_summarizer, OpenAPI_search
from common.constants import GOOGLE_CSR

import pandas as pd
from tqdm import tqdm
# %%
chunker = Chunker(min(OpenAPI_search.MAX_TOKENS, OpenAPI_summarizer.MAX_TOKENS))
srch_mdl = OpenAPI_search(exact_token_count=True)
sum_mdl = OpenAPI_summarizer(exact_token_count=True,
                             okenizer=srch_mdl.load_tokenizer())
top_n = 10
QRYS = ['environment', 
           'renewable energy', 
           'greenhouse gas (ghg) emmissions']


# %%
pdf_content = pdf_reader(GOOGLE_CSR) # looks like: {section: {"content":text, "pages": (int,int)}, ...}

# %% chunking the content
pdf_chunked = pd.DataFrame(columns=['text', 'section', 'chunk_no'])

for section in tqdm(pdf_content):
    chunks = chunker.chunk(pdf_content[section]['content'])
    # convert to dataframe
    df_section = pd.DataFrame({'text':chunks, 'section':section,
                               'chunk_no':range(len(chunks))})
    pdf_chunked = pd.concat([pdf_chunked, df_section])

pdf_chunked.reset_index(drop=True, inplace=True)
    
# %% semantic search
pdf_chunked = srch_mdl.get_scores(pdf_chunked, QRYS[1])
