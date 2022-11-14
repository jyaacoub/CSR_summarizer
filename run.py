# %%
from file_parser.sumarizer import FileSummarizer
from common.constants import GOOGLE_CSR

import os
import datetime
# To control logging level for various modules used in the application:
import logging
logging.disable(logging.INFO)


# %% creating chunks and searching for top matching chunks
fs = FileSummarizer(GOOGLE_CSR, chunk_size=300)

# %%
final_sum = fs.summarize_file("Energy efficiency, Low-carbon fuels, LEED certified, Renewable energy, Solar power, Wind power",
                  summary_size=100, 
                  top_n=20, 
                  capture_all_sections=True)

# %% creating folder with timestamp
newpath = "data/final_summaries/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
if not os.path.exists(newpath):
    os.makedirs(newpath)

# saving to excel
fs.save_summaries(newpath + "/")

# %% creating summaries for these top chunks
# sum_0 = pd.DataFrame(columns=['summary', 'section', 'chunk_no'])

# for _, row in tqdm(top_chunks_0.iterrows(), total=top_chunks_0.shape[0], 
#                    desc="Summarizing chunks"):
#     sum = fs.sum_mdl.summarize_text(row['text'], 
#                               max_resp_tokens=57, summary_prompt=1, # tl;dr prompt is the best
#                               bullet_points=False)
    
#     # adding to the dataframe
#     sum_0 = sum_0.append({'summary': sum,
#                           'section': row.section,
#                           'chunk_no': row.chunk_no}, 
#                          ignore_index=True)

    
# # %% saving to excel
# sum_0.to_excel('data/chunk_sum/sum_0.xlsx')


# # %% Creating summaries for sections with sum_0
# sum_1 = pd.DataFrame(columns=['summary', 'section'])
# for section in tqdm(sum_0.section.unique(), desc="Summarizing sections"):
#     section_text = sum_0[sum_0.section == section].summary.str.cat(sep='\n')
    
#     sum = fs.sum_mdl.summarize_text(section_text, max_resp_tokens=100, 
#                                     summary_prompt=1, # tl;dr prompt is the best
#                                     bullet_points=False)
    
#     # adding to the dataframe
#     sum_1 = sum_1.append({'summary': sum,
#                           'section': section}, 
#                          ignore_index=True)
    
    
# # %% saving to excel
# sum_1.to_excel('data/chunk_sum/sum_1.xlsx')

# # %% getting final summary
# print("Getting final summary...")
# pdf_summary = fs.sum_mdl.summarize_text(sum_1.summary.str.cat(sep='\n'),
#                                         max_resp_tokens=200, 
#                                         summary_prompt=1, # tl;dr prompt is the best
#                                         bullet_points=False)
# print("Done! Final summary:\n\n", pdf_summary)
# %%
