from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract

PROP_ACCOUNTS = ["R2106140","R2106141","R2106143","R2138706","R2145549"]

## Prop Account PDFs -> List of Images. Using PyPDF2, pdf2image.
def pdfs_to_images():
    # Crop and merge PDFs
    prop_account_pdf = PdfFileWriter()
    for prop_account in PROP_ACCOUNTS:
        page = PdfFileReader("pdf/{}.pdf".format(prop_account)).getPage(0)
        # Current Tax by District Section
        page.cropBox.lowerLeft = (325, 500)
        page.cropBox.upperRight = (588, 844)
        prop_account_pdf.addPage(page)
    
    # Write PDF to bytes and make images from it
    tmp_pdf = BytesIO()
    prop_account_pdf.write(tmp_pdf)
    images = convert_from_bytes(tmp_pdf.getvalue(), dpi=120, use_cropbox=True, thread_count=4)

    return images

## Images -> Txt file. Using pytesseract.
def images_to_text(images):
    #--user-words "C:\\Program Files\\Tesseract-OCR\\tessdata\\eng.user-words" 
    tesseract_config='--user-patterns "C:\\Program Files\\Tesseract-OCR\\tessdata\\eng.user-patterns" --dpi 120 --oem 1 --psm 6 '
    i = 0
    for parcel in PROP_ACCOUNTS:
        # with open("data/{}.txt".format(parcel), 'w') as f:
        #     f.write(pytesseract.image_to_string(images[i], config=tesseract_config))
        with open("data/{}.tsv".format(parcel), 'w') as f:
            f.write(pytesseract.image_to_data(images[i], config=tesseract_config))
        i += 1

## Save images as png for debugging.
def save_images(images):
    i = 0
    for img in images:
        img.save("data/{}.png".format(PROP_ACCOUNTS[i]))
        i += 1

def main():
    images = pdfs_to_images()
    images_to_text(images)
    save_images(images)

if __name__ == '__main__':
    main()