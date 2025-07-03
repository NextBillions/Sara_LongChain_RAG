# -*- coding:utf-8 -*-
import os
from win32com.client import Dispatch, DispatchEx  # 导入pywin32模块的client包下的函数
from win32com.client import constants  #  导入pywin32模块的client包下的保存COM常量的类
from win32com.client import gencache    #  导入pywin32模块的client包下的gencache函数
from PyPDF2 import  PdfFileReader  # 获取页码用
import pythoncom  # 导入封装了OLE自动化API的模块，该模块为pywin32的子模块
totalPages = 0  # 记录总页数的全局变量
returnlist = []  # 保存文件列表的全局变量


def wordtopdf(filelist,targetpath):
    valueList = []
    try:
        pythoncom.CoInitialize()   # 调用线程初始化COM库，解决调用Word 2007时出现“尚未调用CoInitialize”错误的问题
        gencache.EnsureModule('{00020905-0000-0000-C000-000000000046}', 0, 8, 4)
        # 开始转换
        w = Dispatch("Word.Application")
        for fullfilename in filelist:
            filename = fullfilename.name
            os.chdir(targetpath)
            # 获取文件名
            filename = fullfilename.name
            # 构造完整的保存路径
            file_path = os.path.join( targetpath, filename)
            # 保存文件
            with open(file_path, "wb") as f:
                # 写入文件内容
                f.write(fullfilename.getvalue())
            doc = os.path.abspath(filename)
            pdfname = targetpath+fullfilename.name + ".pdf"
            output = os.path.abspath(pdfname)
            pdf_name = output

            try:
                doc = w.Documents.Open(doc)
                doc.ExportAsFixedFormat(output, constants.wdExportFormatPDF, \
                                        Item=constants.wdExportDocumentWithMarkup,
                                        CreateBookmarks=constants.wdExportCreateHeadingBookmarks)
            except Exception as e:
                print(e)
            if os.path.isfile(pdf_name):
                valueList.append(pdf_name)
            else:
                print('转换失败！')
                return False
            doc.Close()
        return valueList
    except TypeError as e:
        print('出错了！')
        print(e)
        return -1

def pdf_to_word(word_path, filename,fullfilename):
    # 打开PDF文件
    import fitz
    # print(filename)
    # 构造完整的保存路径
    file_path = os.path.join(word_path, filename)
    # 保存文件
    with open(file_path, "wb") as f:
        # 写入文件内容
        f.write(fullfilename.getvalue())
    # print(file_path)

    pdf_document = fitz.open(file_path)
    from docx import Document
    doc = Document()

    # 遍历PDF的每一页
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        # 提取页面的文本
        text = page.get_text()

        # 将提取的文本添加到Word文档中
        doc.add_paragraph(text)

    # 保存Word文档
    doc.save(word_path+filename)
    print(f"PDF文件已转换为Word文档：{word_path+filename}")
    return word_path+filename

def pdftoword(filelist,targetpath):
    valueList = []
    try:
        for fullfilename in filelist:
            filename = fullfilename.name
            os.chdir(targetpath)
            # 获取文件名
            filename = fullfilename.name
            # 构造完整的保存路径
            file_path = os.path.join( targetpath, filename)
            # 保存文件
            with open(file_path, "wb") as f:
                # 写入文件内容
                f.write(fullfilename.getvalue())
            doc = os.path.abspath(filename)
            docname = targetpath+fullfilename.name + ".doc"
            output = os.path.abspath(docname)
            pdf_name = output
            # print(pdf_name,docname)

            ret=pdf_to_word(targetpath,fullfilename.name + ".doc",fullfilename)
            valueList.append(ret)

        print(valueList)
        return valueList
    except TypeError as e:
        print('出错了！')
        print(e)
        return -1

####################### 统计页码 ############################################

def getPdfPageNum(path):
    with open(path, "rb") as file:
        doc = PdfFileReader(file)
        pagecount = doc.getNumPages()
    return pagecount


####################### 提取目录 ############################################

def getPdfOutlines(pdfpath,listpath,isList):
    print("提取目录")
    with open(pdfpath, "rb") as file:
        doc = PdfFileReader(file)
        outlines = doc.getOutlines()  # 获取大纲
        global returnlist  # 全局变量，保存大纲的列表
        returnlist = []   # 创建一个空列表
        mylist = getOutline(outlines,isList)  # 递归获取大纲
        w = DispatchEx("Word.Application")  # 创建Word文档应用程序对象
        w.Visible = 1
        w.DisplayAlerts = 0
        doc1 = w.Documents.Add()# 添加一个Word文档对象
        range1 = doc1.Range(0,0)
        for item in mylist:       # 通过循环将获取的目录列表插入到Word文档对象中
             range1.InsertAfter(item)
        outpath = os.path.join(listpath,'list.docx') # 连接Word文档路径

        doc1.SaveAs(outpath)  # 保存文件
        doc1.Close()  # 关闭Word文档对象
        w.Quit()  # 退出Word文档应用程序对象
    return outpath


def getOutline(obj,isList):  # 递归获取大纲
    global returnlist
    for o in obj:
        if type(o).__name__ == 'Destination':
            # mypage = getRealPage(doc, pagecount, o.get('/Page').idnum)
            if isList:  # 包括页码
                returnlist.append( o.get('/Title') + "\t\t" + str(o.get('/Page') + 1) + "\n")
            else:       # 不包括页码
                returnlist.append(o.get('/Title') + "\n")
        elif type(o).__name__ == 'list':
            getOutline(o,isList)  # 递归调用获取大纲
    return returnlist
