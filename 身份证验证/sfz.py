from sfz_ui import Ui_Form
from PySide2 import QtWidgets, QtGui, QtCore
import sys
import datetime
import sqlite3
import os.path


class SfzDialog(Ui_Form, QtWidgets.QWidget):

    cx = None
    cu = None

    def __init__(self):
        super(SfzDialog, self).__init__()
        self.setupUi(self)
        if not os.path.exists('sfz.db'):
            QtWidgets.QMessageBox.critical(None, '错误', '数据库文件 sfz.db 未找到!')
            app.exec_()
        else:
            self.cx = sqlite3.connect('sfz.db')
            self.cu = self.cx.cursor()
        self.btnQuery.clicked.connect(self.query)
        self.btnClear.clicked.connect(self.clear)
        self.lEditNum.textChanged.connect(self.lEditNumTextChanged)

    def closeEvent(self, event):
        if self.cx is not None:
            self.cx.close()

    def clear(self):
        self.lEditGender.setText('')
        self.lEditRegion.setText('')
        self.lEditBirth.setText('')
        self.lEditResult.setText('')
        self.lEditNum.setText('')

    def query(self):
        if not os.path.exists('sfz.db'):
            QtWidgets.QMessageBox.critical(None, '警告', '数据库文件 sfz.db 未找到!程序将退出!')
            app.exec_()
        sfz = self.lEditNum.text()
        self.lEditGender.setText('')
        self.lEditRegion.setText('')
        self.lEditBirth.setText('')
        self.lEditResult.setText('')
        # 长度
        if len(sfz) != 18:
            QtWidgets.QMessageBox.warning(None, '注意', '身份证长度错误！')
            return
        # 校验码
        idCodeTuple = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
        checkCodeTuple = ('1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2')
        if checkCodeTuple[sum((a * b for a, b in zip(idCodeTuple, (int(a) for a in sfz[:-1])))) % 11] != sfz[-1].upper():
            self.lEditResult.setText('末位校验码错误')
            return
        # 地区
        region = sfz[:6]
        sql = self.cu.execute('select region from sfz_0 where number = ?', (region,)).fetchone()
        if sql is None:
            self.lEditResult.setText('地区错误')
            return
        else:
            self.lEditRegion.setText(sql[0])

        # 年月日
        year = sfz[6:10]
        month = sfz[10:12]
        day = sfz[12:14]

        try:
            datetime.date(int(year), int(month), int(day))
        except ValueError:
            self.lEditResult.setText('出生年月日格式错误')
            return

        if year + month + day > datetime.datetime.now().strftime('%Y%m%d') or year<'1900':
            self.lEditResult.setText('出生年月日错误')
            return
        self.lEditBirth.setText(year + '年' + month + '月' + day + '日')

        # 性别
        gender = sfz[16:17]
        if int(gender) % 2 == 0:
            self.lEditGender.setText('女')
        else:
            self.lEditGender.setText('男')

        self.lEditResult.setText('身份证校验正确')

    def lEditNumTextChanged(self):
        preRegex = QtCore.QRegExp('^\d{17}[0-9xX]$')  # 身份证正则预校验
        preValidator = QtGui.QRegExpValidator(preRegex, self.lEditNum)
        self.lEditNum.setValidator(preValidator)


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    MainWindow = SfzDialog()
    MainWindow.show()
    sys.exit(app.exec_())