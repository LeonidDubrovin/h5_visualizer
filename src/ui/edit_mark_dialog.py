# Form implementation generated from reading ui file '.\edit_mark_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(459, 130)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_xmax = QtWidgets.QLabel(parent=Dialog)
        self.label_xmax.setObjectName("label_xmax")
        self.verticalLayout_3.addWidget(self.label_xmax)
        self.txtXmin = QtWidgets.QLineEdit(parent=Dialog)
        self.txtXmin.setObjectName("txtXmin")
        self.verticalLayout_3.addWidget(self.txtXmin)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_xmin = QtWidgets.QLabel(parent=Dialog)
        self.label_xmin.setObjectName("label_xmin")
        self.verticalLayout_2.addWidget(self.label_xmin)
        self.txtXmax = QtWidgets.QLineEdit(parent=Dialog)
        self.txtXmax.setObjectName("txtXmax")
        self.verticalLayout_2.addWidget(self.txtXmax)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btnColorPick = QtWidgets.QPushButton(parent=Dialog)
        self.btnColorPick.setObjectName("btnColorPick")
        self.horizontalLayout_3.addWidget(self.btnColorPick)
        self.frameColor = QtWidgets.QFrame(parent=Dialog)
        self.frameColor.setMinimumSize(QtCore.QSize(30, 0))
        self.frameColor.setMaximumSize(QtCore.QSize(30, 16777215))
        self.frameColor.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frameColor.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frameColor.setObjectName("frameColor")
        self.horizontalLayout_3.addWidget(self.frameColor)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnCancel = QtWidgets.QPushButton(parent=Dialog)
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout.addWidget(self.btnCancel)
        self.btnEdit = QtWidgets.QPushButton(parent=Dialog)
        self.btnEdit.setObjectName("btnEdit")
        self.horizontalLayout.addWidget(self.btnEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Редактирование марки"))
        self.label_xmax.setText(_translate("Dialog", "xmin"))
        self.label_xmin.setText(_translate("Dialog", "xmax"))
        self.btnColorPick.setText(_translate("Dialog", "Выбрать цвет"))
        self.btnCancel.setText(_translate("Dialog", "Отмена"))
        self.btnEdit.setText(_translate("Dialog", "OK"))
