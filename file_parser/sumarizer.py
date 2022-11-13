"""
Considerations for generating a file summary:

OpenAPI_summarizer.summarize_text():
    We can vary the max tokens to be returned (tuned as to not miss out important technical details but also not be too long of a summary)
        - vary depending on the length of the text?
        - set to specific number?
        - vary based on information density of text? - https://towardsdatascience.com/linguistic-complexity-measures-for-text-nlp-e4bf664bd660
"""