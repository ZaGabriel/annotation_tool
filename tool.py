from PyQt5 import QtWidgets, QtGui, QtCore
import cv2
import sys
import threading, time

WINDOW_SIZE_WIDTH = 1280
WINDOW_SIZE_HEIGHT = 720

IMAGE_MAX_WIDTH = 1000
IMAGE_MAX_HEIGHT = 500
IMAGE_X0 = int(WINDOW_SIZE_WIDTH / 2 - IMAGE_MAX_WIDTH / 2)
IMAGE_Y0 = 50

class Thread(QtCore.QThread):
    # Frame signal for sending back
    frame_signal = QtCore.pyqtSignal(QtGui.QImage)
    # Image info for sending back
    img_info_signal = QtCore.pyqtSignal(tuple)

    def run(self):
        self.stopSignal = False
        cap = cv2.VideoCapture(self.source)
        while cap.isOpened():
            # If STOP send blank image and break
            if self.stopSignal:
                self.frame_signal.emit(QtGui.QImage())
                break

            ret, frame = cap.read()
            if not ret:
                cap = cv2.VideoCapture(self.source) # Reconnect
                continue

            # Convery to Qt format
            frame = self.img2qimg(frame)

            # Send back image and image info
            self.frame_signal.emit(frame)
            self.img_info_signal.emit((self.img_shape_before, self.img_xywh))

    def stop(self):
        self.stopSignal = True

    def img2qimg(self, img):
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

        # Save img parameter
        self.img_shape_before = (h, w, scaler)
        self.img_xywh = (int(IMAGE_MAX_WIDTH/2 - new_w/2 + IMAGE_X0), IMAGE_Y0, new_w, new_h)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (new_w, new_h))

        # Convert to QImage format
        qimg = QtGui.QImage(img, new_w, new_h, new_w*ch, QtGui.QImage.Format_RGB888)
        return qimg

    def setSource(self, source):
        self.source = source
        cap = cv2.VideoCapture(self.source)
        ret = cap.isOpened()
        cap.release()
        return ret

class BoundingBoxLabel(QtWidgets.QLabel):
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

class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('tool')
        self.resize(WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT)
        self.ui_text()
        self.ui_btn()
        self.ui_img()
        self.parameter_init()

        # Stream thread
        self.stream_thread = Thread()
        self.stream_thread.frame_signal.connect(self.setFrame)
        self.stream_thread.img_info_signal.connect(self.setImgInfo)
        
    def parameter_init(self):
        self.ocv = True
        self.parameter_person_init()
        self.parameter_motor_init()
        self.parameter_car_init()
        

    def parameter_person_init(self):
        self.btnPersonEnable = False
        self.btn_person.setDisabled(True)
        self.boundingBox.paintPerson = False
        self.person_screen_xyxy = [0] * 4
        self.person_screen_xywh = [0] * 4
        self.person_img_xyxy = [0] * 4
        self.person_img_xywh = [0] * 4
        self.label_person_xyxy.setText(f'xyxy : {self.person_img_xyxy}')
        self.label_person_xywh.setText(f'xywh : {self.person_img_xywh}')
        self.update()
    
    def parameter_motor_init(self):
        self.btnMotorEnable = False
        self.btn_motor.setDisabled(True)
        self.boundingBox.paintMotor = False
        self.motor_screen_xyxy = [0] * 4
        self.motor_screen_xywh = [0] * 4
        self.motor_img_xyxy = [0] * 4
        self.motor_img_xywh = [0] * 4
        self.label_motor_xyxy.setText(f'xyxy : {self.motor_img_xyxy}')
        self.label_motor_xywh.setText(f'xywh : {self.motor_img_xywh}')
        self.update()
    
    def parameter_car_init(self):
        self.btnCarEnable = False
        self.btn_car.setDisabled(True)
        self.boundingBox.paintCar = False
        self.car_screen_xyxy = [0] * 4
        self.car_screen_xywh = [0] * 4
        self.car_img_xyxy = [0] * 4
        self.car_img_xywh = [0] * 4
        self.label_car_xyxy.setText(f'xyxy : {self.car_img_xyxy}')
        self.label_car_xywh.setText(f'xywh : {self.car_img_xywh}')
        self.update()

    def ui_text(self):
        # Person
        self.label_person_xyxy = QtWidgets.QLabel(self)
        self.label_person_xyxy.setStyleSheet('font-size:12px;')
        self.label_person_xyxy.setGeometry(400, 610, 230, 20)
        self.label_person_xyxy.setAlignment(QtCore.Qt.AlignCenter)

        self.label_person_xywh = QtWidgets.QLabel(self)
        self.label_person_xywh.setStyleSheet('font-size:12px;')
        self.label_person_xywh.setGeometry(400, 630, 230, 20)
        self.label_person_xywh.setAlignment(QtCore.Qt.AlignCenter)

        # Motor
        self.label_motor_xyxy = QtWidgets.QLabel(self)
        self.label_motor_xyxy.setStyleSheet('font-size:12px;')
        self.label_motor_xyxy.setGeometry(650, 610, 230, 20)
        self.label_motor_xyxy.setAlignment(QtCore.Qt.AlignCenter)

        self.label_motor_xywh = QtWidgets.QLabel(self)
        self.label_motor_xywh.setStyleSheet('font-size:12px;')
        self.label_motor_xywh.setGeometry(650, 630, 230, 20)
        self.label_motor_xywh.setAlignment(QtCore.Qt.AlignCenter)

        # Car
        self.label_car_xyxy = QtWidgets.QLabel(self)
        self.label_car_xyxy.setStyleSheet('font-size:12px;')
        self.label_car_xyxy.setGeometry(900, 610, 230, 20)
        self.label_car_xyxy.setAlignment(QtCore.Qt.AlignCenter)

        self.label_car_xywh = QtWidgets.QLabel(self)
        self.label_car_xywh.setStyleSheet('font-size:12px;')
        self.label_car_xywh.setGeometry(900, 630, 230, 20)
        self.label_car_xywh.setAlignment(QtCore.Qt.AlignCenter)


    def ui_img(self):
        self.img_box = QtWidgets.QWidget(self)
        self.img_box.setGeometry(IMAGE_X0-20, IMAGE_Y0-20, IMAGE_MAX_WIDTH+40, IMAGE_MAX_HEIGHT+40)
        self.img_layout = QtWidgets.QGridLayout(self.img_box)

        self.label_img = QtWidgets.QLabel(self)
        self.label_img.setAlignment(QtCore.Qt.AlignCenter)

        self.boundingBox = BoundingBoxLabel(self)

        self.img_layout.addWidget(self.label_img, 0, 0)
        self.img_layout.addWidget(self.boundingBox, 0, 0)
        
        
    def ui_btn(self):
        # Vertical Layout
        self.btn_vbox = QtWidgets.QWidget(self)
        self.btn_vbox.setGeometry(150,539,250,200)
        self.btn_vlayout = QtWidgets.QVBoxLayout(self.btn_vbox)
        self.btn_vlayout.setAlignment(QtCore.Qt.AlignVCenter)

        # Stream input
        self.input_stream = QtWidgets.QLineEdit(self)
        self.btn_vlayout.addWidget(self.input_stream)

        # Open Stream
        self.btn_open_stream = QtWidgets.QPushButton(self)
        self.btn_open_stream.setText("Open Stream")
        self.btn_open_stream.clicked.connect(self.btnOpenStreamEvent)
        self.btn_vlayout.addWidget(self.btn_open_stream)

        # Open Image
        self.btn_open_img = QtWidgets.QPushButton(self)
        self.btn_open_img.setText("Open Image")
        self.btn_open_img.clicked.connect(self.btnOpenImageEvent)
        self.btn_vlayout.addWidget(self.btn_open_img)

        # Save
        self.btn_save = QtWidgets.QPushButton(self)
        self.btn_save.setText("Save")
        self.btn_save.clicked.connect(self.btnSaveEvent)
        self.btn_vlayout.addWidget(self.btn_save)
        self.btn_save.setDisabled(True)

        # Horizonal Layout
        self.btn_hbox = QtWidgets.QWidget(self)
        self.btn_hbox.setGeometry(390,570,750,50)
        self.btn_hlayout = QtWidgets.QHBoxLayout(self.btn_hbox)
        self.btn_hlayout.setAlignment(QtCore.Qt.AlignVCenter)

        # Person
        self.btn_person = QtWidgets.QPushButton(self)
        self.btn_person.setText("Person")
        self.btn_person.clicked.connect(self.btnPersonEvent)
        self.btn_hlayout.addWidget(self.btn_person)

        # Motor
        self.btn_motor = QtWidgets.QPushButton(self)
        self.btn_motor.setText("Motorcycle")
        self.btn_motor.clicked.connect(self.btnMotorEvent)
        self.btn_hlayout.addWidget(self.btn_motor)

        # Car
        self.btn_car = QtWidgets.QPushButton(self)
        self.btn_car.setText("Car")
        self.btn_car.clicked.connect(self.btnCarEvent)
        self.btn_hlayout.addWidget(self.btn_car)

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
        h_r, w_r, scaler = self.img_shape_before
        
        # Constraint for mouse position range
        mouse_x = min(max(mouse_x, x), x + w)
        mouse_y = min(max(mouse_y, y), y + h)

        img_x = int((mouse_x - x) / scaler)
        img_y = int((mouse_y - y) / scaler)

        # Constraint for original image range
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
                xy = [event.x(), event.y()]
                self.person_screen_xyxy[0:2] = xy
                self.person_img_xyxy[0:2] = self.caculateXY(xy)

            if self.btnMotorEnable:
                # mouse position on screen
                xy = [event.x(), event.y()]
                self.motor_screen_xyxy[0:2] = xy
                self.motor_img_xyxy[0:2] = self.caculateXY(xy)

            if self.btnCarEnable:
                # mouse position on screen
                xy = [event.x(), event.y()]
                self.car_screen_xyxy[0:2] = xy
                self.car_img_xyxy[0:2] = self.caculateXY(xy)
            
    def mouseReleaseEvent(self, event):
        if event.button() == 1 and self.label_img.pixmap() is not None:
            if self.btnPersonEnable:
                xy = [event.x(), event.y()]
                
                # Save mouse position for drawing bounding box on screen
                self.person_screen_xyxy[2:4] = xy

                # Convert mouse position to image position
                self.person_img_xyxy[2:4] = self.caculateXY(xy)
                
                self.person_img_xywh = self.xyxy2xywh(self.person_img_xyxy)
                
                self.label_person_xyxy.setText(f'xyxy : {self.person_img_xyxy}')
                self.label_person_xywh.setText(f'xywh : {self.person_img_xywh}')

                self.btnPersonEnable = False
                self.btn_person.setDisabled(False)

                # Add layout offset
                self.person_screen_xyxy = [ self.person_screen_xyxy[0]-IMAGE_X0+10,
                                            self.person_screen_xyxy[1]-IMAGE_Y0+10,
                                            self.person_screen_xyxy[2]-IMAGE_X0+10,
                                            self.person_screen_xyxy[3]-IMAGE_Y0+10]
                
                self.person_screen_xywh = self.xyxy2xywh(self.person_screen_xyxy)
                self.boundingBox.setPersonParameter(self.person_screen_xywh)
                self.boundingBox.paintPerson = True
                self.boundingBox.update()
                self.btn_save.setDisabled(False)

            if self.btnMotorEnable:
                xy = [event.x(), event.y()]

                # Save mouse position for drawing bounding box on screen
                self.motor_screen_xyxy[2:4] = xy

                # Convert mouse position to image position
                self.motor_img_xyxy[2:4] = self.caculateXY(xy)
                
                self.motor_img_xywh = self.xyxy2xywh(self.motor_img_xyxy)
                
                self.label_motor_xyxy.setText(f'xyxy : {self.motor_img_xyxy}')
                self.label_motor_xywh.setText(f'xywh : {self.motor_img_xywh}')

                self.btnMotorEnable = False
                self.btn_motor.setDisabled(False)

                # Add layout offset
                self.motor_screen_xyxy = [ self.motor_screen_xyxy[0]-IMAGE_X0+10,
                                            self.motor_screen_xyxy[1]-IMAGE_Y0+10,
                                            self.motor_screen_xyxy[2]-IMAGE_X0+10,
                                            self.motor_screen_xyxy[3]-IMAGE_Y0+10]
                
                self.motor_screen_xywh = self.xyxy2xywh(self.motor_screen_xyxy)
                self.boundingBox.setMotorParameter(self.motor_screen_xywh)
                self.boundingBox.paintMotor = True
                self.boundingBox.update()
                self.btn_save.setDisabled(False)

            if self.btnCarEnable:
                xy = [event.x(), event.y()]

                # Save mouse position for drawing bounding box on screen
                self.car_screen_xyxy[2:4] = xy

                # Convert mouse position to image position
                self.car_img_xyxy[2:4] = self.caculateXY(xy)
                
                self.car_img_xywh = self.xyxy2xywh(self.car_img_xyxy)
                
                self.label_car_xyxy.setText(f'xyxy : {self.car_img_xyxy}')
                self.label_car_xywh.setText(f'xywh : {self.car_img_xywh}')

                self.btnCarEnable = False
                self.btn_car.setDisabled(False)

                # Add layout offset
                self.car_screen_xyxy = [ self.car_screen_xyxy[0]-IMAGE_X0+10,
                                            self.car_screen_xyxy[1]-IMAGE_Y0+10,
                                            self.car_screen_xyxy[2]-IMAGE_X0+10,
                                            self.car_screen_xyxy[3]-IMAGE_Y0+10]
                
                self.car_screen_xywh = self.xyxy2xywh(self.car_screen_xyxy)
                self.boundingBox.setCarParameter(self.car_screen_xywh)
                self.boundingBox.paintCar = True
                self.boundingBox.update()
                self.btn_save.setDisabled(False)

    @QtCore.pyqtSlot(QtGui.QImage)
    def setFrame(self, frame):
        self.label_img.setPixmap(QtGui.QPixmap(IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT).fromImage(frame))

    @QtCore.pyqtSlot(tuple)
    def setImgInfo(self, img_info):
        self.img_shape_before, self.img_xywh = img_info

    def btnOpenStreamEvent(self):
        # Clear label
        self.label_img.clear()
        
        # Set video source
        ret = self.stream_thread.setSource(self.input_stream.text())
        if not ret:
            self.stream_thread.stop()
            return

        # init parameters
        self.parameter_init()

        # Enable button 
        self.btn_save.setDisabled(False)
        self.btn_person.setDisabled(False)
        self.btn_motor.setDisabled(False)
        self.btn_car.setDisabled(False)

        # Start/Stop stream thread
        if self.stream_thread.isRunning():
            self.stream_thread.stop()
        else:
            self.stream_thread.start()

    def img2qimg(self, img):
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

        # Save img parameter
        self.img_shape_before = (h, w, scaler)
        self.img_xywh = (int(IMAGE_MAX_WIDTH/2 - new_w/2 + IMAGE_X0), IMAGE_Y0, new_w, new_h)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (new_w, new_h))

        # Convert to Qlabel format
        qimg = QtGui.QImage(img, new_w, new_h, new_w*ch, QtGui.QImage.Format_RGB888)
        return qimg

    # Button Event
    def btnOpenImageEvent(self):
        # Stop video stream
        if self.stream_thread.isRunning():
            self.stream_thread.stop()

        # Open file exploer
        self.filePath , _ = \
            QtWidgets.QFileDialog.getOpenFileName(filter="Image Files (*.jpg *.png *.jpeg)")
            
        if self.filePath == '' :
            return

        # Read image
        img = cv2.imread(self.filePath)

        # Convert to Qt format
        qimg = self.img2qimg(img)

        # Show image on label
        self.label_img.setPixmap(QtGui.QPixmap(IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT).fromImage(qimg))

        # init parameters
        self.parameter_init()
        
        # Enable button 
        self.btn_save.setDisabled(False)
        self.btn_person.setDisabled(False)
        self.btn_motor.setDisabled(False)
        self.btn_car.setDisabled(False)

    def btnPersonEvent(self):
        self.parameter_person_init()
        self.btnPersonEnable = True
        self.btn_save.setDisabled(True)
        

    def btnMotorEvent(self):
        self.parameter_motor_init()
        self.btnMotorEnable = True
        self.btn_save.setDisabled(True)

    def btnCarEvent(self):
        self.parameter_car_init()
        self.btnCarEnable = True
        self.btn_save.setDisabled(True)

    def btnSaveEvent(self):
        with open("detect_area.cfg", "w") as f:
            f.writelines(f"{' '.join(str(i) for i in self.person_img_xywh)}\n")
            f.writelines(f"{' '.join(str(i) for i in self.motor_img_xywh)}\n")
            f.writelines(f"{' '.join(str(i) for i in self.car_img_xywh)}\n")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Form = App()
    Form.show()
    sys.exit(app.exec_())