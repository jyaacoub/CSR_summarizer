from PyPDF2 import PdfReader, PdfFileReader, PdfFileWriter
#from common.constants import GOOGLE_CSR

GOOGLE_CSR = "file_reader/google-2022-environmental-report.pdf" #import Google CSR file, update the path to constants.py later
pdf = PdfFileReader(GOOGLE_CSR)

#uses metadata to find page numbers of each section and stores the section header as the key and content as value
toc_dict = {} #where dictionary is stored
page_num = [] #stores the page numbers of each section

print("extracting page numbers for each section...")
for outline in pdf.outlines:
    try:
        page_num.append([pdf.getDestinationPageNumber(outline)+1, outline.title])
    except:
        pass

page_num.append([pdf.numPages, "Last Page"]) # add the last page of the document
print(page_num)
print('')

for i in range(len(page_num)-1):
    current_section_start = page_num[i][0]
    next_section_start = page_num[i+1][0]
    section_title = page_num[i][1]

    for current_page in range(current_section_start, max(next_section_start, current_section_start+1)):
        print(f"Current Page iterating: {current_page}")
        pageObj = pdf.getPage(current_page)
        try:
            txt = pageObj.extract_text()
            if toc_dict.get(section_title) is not None:
                toc_dict[section_title] = toc_dict[section_title] + txt
            else:
                toc_dict[section_title] = txt
        except:
            pass
    print(section_title)
    print(''.center(100, '-'))
    print(toc_dict[section_title])
    print('\n')
                



# with open('file_reader/CSR_text.txt', 'w', encoding="utf-8") as file:
#     for page_num in range(pdf.numPages):
#         pageObj = pdf.getPage(page_num)

#         try:
#             txt = pageObj.extract_text()
#             print('page extracted')
#         except:
#             pass
#         else:
#             # file.write('Page {0}\n'.format(page_num + 1))
#             # file.write(''.center(100, '-'))
#             # file.write('\n')
#             # file.write(txt)
#             # file.write('\n\n\n')
#     #file.close()







