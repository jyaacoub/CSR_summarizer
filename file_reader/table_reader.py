#takes all tables in the pdf file and stores it in a file
import tabula
import os

# def table_reader(file_path):
file_path = "data/CSR_samples/google-2022-environmental-report.pdf"
tables = tabula.read_pdf(file_path, pages="all")

#saving into excel sheet for testing purposes
folder_name = "tables"
if not os.path.isdir(folder_name):
    os.mkdir(folder_name)
# iterate over extracted tables and export as excel individually
for i, table in enumerate(tables, start=1):
    table.to_excel(os.path.join(folder_name, f"table_{i}.xlsx"), index=False)
    # return tables
