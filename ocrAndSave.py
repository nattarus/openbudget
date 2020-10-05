import pickle
import re
from google.cloud import vision
import argparse
import fitz


def pageParser(doc, pageNum):

    page = doc[pageNum]
    pix = page.getPixmap(matrix=fitz.Matrix(
        4, 4), colorspace='csGRAY', clip=[0, 50, 1000, 1000])
    pixImg = pix.getPNGData()

    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=pixImg)

    response = client.document_text_detection(image=image)
    labels = response.full_text_annotation

    return labels.text


def getContentTable(filePath):
    doc = fitz.open(filePath)
    index = []
    endPageToggle = 0
    for (lvl, title, page) in doc.getToC():
        if lvl == 3:
            department = title
        if lvl == 4:
            division = title
        if endPageToggle == 1:
            info["endPage"] = page
            endPageToggle = 0
            index.append(info)
        if title.find('รายละเอียดงบประมาณจำแนกตามแผนงาน') != -1:
            info = {
                "department": department,
                "division": division,
                'page': page
            }
            endPageToggle = 1
    print(index)

    return index


def pageOcr(pdfPath, output):
    doc = fitz.open(pdfPath)
    contentTable = getContentTable(pdfPath)
    result = []
    for table in contentTable:

        startPage = table['page'] - 1
        endPage = table['endPage'] - 1
        tempArr = []
        while startPage < endPage:

            page = doc[startPage]
            # pix = page.getPixmap()
            # pix.writeImage('testImg/page-%i.png' % page.number)

            text = pageParser(doc, startPage)
            print(page)
            startPage += 1
            tempArr.append(
                [text, page.number, table['department'], table['division']])
        result.append(tempArr)

    with open(output, 'wb') as fp:
        pickle.dump(result, fp)


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="ocr pdf"
    )
    parser.add_argument(
        "-o", "--output", type=str, nargs="?", help="The output directory", default="data/OCR_text/"
    )

    # parser.add_argument(
    #     "--output_dir", type=str, nargs="?", help="The output directory", default="data/OCR_text"
    # )

    parser.add_argument(
        "-i",
        "--input_file",
        type=str,
        nargs="?",
        help="pdf path",
        default="",
    )
    return parser.parse_args()


def main():
    arg = parse_arguments()
    pageOcr(arg.input_file, arg.output)


if __name__ == "__main__":
    main()


# pageOcr('data/budgetPdf/1.pdf')
