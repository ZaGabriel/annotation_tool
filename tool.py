from PyQt5 import QtWidgets, QtGui, QtCore
import cv2
import sys

WINDOW_SIZE_WIDTH = 1280
WINDOW_SIZE_HEIGHT = 720

IMAGE_MAX_WIDTH = 1000
IMAGE_MAX_HEIGHT = 500
IMAGE_X0 = int(WINDOW_SIZE_WIDTH / 2 - IMAGE_MAX_WIDTH / 2)
IMAGE_Y0 = 50

class MyLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.paintPerson = False
        self.paintMotor = False
        self.paintCar = False

    def setPersonParameter(self, xywh):
        self.person_x, self.person_y, self.person_w, self.person_h = xywh

    def setMotorParameter(self, xywh):
        self.motor_x, self.motor_y, self.motor_w, self.motor_h = xywh

    def setCarParameter(self, xywh):
        self.car_x, self.car_y, self.car_w, self.car_h = xywh

    def paintEvent(self, event):
        qpainter = QtGui.QPainter()
        qpainter.begin(self)

        if self.paintPerson:
            qpainter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 4))
            qpainter.drawRect(self.person_x, self.person_y, self.person_w, self.person_h)
        if self.paintMotor:
            qpainter.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0), 4))
            qpainter.drawRect(self.motor_x, self.motor_y, self.motor_w, self.motor_h)
        if self.paintCar:
            qpainter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 255), 4))
            qpainter.drawRect(self.car_x, self.car_y, self.car_w, self.car_h)

        qpainter.end()

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('tool')
        self.resize(WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT)
        self.ui_text()
        self.ui_btn()
        self.ui_img()
        self.setMouseTracking(True)
        self.btnPersonEnable = False
        self.btnMotorEnable = False
        self.btnCarEnable = False
        self.person_x, self.person_y, self.person_w, self.person_h = None, None, None, None
        self.motor_x, self.motor_y, self.motor_w, self.motor_h = None, None, None, None
        self.car_x, self.car_y, self.car_w, self.car_h = None, None, None, None

    def ui_text(self):
        # Person
        self.label_person_xyxy = QtWidgets.QLabel(self)
        self.label_person_xyxy.setStyleSheet('font-size:12px;')
        self.label_person_xyxy.setGeometry(400, 590, 230, 20)
        self.label_person_xyxy.setAlignment(QtCore.Qt.AlignCenter)

        self.label_person_xywh = QtWidgets.QLabel(self)
        self.label_person_xywh.setStyleSheet('font-size:12px;')
        self.label_person_xywh.setGeometry(400, 610, 230, 20)
        self.label_person_xywh.setAlignment(QtCore.Qt.AlignCenter)

        # Motor
        self.label_motor_xyxy = QtWidgets.QLabel(self)
        self.label_motor_xyxy.setStyleSheet('font-size:12px;')
        self.label_motor_xyxy.setGeometry(650, 590, 230, 20)
        self.label_motor_xyxy.setAlignment(QtCore.Qt.AlignCenter)

        self.label_motor_xywh = QtWidgets.QLabel(self)
        self.label_motor_xywh.setStyleSheet('font-size:12px;')
        self.label_motor_xywh.setGeometry(650, 610, 230, 20)
        self.label_motor_xywh.setAlignment(QtCore.Qt.AlignCenter)

        # Car
        self.label_car_xyxy = QtWidgets.QLabel(self)
        self.label_car_xyxy.setStyleSheet('font-size:12px;')
        self.label_car_xyxy.setGeometry(900, 590, 230, 20)
        self.label_car_xyxy.setAlignment(QtCore.Qt.AlignCenter)

        self.label_car_xywh = QtWidgets.QLabel(self)
        self.label_car_xywh.setStyleSheet('font-size:12px;')
        self.label_car_xywh.setGeometry(900, 610, 230, 20)
        self.label_car_xywh.setAlignment(QtCore.Qt.AlignCenter)


    def ui_img(self):
        self.img_box = QtWidgets.QWidget(self)
        self.img_box.setGeometry(IMAGE_X0-20, IMAGE_Y0-20, IMAGE_MAX_WIDTH+40, IMAGE_MAX_HEIGHT+40)
        self.img_layout = QtWidgets.QGridLayout(self.img_box)

        self.label_img = QtWidgets.QLabel(self)
        self.label_img.setAlignment(QtCore.Qt.AlignCenter)

        self.boundingBox = MyLabel(self)

        self.img_layout.addWidget(self.label_img, 0, 0)
        self.img_layout.addWidget(self.boundingBox, 0, 0)
        
        
    def ui_btn(self):
        # Horizonal Layout
        self.btn_box = QtWidgets.QWidget(self)
        self.btn_box.setGeometry(140,620,1000,50)
        self.btn_layout = QtWidgets.QHBoxLayout(self.btn_box)
        self.btn_layout.setAlignment(QtCore.Qt.AlignVCenter)

        # Open Image
        self.btn_open = QtWidgets.QPushButton(self)
        self.btn_open.setText("Open")
        self.btn_open.clicked.connect(self.btnOpenEvent)
        self.btn_layout.addWidget(self.btn_open)

        # Save
        self.btn_save = QtWidgets.QPushButton(self)
        self.btn_save.setText("Save")
        self.btn_save.clicked.connect(self.btnSaveEvent)
        self.btn_save.setGeometry(150, 665, 240, 25)
        self.btn_save.setDisabled(True)

        # Person
        self.btn_person = QtWidgets.QPushButton(self)
        self.btn_person.setText("Person")
        self.btn_person.clicked.connect(self.btnPersonEvent)
        self.btn_layout.addWidget(self.btn_person)

        # Motor
        self.btn_motor = QtWidgets.QPushButton(self)
        self.btn_motor.setText("Motorcycle")
        self.btn_motor.clicked.connect(self.btnMotorEvent)
        self.btn_layout.addWidget(self.btn_motor)

        # Car
        self.btn_car = QtWidgets.QPushButton(self)
        self.btn_car.setText("Car")
        self.btn_car.clicked.connect(self.btnCarEvent)
        self.btn_layout.addWidget(self.btn_car)

    # Paint Margin for Image
    def paintEvent(self, event):
        qpainter = QtGui.QPainter()
        qpainter.begin(self)

        # Margin for image
        qpainter.setPen(QtGui.QPen(QtGui.QColor('#0'), 4))
        qpainter.drawRect(IMAGE_X0-2, IMAGE_Y0-2, IMAGE_MAX_WIDTH+4, IMAGE_MAX_HEIGHT+4)

        qpainter.end()

    # Transfer mouse XY to original image XY
    def caculateXY(self, mouse_xy):
        mouse_x, mouse_y = mouse_xy

        x, y, w, h = self.img_xywh
        w_r, h_r, scaler = self.img_shape_before

        # constraint for mouse position range
        mouse_x = min(max(mouse_x, x), x + w)
        mouse_y = min(max(mouse_y, y), y + h)

        img_x = int((mouse_x - x) / scaler)
        img_y = int((mouse_y - y) / scaler)

        # constraint for original image range
        img_x = max(min(img_x, w_r), 0)
        img_y = max(min(img_y, h_r), 0)

        return [img_x, img_y]
    
    def xyxy2xywh(self, xyxy):
        x1, y1, x2, y2 = xyxy
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x1 - x2), abs(y1 - y2)
        return [x, y, w, h]

    # Mouse Event
    def mousePressEvent(self, event):
        if event.button() == 1 and self.label_img.pixmap() is not None:
            if self.btnPersonEnable:
                # mouse position on screen
                self.person_screen_xyxy[0:2] = (event.x(), event.y())
                self.person_img_xyxy[0:2] = self.caculateXY((event.x(), event.y()))

            if self.btnMotorEnable:
                self.img_motor_x1, self.img_motor_y1 = event.x()-IMAGE_X0, event.y()-IMAGE_Y0
                self.motor_x1, self.motor_y1 = self.caculateXY(event.x(), event.y())

            if self.btnCarEnable:
                self.img_car_x1, self.img_car_y1 = event.x()-IMAGE_X0, event.y()-IMAGE_Y0
                self.car_x1, self.car_y1 = self.caculateXY(event.x(), event.y())

    
    def mouseReleaseEvent(self, event):
        if event.button() == 1 and self.label_img.pixmap() is not None:
            if self.btnPersonEnable:
                # Convert mouse position to image position
                self.person_img_xyxy[2:4] = self.caculateXY((event.x(), event.y()))
                
                self.person_img_xywh = self.xyxy2xywh(self.person_img_xyxy)
                
                self.label_person_xyxy.setText(f'xyxy : {self.person_img_xyxy}')
                self.label_person_xywh.setText(f'xywh : {self.person_img_xywh}')

                self.btnPersonEnable = False
                self.btn_person.setDisabled(False)

                # Save mouse position for drawing bounding box on screen
                self.person_screen_xyxy[2:4] = (event.x(), event.y())

                # Add offset
                self.person_screen_xyxy = ( self.person_screen_xyxy[0]-IMAGE_X0+10,
                                            self.person_screen_xyxy[1]-IMAGE_Y0+10,
                                            self.person_screen_xyxy[2]-IMAGE_X0+10,
                                            self.person_screen_xyxy[3]-IMAGE_Y0+10)
                
                self.person_screen_xywh = self.xyxy2xywh(self.person_screen_xyxy)
                self.boundingBox.setPersonParameter(self.person_screen_xywh)
                self.boundingBox.paintPerson = True
                self.boundingBox.update()

            if self.btnMotorEnable:
                self.img_motor_x2, self.img_motor_y2 = event.x()-IMAGE_X0, event.y()-IMAGE_Y0
                self.motor_x2, self.motor_y2 = self.caculateXY(event.x(), event.y())
                self.motor_x, self.motor_y, self.motor_w, self.motor_h = \
                    self.xyxy2xywh(self.motor_x1, self.motor_y1, self.motor_x2, self.motor_y2)

                self.label_motor_xyxy.setText(f'xyxy : ({self.motor_x1}, {self.motor_y1}), ({self.motor_x2}, {self.motor_y2})')
                self.label_motor_xywh.setText(f'xywh : {self.motor_x}, {self.motor_y}, {self.motor_w}, {self.motor_h}')
                
                self.btnMotorEnable = False
                self.btn_motor.setDisabled(False)

                xywh = self.xyxy2xywh(self.img_motor_x1+10, self.img_motor_y1+10, self.img_motor_x2+10, self.img_motor_y2+10)
                self.boundingBox.setMotorParameter(xywh)
                self.boundingBox.paintMotor = True
                self.boundingBox.update()

            if self.btnCarEnable:
                self.img_car_x2, self.img_car_y2 = event.x()-IMAGE_X0, event.y()-IMAGE_Y0
                self.car_x2, self.car_y2 = self.caculateXY(event.x(), event.y())
                self.car_x, self.car_y, self.car_w, self.car_h = \
                    self.xyxy2xywh(self.car_x1, self.car_y1, self.car_x2, self.car_y2)

                self.label_car_xyxy.setText(f'xyxy : ({self.car_x1}, {self.car_y1}), ({self.car_x2}, {self.car_y2})')
                self.label_car_xywh.setText(f'xywh : {self.car_x}, {self.car_y}, {self.car_w}, {self.car_h}')

                self.btnCarEnable = False
                self.btn_car.setDisabled(False)

                xywh = self.xyxy2xywh(self.img_car_x1+10, self.img_car_y1+10, self.img_car_x2+10, self.img_car_y2+10)
                self.boundingBox.setCarParameter(xywh)
                self.boundingBox.paintCar = True
                self.boundingBox.update()

            if self.checkNotEmpty():
                self.btn_save.setDisabled(False)

    def checkNotEmpty(self):
        if self.person_x is not None and self.person_y is not None and self.person_w is not None and self.person_h and \
            self.motor_x is not None and self.motor_y is not None and self.motor_w is not None and self.motor_h and \
            self.car_x is not None and self.car_y is not None and self.car_w is not None and self.car_h:

            return True
        else:
            return False
        
    # Button Event
    def btnOpenEvent(self):
        # Open file exploer
        self.filePath , _ = \
            QtWidgets.QFileDialog.getOpenFileName(filter="Image Files (*.jpg *.png *.jpeg)")
            
        if self.filePath == '' :
            return

        # Read image
        img = cv2.imread(self.filePath)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape   
        
        # Caculate resize scale
        if w/h > IMAGE_MAX_WIDTH/IMAGE_MAX_HEIGHT:
            scaler = IMAGE_MAX_WIDTH / w
            new_w = int(w * scaler)
            new_h = int(h * scaler)
        else :
            scaler = IMAGE_MAX_HEIGHT / h
            new_w = int(w * scaler)
            new_h = int(h * scaler)

        img = cv2.resize(img, (new_w, new_h))

        # Show image on label
        qimg = QtGui.QImage(img, new_w, new_h, new_w*ch, QtGui.QImage.Format_RGB888)
        canvas = QtGui.QPixmap(IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT).fromImage(qimg)
        self.label_img.setPixmap(canvas)

        self.img_shape_before = (h, w, scaler)
        self.img_xywh = (int(IMAGE_MAX_WIDTH/2 - new_w/2 + IMAGE_X0), IMAGE_Y0, new_w, new_h)

        # Disable save button 
        self.btn_save.setDisabled(True)

    def btnPersonEvent(self):
        self.btnPersonEnable = True
        self.btn_save.setDisabled(True)
        self.btn_person.setDisabled(True)

        self.label_person_xyxy.setText('')
        self.label_person_xywh.setText('')

        self.person_screen_xyxy = [0] * 4
        self.person_img_xyxy = [0] * 4

        # clear showed bounding box
        self.boundingBox.paintPerson = False
        self.boundingBox.update()

    def btnMotorEvent(self):
        self.btnMotorEnable = True
        self.btn_save.setDisabled(True)
        self.btn_motor.setDisabled(True)

        self.label_motor_xyxy.setText('')
        self.label_motor_xywh.setText('')
        
        # clear showed bounding box
        self.boundingBox.paintMotor = False
        self.boundingBox.update()

    def btnCarEvent(self):
        self.btnCarEnable = True
        self.btn_save.setDisabled(True)
        self.btn_car.setDisabled(True)

        self.label_car_xyxy.setText('')
        self.label_car_xywh.setText('')

        self.boundingBox.paintCar = False
        self.boundingBox.update()

    def btnSaveEvent(self):
        with open("detect_area.cfg", "w") as f:
            f.writelines(*self.person_img_xywh)
            f.writelines(f'{self.motor_x} {self.motor_y} {self.motor_w} {self.motor_h}\n')
            f.writelines(f'{self.car_x} {self.car_y} {self.car_w} {self.car_h}\n')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Form = MyWidget()
    Form.show()
    sys.exit(app.exec_())