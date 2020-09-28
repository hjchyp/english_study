from django.contrib.auth.decorators import login_required
import xlrd

class LoginRequiredMixin:
    @classmethod
    def as_view(cls,**initkwargs):
        # 调用继承的类的login的后面一个类的as_view()
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

def trans_excel_to_list(workbook_path):
    '''

    :param workbook: a class from xlrd.open_workbook
    :return: 第一张表的所有有内容的单元格的列表, [[1,q,e,s],[2,e,r,t],...]
    '''

    workbook = xlrd.open_workbook(workbook_path)

    table = workbook.sheets()[0]

    nrows = table.nrows

    ret = []

    for i in range(nrows):

        source = table.row_values(i)

        real = []
        for i in source:
            if type(i) == float:
                real.append(int(i))
            elif i != '':
                real.append(i)

        ret.append(real)


    return ret