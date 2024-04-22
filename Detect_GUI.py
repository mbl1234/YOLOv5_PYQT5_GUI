# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'ui/ui/detect_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import sys
import cv2
import argparse
import random
import torch
import numpy as np
import torch.backends.cudnn as cudnn
from models.common import DetectMultiBackend
from models.experimental import attempt_load
from utils.augmentations import letterbox
from utils.general import check_img_size, non_max_suppression, scale_coords, increment_path
from utils.torch_utils import select_device
from utils.plots import Annotator, plot_one_box2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ui_img.detect_rc
class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setWindowTitle("基于YOLOv5的识别检测演示软件V1.0")
        self.resize(1600, 900)
        self.centralwidget = QWidget()
        self.centralwidget.setObjectName("centralwidget")
        # 背景图像
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setGeometry(QtCore.QRect(-11, -10, 1661, 931))
        self.listView.setStyleSheet("background-image: url(:/detect/detect.JPG);")
        self.listView.setObjectName("listView")
        # 模型选择
        self.btn_selet_model = QtWidgets.QPushButton(self.centralwidget)
        self.btn_selet_model.setGeometry(QtCore.QRect(70, 810, 112, 51))
        font = QtGui.QFont()
        font.setFamily("Adobe 宋体 Std L")
        font.setPointSize(12)
        self.btn_selet_model.setFont(font)
        self.btn_selet_model.setObjectName("btn_selet_model")
        self.btn_selet_model.clicked.connect(self.seletModels)
        # 呈现原始图像
        self.label_show_yuanshi = QtWidgets.QLabel(self.centralwidget)
        self.label_show_yuanshi.setGeometry(QtCore.QRect(70, 80, 700, 700))
        self.label_show_yuanshi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_show_yuanshi.setObjectName("label_show_yuanshi")
        # 模型初始化
        self.btn_init_model = QtWidgets.QPushButton(self.centralwidget)
        self.btn_init_model.setGeometry(QtCore.QRect(220, 810, 112, 51))
        font = QtGui.QFont()
        font.setFamily("Adobe 宋体 Std L")
        font.setPointSize(12)
        self.btn_init_model.setFont(font)
        self.btn_init_model.setObjectName("btn_init_model")
        self.btn_init_model.clicked.connect(self.initModels)
        # 选择图像进行检测
        self.btn_detect_img = QtWidgets.QPushButton(self.centralwidget)
        self.btn_detect_img.setGeometry(QtCore.QRect(370, 810, 112, 51))
        font = QtGui.QFont()
        font.setFamily("Adobe 宋体 Std L")
        font.setPointSize(12)
        self.btn_detect_img.setFont(font)
        self.btn_detect_img.setObjectName("btn_detect_img")
        self.btn_detect_img.clicked.connect(self.openImage)
        # 保存结果图像
        self.btn_save_img = QtWidgets.QPushButton(self.centralwidget)
        self.btn_save_img.setGeometry(QtCore.QRect(1125, 810, 112, 51))
        font = QtGui.QFont()
        font.setFamily("Adobe 宋体 Std L")
        font.setPointSize(12)
        self.btn_save_img.setFont(font)
        self.btn_save_img.setObjectName("btn_save_img")
        self.btn_save_img.clicked.connect(self.saveImage)
        # 清除结果图像
        self.btn_clear_img = QtWidgets.QPushButton(self.centralwidget)
        self.btn_clear_img.setGeometry(QtCore.QRect(1275, 810, 112, 51))
        font = QtGui.QFont()
        font.setFamily("Adobe 宋体 Std L")
        font.setPointSize(12)
        self.btn_clear_img.setFont(font)
        self.btn_clear_img.setObjectName("btn_clear_img")
        self.btn_clear_img.clicked.connect(self.clearImage)
        # 退出应用
        self.btn_exit_app = QtWidgets.QPushButton(self.centralwidget)
        self.btn_exit_app.setGeometry(QtCore.QRect(1425, 810, 112, 51))
        font = QtGui.QFont()
        font.setFamily("Adobe 宋体 Std L")
        font.setPointSize(12)
        self.btn_exit_app.setFont(font)
        self.btn_exit_app.setObjectName("btn_exit_app")
        self.btn_exit_app.clicked.connect(self.exitApp)
        # 呈现结果图像
        self.label_show_jieguo = QtWidgets.QLabel(self.centralwidget)
        self.label_show_jieguo.setGeometry(QtCore.QRect(840, 80, 700, 700))
        self.label_show_jieguo.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label_show_jieguo.setObjectName("label_show_jieguo")
        # 标题
        self.label_show_title = QtWidgets.QLabel(self.centralwidget)
        self.label_show_title.setGeometry(QtCore.QRect(430, 20, 800, 41))
        self.label_show_title.setObjectName("label_show_title")
        # 主窗口
        self.setCentralWidget(self.centralwidget)
        self.retranslateUi(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(self.centralwidget)
        
    # 图像检测函数    
    def detectImage(self, name_list, img):
        '''
        :param name_list: 文件名列表
        :param img: 待检测图片
        :return: info_show:检测输出的文字信息
        '''
        showimg = img
        with torch.no_grad():
            img = letterbox(img, new_shape=self.opt.imgsz)[0]
            # Convert
            img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
            img = np.ascontiguousarray(img)
            img = torch.from_numpy(img).to(self.device)
            img = img.half() if self.opt.half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if len(img.shape) == 3:
                img = img[None]
            # Inference
            pred = self.model(img, augment=self.opt.augment, visualize=self.opt.visualize)
            # Apply NMS
            pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, classes=self.opt.classes, agnostic=self.opt.agnostic_nms, max_det=self.opt.max_det)
            info_show = ""
            # Process detections
            annotator = Annotator(img, line_width=self.opt.line_thickness, example=str(self.names))
            for i, det in enumerate(pred):
                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], showimg.shape).round()
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)
                        print(c)
                        label = None if self.opt.hide_labels else (self.names[c] if self.opt.hide_conf else f'{self.names[c]} {conf:.2f}')
                        name_list.append(self.names[int(cls)])
                        single_info = plot_one_box2(xyxy, showimg, label=label, color=self.colors[int(cls)], line_thickness=2)
                        print(single_info)
                        info_show = info_show + single_info + "\n"
    # 模型选择函数                  
    def seletModels(self):
        self.openfile_name_model, _ = QFileDialog.getOpenFileName(self.btn_selet_model, '选择weights文件', '.', '权重文件(*.pt)')
        if not self.openfile_name_model:
            QMessageBox.warning(self, "Warning:", "打开权重失败", buttons=QMessageBox.Ok,)
        else:
            print('加载weights文件地址为：' + str(self.openfile_name_model))
            QMessageBox.information(self, u"Notice", u"权重打开成功", buttons=QtWidgets.QMessageBox.Ok)
            
    # 模型初始化函数        
    def initModels(self):
        # 模型相关参数配置
        parser = argparse.ArgumentParser()
        parser.add_argument('--weights', nargs='+', type=str, default='runs/train/exp/weights/best.pt', help='model path(s)')
        parser.add_argument('--source', type=str, default='data/applenew5/images/test/', help='file/dir/URL/glob, 0 for webcam')
        parser.add_argument('--data', type=str, default='data/coco128.yaml', help='(optional) dataset.yaml path')
        parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=640, help='inference size h,w')
        parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
        parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
        parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
        parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
        parser.add_argument('--view-img', action='store_true', help='show results')
        parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
        parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
        parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
        parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
        parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
        parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
        parser.add_argument('--augment', action='store_true', help='augmented inference')
        parser.add_argument('--visualize', action='store_true', help='visualize features')
        parser.add_argument('--update', action='store_true', help='update all models')
        parser.add_argument('--project', default='runs/detect', help='save results to project/name')
        parser.add_argument('--name', default='exp', help='save results to project/name')
        parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
        parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
        parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
        parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
        parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
        parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
        self.opt = parser.parse_args()
        print(self.opt)
        # 默认使用opt中的设置（权重等）来对模型进行初始化
        source, weights, view_img, save_txt, imgsz, half, data, dnn, visualize, max_det = \
            self.opt.source, self.opt.weights, self.opt.view_img, self.opt.save_txt, self.opt.imgsz, self.opt.half, self.opt.data, self.opt.dnn, self.opt.visualize, self.opt.max_det
        # 若openfile_name_model不为空，则使用此权重进行初始化
        if self.openfile_name_model:
            weights = self.openfile_name_model
            print("Using button choose model")
        self.device = select_device(self.opt.device)
        cudnn.benchmark = True
        # Load model
        self.model = DetectMultiBackend(weights, device=self.device, dnn=self.opt.dnn, data=self.opt.data, fp16=half)
        stride = self.model.stride # model stride
        self.imgsz = check_img_size(imgsz, s=stride)  # check img_size
        # Get names and colors
        self.names = self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
        print("model initial done")
        # 设置提示框
        QtWidgets.QMessageBox.information(self, u"Notice", u"模型加载完成", buttons=QtWidgets.QMessageBox.Ok,
                                      defaultButton=QtWidgets.QMessageBox.Ok)
    # 图像选择函数
    def openImage(self):
        print('openImage')
        name_list = []
        fname, _ = QFileDialog.getOpenFileName(self, '打开文件', '.', '图像文件(*.jpg)')
        print(fname)
        # if not fname:
        #     QMessageBox.warning(self, u"Warning", u"打开图片失败", buttons=QMessageBox.Ok)
        # else:
        self.label_show_yuanshi.setPixmap(QPixmap(fname))
        self.label_show_yuanshi.setScaledContents(True)
        img = cv2.imread(fname)
        print(img)
        print("model initial done21")
        self.detectImage(name_list, img)
        info_show = self.detectImage(name_list, img)
        print(info_show)
        # 检测结果显示在界面
        print("model initial done23")
        self.result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        self.result = cv2.resize(self.result, (1000, 1000), interpolation=cv2.INTER_AREA)
        self.QtImg = QImage(self.result.data, self.result.shape[1], self.result.shape[0], QImage.Format_RGB32)
        self.qImg = self.QtImg
        self.label_show_jieguo.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))
        print(self.label_show_jieguo)
        self.label_show_jieguo.setScaledContents(True)  # 设置图像自适应界面大小
        return self.qImg
        
    # 图像保存函数
    def saveImage(self):
        fd, _ = QFileDialog.getSaveFileName(self, "保存图片", ".", "*.jpg")
        self.qImg.save(fd)
        
    # 图像清除函数
    def clearImage(self, stopp):
        result = QMessageBox.question(self, "Warning:", "是否清除本次检测结果", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if result == QMessageBox.Yes:
            self.label_show_yuanshi.clear()
            self.label_show_jieguo.clear()
        else:
            stopp.ignore()
            
    # 应用退出函数
    def exitApp(self, event):
        event = QApplication.instance()
        result = QMessageBox.question(self, "Notice:", "您真的要退出此应用吗", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if result == QMessageBox.Yes:
            event.quit()
        else:
            event.ignore()
            
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_selet_model.setText(_translate("MainWindow", "最优模型选择"))
        self.label_show_yuanshi.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">原始图像</span></p></body></html>"))
        self.btn_init_model.setText(_translate("MainWindow", "模型初始化"))
        self.btn_detect_img.setText(_translate("MainWindow", "选择检测图像"))
        self.btn_save_img.setText(_translate("MainWindow", "保存结果图像"))
        self.btn_clear_img.setText(_translate("MainWindow", "清除结果图像"))
        self.btn_exit_app.setText(_translate("MainWindow", "退出应用"))
        self.label_show_jieguo.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt;\">结果图像</span></p></body></html>"))
        self.label_show_title.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:26pt; color:#ffffff;\">基于YOLOv5的识别检测演示软件</span></p></body></html>"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())
