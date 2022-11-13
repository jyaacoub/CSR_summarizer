# %%
from file_reader import pdf_reader
from file_parser.chunker import Chunker
from models.open_ai import OpenAPI_summarizer, OpenAPI_search
from common.constants import GOOGLE_CSR

import pandas as pd
# %%
chunker = Chunker(min(OpenAPI_search.MAX_TOKENS, OpenAPI_summarizer.MAX_TOKENS))
srch_mdl = OpenAPI_search()
sum_mdl = OpenAPI_summarizer(tokenizer=srch_mdl.load_tokenizer())
top_n = 10


# %%
pdf_content = pdf_reader(GOOGLE_CSR) # looks like: {section: {"content":text, "pages": (int,int)}, ...}