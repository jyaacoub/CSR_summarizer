from file_parser.sumarizer import FileSummarizer
from common.constants import GOOGLE_CSR

#  creating chunks and searching for top matching chunks
fs = FileSummarizer(GOOGLE_CSR, 
                    chunk_size=250) # chunk size for summarization
final_sum = fs.summarize_file(
                query="Greenhouse gas, GHG emissions, plans, future",
                summary_size=200, # max size for each summary
                top_n=20,         # how many top matching chunks to summarize
                capture_all_sections=False) # include chunks from all sections?




# SAVING THE SUMMARY
import os
import datetime
# creating folder with timestamp
newpath = "data/final_summaries/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
if not os.path.exists(newpath):
    os.makedirs(newpath)

# saving to excel
fs.save_summaries(newpath + "/")