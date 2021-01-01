import PyPDF2 as pypdf
import sys

INPUT_FILE = sys.argv[1]
pdfobject=open(INPUT_FILE,'rb')
pdf=pypdf.PdfFileReader(pdfobject)
print(pdf.getFormTextFields())
