import fitz
import pickle
import re
import csv
import argparse


def readDivision(division):

    parserToggle = False
    projectInfo = ''
    projects = []
    plan = ''
    finalResult = []

    ## try to extract only pages with detail(without table) and concat infomation of all pages in the same project to one object ##
    for page in division:
        text = page[0]
        pageNum = page[1] + 1
        department = page[2]
        division = page[3]

        isPlan = re.search(r'7\.\d แผนงาน.+\n', text)

        isProject = re.search(r'7\.\d\.\d ผลผลิต|7\.\d\.\d โครงการ', text)

        if isProject or isPlan:
            parserToggle = False
            if projectInfo != '':
                projects.append({'plan': currentPlan, 'info': projectInfo, 'page': pageNum,
                                 'department': department, 'division': division})

        if isPlan:
            plan = isPlan.group(0)

        if text.find('รายละเอียดงบประมาณจำแนกตามงบรายจ่าย') != -1:
            currentPlan = plan
            projectInfo = ''
            parserToggle = True

        if parserToggle:
            projectInfo += text

    projects.append({'plan': currentPlan, 'info': projectInfo, 'page': pageNum,
                     'department': department, 'division': division})

    ## split pattern ##

    firstPattern = r'(?=\d\. งบ)|(?=\nงบเงินอุดหนุน)'
    secondPattern = r'^(?=\d{1,2}\.\d [^k].+\n)|^(?=เงินอุดหนุนทั่วไป)'

    for p in projects:
        info = p['info']
        pageNum = p['page']
        division = p['division']
        department = p['department']

        resultRows = []

        def rowConstruct(page, name, plan, project, budgetType='รวม', subType='รวม', department=department, division=division, ):
            return{'name': name, 'subType': subType, 'budgetType': budgetType, 'project': project, 'plan': plan, 'department': department, 'division': division, 'page': page}

        ## split row between subject element and baht value ##
        [bahtList, infoRow] = filterBaht(info)

        projectName, * \
            projectDetail = re.split(firstPattern, infoRow, flags=re.MULTILINE)

        ## replace header with none(repetitive infomation) ##
        projectName = re.sub(
            r'รายละเอียดงบประมาณจำแนกตามงบรายจ่าย\n',  '', projectName)

        ### check and split เงินนอกงบประมาณ ###

        if projectName.find('เงินนอกงบประมาณ') > 0:

            ## split with first pattern ##
            projectName, outBud = re.split(r'^(?=เงินนอกงบประมาณ)', projectName, 1,flags=re.MULTILINE)
            resultRows.append(rowConstruct(
                pageNum, projectName, p['plan'], projectName))
            resultRows.append(rowConstruct(
                pageNum, outBud, p['plan'], projectName,))

        else:
            resultRows.append(rowConstruct(
                pageNum, projectName, p['plan'], projectName,))

        for f in projectDetail:

            ### check and  split เงินนอกงบประมาณ again ###

            if f.find('เงินนอกงบประมาณ') > 0 and f.find('เงินนอกงบประมาณ') < 50:

                ### split second pettern ###
                budgetType, outBud, typeDetail = re.split('\n', f, 2)
                resultRows.append(rowConstruct(
                    pageNum, budgetType, p['plan'], projectName))
                resultRows.append(rowConstruct(
                    pageNum, outBud, p['plan'], projectName,))

            else:
                budgetType, typeDetail = re.split('\n', f, 1)
                resultRows.append(rowConstruct(
                    pageNum, budgetType, p['plan'], projectName,))

            secondSplit = re.split(
                secondPattern, typeDetail, flags=re.MULTILINE)

            if len(secondSplit) > 1:
                secondSplit = secondSplit[1:]
                for s in secondSplit:
                    if s.find('เงินนอกงบประมาณ') > 0 and s.find('เงินนอกงบประมาณ') < 50:
                        secondName, outBud, theRest = s.split('\n', 2)
                        resultRows.append(rowConstruct(
                            pageNum, secondName, p['plan'], projectName, budgetType, secondName))
                        resultRows.append(rowConstruct(
                            pageNum, outBud, p['plan'], projectName, budgetType, secondName))
                    else:
                        secondName, theRest = s.split('\n', 1)
                        resultRows.append(rowConstruct(
                            pageNum, secondName, p['plan'], projectName, budgetType, secondName))
                    if len(theRest) > 1:
                        thirdText = theRest
                        for row in (finalSpiter(thirdText)):
                            resultRows.append(rowConstruct(
                                pageNum, row, p['plan'], projectName, budgetType, secondName))

            else:
                for row in finalSpiter(secondSplit[0]):
                    resultRows.append(rowConstruct(
                        pageNum, row, p['plan'], projectName, budgetType, ))

        ## check result by compare length of value and subject(derive from above splitting)##

        if len(bahtList) == len(resultRows):
            for idx, val in enumerate(resultRows):
                if len(bahtList) > idx:
                    value = (re.sub(r'\D', '', bahtList[idx]))
                    if value == '':
                        value = 0
                    else:
                        value = int(value)
                    page = val['page']
                    id = str(1)+'_'+str(page)+'_'+str(idx)

                    val.update({'value': value, 'id': id})
                    finalResult.append(val)

        else:
            print('Error: indiscrepencies at : ', division, plan, projectName,)
            print('bahtlist: ', len(bahtList), 'resultList: ', len(resultRows))
            for idx, val in enumerate(resultRows):
                if len(bahtList) > idx:
                    value = (re.sub(r'\D', '', bahtList[idx]))

                    val.update({'value': value})
                    print([val['name'], val['value']], val['page'])
            print(infoRow)
            for r in resultRows:
                print('xxx')
                print(r)
            for b in bahtList:
                print('bbb')
                print(b)

    return finalResult


def filterBaht(text):
    bahtPattern = r'.*(?<![ธนเ])บาท?\n|^\d{1,3},\d{3},\d{3}$'
    valueList = re.findall(bahtPattern, text, flags=re.MULTILINE)
    newInfo = re.sub(bahtPattern, '', text, flags=re.MULTILINE)
    return [valueList, newInfo]


def finalSpiter(text):
    rows = []
    ### thirdpattern = (123) | 2) | 2.3.4 | edge case>>> ###
    thirdPattern = r'^(?=\([\dZTBg\. S]{1,5}\))|^(?=\d{1,2}\.?\d{0,2}\.?\d{0,2}\.?\d{0,2}\)[^\n])|^(?=[1-3]{1,2}\.?\d\.?\d\.?\d{0,2} [เค])|^(?=ค่าใช้จ่ายในการบำรุงรักษาเครื่องปรับอากาศ)|^(?=- เงินรายได้)|^(?=2 ค่าสาธารณูปโภค)|^(?=1 ค่าใช้สอย)|^(?=โครงการสร้างโอกาสในการพัฒนาสมรรถนะของผู้ประกอบอาชี|^(?=ค่าใช้จ่ายในการดำเนินภารกิจส่งเสริมสินค้าและธุรกิจฮาลาลในต่างประเทศ))|^(?=ค่าใช้จ่ายในการสนับสนุนการดำเนินงานของคณะกรรม)|^(?=ค่าใช้จ่ายในการเพิ่มประสิทธิภาพระบบสารสนเทศเพื่อ|^(?=\( \(2\) ค่าเบี้ยประชุ))'
    yearPattern = r'^(?=วงเงินทั้งสิ้?น)|^(?=.*ตั้งงบประมา?ณ?)|^(?=.*ผูกพันงบประมาณ)|^(?=เงินงบประมาณ)|^(?=เงินนอกงบประมาณ)|^(?=วงเงินทงสน)'
    thirdSplit = re.split(thirdPattern, text, flags=re.MULTILINE)
    thirdSplit = thirdSplit[1:]
    for t in thirdSplit:
        yearSplit = re.split(yearPattern, t, flags=re.MULTILINE)
        if len(yearSplit) > 1:
            for l in yearSplit:
                rows.append(l)

        else:
            rows.append(yearSplit[0])
    return rows


def readPickle(picklePath, output):
    with open(picklePath, 'rb') as fp:
        arr = pickle.load(fp)
    rows = []
    for div in arr:
        result = readDivision(div)
        for row in result:
            rows.append(row)

    with open(output, 'w') as f:
        w = csv.DictWriter(f, rows[1].keys())
        w.writeheader()
        w.writerows(rows)


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="ocr pdf"
    )
    parser.add_argument(
        "-o", "--output", type=str, nargs="?", help="The output directory", default=""
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
    readPickle(arg.input_file, arg.output)


if __name__ == "__main__":
    main()

# pickleP = './data/OCR_text/1.txt'

# readPickle(pickleP)
