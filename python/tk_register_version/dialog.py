import os
from tank.platform.qt import QtGui, QtCore

def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    win = app_instance.engine.show_dialog("Register Versions", app_instance, Window)
    return win

class Window(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        
        #Custom code here
        self.resize(750,100)
        
        #Creating Layout
        mainLayout = QtGui.QVBoxLayout(self)
        Layout_01 = QtGui.QGridLayout(self)
        Layout_02 = QtGui.QGridLayout(self)
        horBoxLayout = QtGui.QHBoxLayout()
        
        #Connect the Layouts
        mainLayout.addLayout(Layout_01)
        mainLayout.addLayout(Layout_02)
        
        #Widgets
        self.project_txt = QtGui.QLabel("Project:")
        self.project_field = QtGui.QTextEdit()
        self.project_field.setMaximumSize(5000, 25)

        self.asset_type_txt = QtGui.QLabel("Asset Type:")
        self.asset_type_field = QtGui.QTextEdit()
        self.asset_type_field.setMaximumSize(5000, 25)

        self.asset_txt = QtGui.QLabel("Asset:")
        self.asset_field = QtGui.QTextEdit()
        self.asset_field.setMaximumSize(5000, 25)

        self.task_txt = QtGui.QLabel("Task:")
        self.task_field = QtGui.QTextEdit()
        self.task_field.setMaximumSize(5000, 25)

        self.trg_file_txt = QtGui.QPushButton("Target Version Path:")
        self.trg_file_field = QtGui.QTextEdit()
        self.trg_file_field.setMaximumSize(5000, 25)

        self.trg_publish_file_txt = QtGui.QPushButton("Target Publish Path:")
        self.trg_publish_file_field = QtGui.QTextEdit()
        self.trg_publish_file_field.setMaximumSize(5000, 25)

        self.loadVersionFile_button = QtGui.QPushButton("Load Version")
        self.loadPublishFile_button = QtGui.QPushButton("Load Publish")

        self.versionUpFile_button = QtGui.QPushButton("Version+")
        
        self.apps_txt = QtGui.QLabel("Apps Used:")
        self.apps_combobox = QtGui.QComboBox()
        self.apps_combobox.addItem("None")
        
        self.publishFile_button = QtGui.QPushButton("Publish")
        
        #adding widgets
        Layout_01.addWidget(self.project_txt, 0, 0)
        Layout_01.addWidget(self.project_field, 0 , 1)

        Layout_01.addWidget(self.asset_type_txt, 1 , 0)
        Layout_01.addWidget(self.asset_type_field, 1 , 1)

        Layout_01.addWidget(self.asset_txt, 2 , 0)
        Layout_01.addWidget(self.asset_field, 2 , 1)
        
        Layout_01.addWidget(self.task_txt, 3 , 0)
        Layout_01.addWidget(self.task_field, 3 , 1)
                
        Layout_01.addWidget(self.trg_file_txt, 4 , 0)
        Layout_01.addWidget(self.trg_file_field, 4 , 1)

        Layout_02.addWidget(self.trg_publish_file_txt, 1 , 0)
        Layout_02.addWidget(self.trg_publish_file_field, 1 , 1)

        Layout_01.addWidget(self.loadVersionFile_button, 5 ,0)
        Layout_01.addWidget(self.versionUpFile_button, 5, 1)

        horBoxLayout.addWidget(self.apps_combobox)
        horBoxLayout.addWidget(self.loadPublishFile_button)
        horBoxLayout.addWidget(self.publishFile_button)
        
        mainLayout.addLayout(horBoxLayout)

        self.setWindowTitle("Register Versions on shotgun")
    
    def publish_file(self):
        QtGui.QMessageBox.information(self, 'Version registered', 'Version created and uploaded on shotgun', QtGui.QMessageBox.Ok)