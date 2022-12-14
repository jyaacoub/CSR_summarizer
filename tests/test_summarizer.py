# %%
from transformers import GPT2Tokenizer
from models.open_ai import OpenAPI_summarizer
from tqdm import tqdm

text = """Environmental data
The following table provides an overview of our performance over time and 
includes both environmental data for our global operations (including our data  
centers, offices, networking infrastructure, and other facilities) and data beyond  
our operations (including our investments and technology). The majority of our  
environmental data covers Alphabet Inc. and its subsidiaries, including 
Google LLC. All reported data is global and annual unless otherwise specified. 
We obtain third-party assurance from an independent, accredited auditor for 
specific environmental data as part of our Independent Accountants’ Review , 
including select GHG emissions, energy, and water metrics as indicated in the 
table below.
For more information on our energy use and GHG emissions, see Alphabet’s 
CDP Climate Change Response on Google’s sustainability reports"""

# %%
op = OpenAPI_summarizer() # token counter is created in the constructor
samples = []
with tqdm(total=8) as pbar:
    for i in range(4):
        resT = op.summarize_text(text, max_resp_tokens=57, summary_prompt=i, bullet_points=False,
                                temp=0.7,   
                                top_p=1,           
                                freq_penalty=0.07, # should stay low to avoid just coming up with unrelated words
                                pres_penalty=0.2)
        pbar.update(1)
        resF = op.summarize_text(text, max_resp_tokens=57, summary_prompt=i, bullet_points=True,
                                temp=0.7,   
                                top_p=1,           
                                freq_penalty=0.07, # should stay low to avoid just coming up with unrelated words
                                pres_penalty=0.2)
        pbar.update(1)

        samples.append((resT, resF))

# %%
with open("data/CSR_samples/sample_summaries_p12_r1.txt", "w", encoding="utf-8") as f:
    for i, sample in enumerate(samples):
        f.write(f"Prompt {i}")
        f.write(f"\n{sample[0]}\n")
        f.write("\t"+"-"*20)
        f.write(f"\n{sample[1]}\n")
        f.write("#"*20)
        f.write("\n")
        

# %%
