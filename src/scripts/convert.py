import os
from PIL import Image
import PyPDF2
import contextlib


# path to file
def image_to_pdf(path: str) -> None:
    if not os.path.exists(path):
        print("poshel nahui")
        return

    image = Image.open(path)
    image = image.convert('RGB')
    idx = path.find('.')
    if (idx := path.find('.')) != -1:
        path = path[:idx]
    path += '.pdf'
    image.save(path)


# path to folder
def merge_pdf(path: str) -> None:
    if not os.path.exists(path):
        print("poshel nahui")
        return

    pdf_files_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if (file.endswith(".pdf")):
                pdf_files_list.append(os.path.join(root, file))

    print(*pdf_files_list, sep='\n')

    with contextlib.ExitStack() as stack:
        pdf_merger = PyPDF2.PdfMerger()
        files = [stack.enter_context(open(pdf, 'rb')) for pdf in pdf_files_list]
        for f in files:
            pdf_merger.append(f)
        with open(pdf_files_list[0][:-4] + '_merged.pdf', 'wb') as f:
            pdf_merger.write(f)


inp = input()
path = input()
if inp == 'new':
    image_to_pdf(path)
else:
    merge_pdf(path)
