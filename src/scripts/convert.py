import os
from PIL import Image
import PyPDF2
import contextlib


# path to file
def image_to_pdf(path: str) -> None:
    """

    :param path:
    :return:
    """
    image = Image.open(path)
    image = image.convert("RGB")
    if (idx := path.rfind("."), -5) != -1:
        path = path[:idx]
    path += ".pdf"
    image.save(path)


def make_notebook(file_name: str, usr_id: int) -> None:
    """

    :param file_name:
    :param usr_id:
    :return:
    """
    path = os.path.abspath(os.getcwd()) + "/" + f"../usr_files/{usr_id}/"
    files = [path + file for file in os.listdir(path) if file.startswith(str(usr_id))]
    for f in files:
        if not f.endswith(".pdf"):
            image_to_pdf(f)
            os.remove(f)

    pdf_files_list = [
        path + file for file in os.listdir(path) if file.startswith(str(usr_id))
    ]

    with contextlib.ExitStack() as stack:
        pdf_merger = PyPDF2.PdfMerger()
        files = [stack.enter_context(open(pdf, "rb")) for pdf in pdf_files_list]
        for f in files:
            pdf_merger.append(f)
        with open(path + file_name + ".pdf", "wb") as f:
            pdf_merger.write(f)
    for f in pdf_files_list:
        os.remove(f)


def update_notebook(file_name: str, usr_id: int) -> None:
    """

    :param file_name:
    :param usr_id:
    :return:
    """
    path = os.path.abspath(os.getcwd()) + "/" + f"../usr_files/{usr_id}/"
    files = [path + file for file in os.listdir(path) if file.startswith(str(usr_id))]
    for f in files:
        if not f.endswith(".pdf"):
            image_to_pdf(f)
            os.remove(f)

    pdf_files_list = [
        path + file for file in os.listdir(path) if file.startswith(str(usr_id))
    ] + [path + file_name + ".pdf"]

    with contextlib.ExitStack() as stack:
        pdf_merger = PyPDF2.PdfMerger()
        files = [stack.enter_context(open(pdf, "rb")) for pdf in pdf_files_list]
        for f in files:
            pdf_merger.append(f)
        with open(path + file_name + ".pdf", "wb") as f:
            pdf_merger.write(f)
    for f in pdf_files_list:
        if f != path + file_name + ".pdf":
            os.remove(f)
