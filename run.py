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
