import xlrd
import os
import django
import sys
import datetime
# 这两行很重要，用来寻找项目根目录，os.path.dirname要写多少个根据要运行的python文件到根目录的层数决定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(BASE_DIR)
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engs.settings')
django.setup()
from recite.models import Unit,ItemBank




def main(filename):

    data = trans_excel_to_list(filename)[1:]

    for row in data:
        in_data = ItemBank.objects.create(item_ch=row[0],
                                item_en=row[1],
                                item_type=row[2],
                                unit_id = row[3],
                                unit_item_id=row[4])
        in_data.save()

    with open('log.txt','a',encoding='utf8') as f:
        content = '%s:' % datetime.datetime.now() + filename
        f.write(content)

    print('上传完成')

def trans_excel_to_list(filename):
    '''

    :param workbook: a class from xlrd.open_workbook
    :return: 第一张表的所有有内容的单元格的列表, [[1,q,e,s],[2,e,r,t],...]
    '''
    # 读取工作薄
    workbook = xlrd.open_workbook(filename)

    table = workbook.sheets()[0]

    nrows = table.nrows

    ret = []

    for i in range(nrows):

        source = table.row_values(i)

        real = [s for s in source if s != '' ]

        ret.append(real)

    return ret

if __name__ == '__main__':
    filename = '01国情.xlsx'
    main(filename)