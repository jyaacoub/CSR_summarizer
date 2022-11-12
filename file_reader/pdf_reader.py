from PyPDF2 import PdfReader, PdfFileReader, PdfFileWriter
#from common/constants.py import *

GOOGLE_CSR = "file_reader/google-2022-environmental-report.pdf" #import Google CSR file, update the path to constants.py later
pdf = PdfFileReader(GOOGLE_CSR)

with open('file_reader/CSR_text.txt', 'w', encoding="utf-8") as file:
    for page_num in range(pdf.numPages):
        pageObj = pdf.getPage(page_num)

        try:
            txt = pageObj.extract_text()
            print('page extracted')
        except:
            pass
        else:
            file.write('    Page {0}\n'.format(page_num + 1))
            file.write(''.center(100, '-'))
            file.write('\n')
            file.write(txt)
    file.close()






