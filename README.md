# Thailand Official Budget to CSV
## How it work
  หลักการทำงานของ script จะแยกเป็น 2 ส่วน
  1. ocrAndSave.py OCR โดย google cloud vision แล้ว save ไว้ก่อน เป็น list of dict
  1. parserToCSV.py เปิดที่ save ไว้แล้ว ตัด string โดยจับ pattern แยก 2 column(หัวข้อ และ มูลค่า) แล้วมาเทียบกันถ้าไม่ตรงกัน ต้อง debug
  
  script ไม่ได้ parse ทั้งหมด แต่เลือกเฉพาะส่วนของรายละเอียด (หัวข้อ 7 ใน table of content) ของแต่ละหน่วยงานในเล่มขาวคาดแดง(ฉ.3)
  
### ocrAndSave.py
```
python ocrAndSave.py -i input_pdf -o output
```
ต้องมี service accout ของ google vision cloud(billing account needed which require credit card or paypal account) และ export ไว้ใน env in terminal seesion
```
 export GOOGLE_APPLICATION_CREDENTIALS=/home/$USER/works/experiment/vision_a.json     
```
จะทยอยๆ push ให้

### parserToCSV.py
```
python parserToCSV.py -i input_from_above -o output_csv
```
หากส่วนที่จำนวนหัวข้อ กับ มูลค่า ไม่ตรงกันจะ ขึ้น error ต้องลองไล่ดู ว่าตัดพลาดตรงไหน แล้ว เพิ่ม pattern Regex เข้าไป(ส่วนใหญ่เพิ่มที่ third pattern)
โครงการที่ตรงจะ save เป็น csv

เวลา debug
```
python parserToCSV.py -i input_from_above -o output_csv > .debug.txt
```

#### สาเหตุที่ผิดพลาด
* OCR มาผิดหรือ ไม่ครบประโยคเพราะ font ที่ใช้ เป็น font อ่านยาก(Dilleniaupc) (แต่ google cloud vision correct more than 99 percent)
* pattern ของหัวข้อ ไม่มีมาตรฐาน

เป็น edge case ซึ่งต้องแก้ทีละไฟล์

#### Folder
* data/ocr_text ---> data from ocrAndSave.py
* data/csv final ---> result without error

#### Project Goal
* ระยะแรกทำ 64 ให้ครบทุกเล่มที่ทำได้ แล้ว publish 

#### Note


#### LINK
(สำนักงบ)[http://www.bb.go.th/topic3.php?catID=1328&gid=860&mid=544]
