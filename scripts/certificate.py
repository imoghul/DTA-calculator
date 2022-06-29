from docx import *
from docx.shared import *
import contextlib
from docx2pdf import convert
import os,sys
import shutil
docPath = "C:\\Users\\Ibrahim.Moghul\\Desktop\\Data Analysis Scripts\\OUTPUT\\FACTORY\\Certificates\\"


def createCertificate(sn,cbDate,result,path=docPath):
    dest = path+"%s_certificate.docx"%sn
    shutil.copy2(path+"TEMPLATE.docx",dest)
    doc = Document(dest)

    for t in doc.tables:
        for c in t._cells:
            
            if c.text == "SERIAL NUMBER": 
                c.text = sn
                paragraphs = c.paragraphs
                paragraph = paragraphs[0]
                run_obj = paragraph.runs
                run = run_obj[0]
                font = run.font
                font.size = Pt(30)
                font.color.rgb = RGBColor(0x00,0x00,0x00)#RGBColor(0xff,0xff,0xff)
                font.name = "AvenirNext LT Pro Regular"
            elif c.text == "CALIBRATION DATE" or c.text == "RESULT": 
                if(c.text == "CALIBRATION DATE"): c.text = cbDate
                elif (c.text == "RESULT"): c.text = result
                paragraphs = c.paragraphs
                paragraph = paragraphs[0]
                run_obj = paragraph.runs
                run = run_obj[0]
                font = run.font
                font.size = Pt(12)
                font.color.rgb = RGBColor(0x00,0x00,0x00)#RGBColor(0xff,0xff,0xff)
                font.name = "AvenirNext LT Pro Regular"
    
            doc.save(dest)
    

def convertToPDF_doc(doc):
    # with contextlib.redirect_stdout(open(os.devnull, 'w')):
    try:
        print('Converting %s to pdf'%doc.replace("\\","/").split("/")[-1])
        convert(doc)
    except:
        print(doc+" couldn't be converted to a pdf")


def convertToPDF_path(path):
    # with contextlib.redirect_stdout(open(os.devnull, 'w')):
    try:
        print('Converting certificates to pdfs')
        convert(path)
    except Exception as e:
        pass#print("Some files couldn't be converted to a pdf")