import PyPDF2 as pypdf

pdfobject=open('en/solution/solution_12345.pdf','rb')
pdf = pypdf.PdfFileReader(pdfobject)
var = pdf.getFields()
print(var)
#%%
