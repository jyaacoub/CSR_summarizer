# %%
from file_parser.sumarizer import FileSummarizer
from common.constants import GOOGLE_CSR

import os
import datetime
# To control logging level for various modules used in the application:
import logging
logging.disable(logging.INFO)


# %% creating chunks and searching for top matching chunks
fs = FileSummarizer(GOOGLE_CSR, chunk_size=150)

# %%
final_sum = fs.summarize_file("Greenhouse gas, GHG emissions",
                  summary_size=100, 
                  top_n=50, 
                  capture_all_sections=False)

# %% creating folder with timestamp
newpath = "data/final_summaries/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
if not os.path.exists(newpath):
    os.makedirs(newpath)

# saving to excel
fs.save_summaries(newpath + "/")