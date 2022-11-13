#uses metadata to find page numbers of each section and stores the section header as the key and content as value
from PyPDF2 import PdfReader, PdfFileReader, PdfFileWriter

def pdf_reader(file_path):
    pdf = PdfFileReader(file_path)

    toc_dict = {} #where dictionary is stored
    page_num = [] #stores the page numbers of each section

    print("extracting page numbers for each section...")
    for outline in pdf.outlines: # adds all the section page numbers into a 2d array [page number, section title]
        try:
            page_num.append([pdf.getDestinationPageNumber(outline)+1, outline.title])
        except:
            pass

    page_num.append([pdf.numPages, "Last Page"]) # add the last page of the document
    print(page_num)
    print('')

    for i in range(len(page_num)-1): #loop for adding all the content into the dictionary
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
    
    return toc_dict
                



#UNUSED CODE FOR EXTRACTING PDF INTO FILE----------------------------------------------------------------------------------
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







