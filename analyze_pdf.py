from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract

PARCEL_LIST = ["R2106140","R2106141","R2106143","R2138706","R2145549"]

## Parcel PDFs -> List of Images. Using PyPDF2, pdf2image.
def pdfs_to_images():
    # Merge PDFs
    tmp_pdfs = BytesIO()
    parcel_pdfs = PdfFileWriter()
    for parcel in PARCEL_LIST:
        pdf = PdfFileReader("pdf/{}.pdf".format(parcel))
        parcel_pdfs.addPage(pdf.getPage(0))
    parcel_pdfs.write(tmp_pdfs)

    # Make images from PDF
    images = convert_from_bytes(tmp_pdfs.getvalue(), dpi=150, use_cropbox=True, fmt="jpg")
    return images  

## Images -> Txt file. Using pytesseract. 
def images_to_text(images):
    i = 0
    for parcel in PARCEL_LIST:
        with open("data/{}.txt".format(parcel), 'w') as f:
            f.write(pytesseract.image_to_string(images[i]))
        i =+ 1

def main():
    images_to_text(pdfs_to_images())

if __name__ == '__main__':
    main()