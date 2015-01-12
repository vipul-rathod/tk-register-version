"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

App that creates folders on disk from inside of Shotgun.

"""

from tank.platform import Application
import tank
from tank.platform.qt import QtGui, QtCore
import sys, os

class RegisterVersion(tank.platform.Application):
    
    def init_app(self):
        deny_permissions = self.get_setting("deny_permissions")
        deny_platforms = self.get_setting("deny_platforms")
        self.tk = self.engine._TankBundle__tk
        self.ctx = self.engine._TankBundle__context
        self.project_name = self.ctx.project["name"]
        if self.ctx.entity["name"].__contains__("_"):
            self.asset_name = self.ctx.entity["name"].replace("_", "")
        elif self.ctx.entity["name"].__contains__(" "):
            self.asset_name = self.ctx.entity["name"].replace(" ", "")
        else:
            self.asset_name = self.ctx.entity["name"]
        self.asset = self.ctx.entity["name"]
#         self.asset_name = self.ctx.entity["name"]
        self.asset_type = self.tk.shotgun.find_one("Asset", filters = [["code", "is", self.asset]], fields= ["sg_asset_type"])["sg_asset_type"]
        self.task = self.ctx.task["name"]
        self.template_path = self.engine.get_template_by_name("review_version_path")
        
        self.fields = {}
        self.fields["Asset"] = self.asset
        self.fields["sg_asset_type"] = self.asset_type
        self.fields["Step"] = self.task
        self.fields["name"] = self.asset_name
        self.fields["version"] = 0
        self.fields["ext"] = "mov"
        
        self.path = self.template_path.apply_fields(self.fields)
        self.verDir = self.check_existing_version(self.path) 

        p = {
            "title": "Register Version",
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": True
        }

        self.engine.register_command("register_version", self.register_version, p)

    def check_existing_version(self, path):
        self.version_dir = path.split(self.asset_name)[0]
        if os.path.exists(self.version_dir):
            files = os.listdir(self.version_dir)
            return files
        else:
            app = QtGui.QApplication(sys.argv)
            error_message = QtGui.QMessageBox()
            if error_message.question(None, "", "%s path doesn't exists on the disk" % self.version_dir, error_message.Ok) == error_message.Ok:
                app.quit()
                sys.exit(app.exec_())

    def register_version(self):
        
        win = Window()
        win.project_field.setText(str(self.project_name))
        win.asset_type_field.setText(str(self.asset_type))
        win.asset_field.setText(str(self.asset))
        win.task_field.setText(str(self.task))
        win.trg_file_field.setText(str(self.verDir))
        win.show()
        win.exec_()

class Window(QtGui.QDialog):

    def __init__(self, parent=None, *args, **kwargs):
        super(Window, self).__init__(parent)
        
        #Custom code here
        self.resize(500,100)
        
        #Creating Layout
        mainLayout = QtGui.QVBoxLayout(self)
        Layout_01 = QtGui.QGridLayout(self)
        Layout_02 = QtGui.QGridLayout(self)
        
        #Connect the Layouts
        mainLayout.addLayout(Layout_01)
        mainLayout.addLayout(Layout_02)
        
        #Widgets
        project_txt = QtGui.QLabel("Project:")
        self.project_field = QtGui.QTextEdit()
        self.project_field.setMaximumSize(5000, 25)

        aseet_type_txt = QtGui.QLabel("Asset Type:")
        self.asset_type_field = QtGui.QTextEdit()
        self.asset_type_field.setMaximumSize(5000, 25)

        aseet_txt = QtGui.QLabel("Asset:")
        self.asset_field = QtGui.QTextEdit()
        self.asset_field.setMaximumSize(5000, 25)

        task_txt = QtGui.QLabel("Task:")
        self.task_field = QtGui.QTextEdit()
        self.task_field.setMaximumSize(5000, 25)

        version_txt = QtGui.QLabel("Version:")
        self.version_field = QtGui.QTextEdit()
        self.version_field.setMaximumSize(5000, 25)

        trg_file_txt = QtGui.QLabel("Target File Path:")
        self.trg_file_field = QtGui.QTextEdit()
        self.trg_file_field.setMaximumSize(5000, 25)

        src_file_txt = QtGui.QLabel("Source File Path:")
        self.src_file_field = QtGui.QTextEdit()
        self.src_file_field.setMaximumSize(5000, 25)
        self.src_file_field.setEnabled(False)

        loadfile_button = QtGui.QPushButton("Load File")
        loadfile_button.released.connect(self.load_file)

        publishfile_button = QtGui.QPushButton("Version+")
        publishfile_button.released.connect(self.publish_file)
        
        #adding widgets
        Layout_01.addWidget(project_txt, 0, 0)
        Layout_01.addWidget(self.project_field, 0 , 1)

        Layout_01.addWidget(aseet_type_txt, 1 , 0)
        Layout_01.addWidget(self.asset_type_field, 1 , 1)

        Layout_01.addWidget(aseet_txt, 2 , 0)
        Layout_01.addWidget(self.asset_field, 2 , 1)
        
        Layout_01.addWidget(task_txt, 3 , 0)
        Layout_01.addWidget(self.task_field, 3 , 1)
        
        Layout_01.addWidget(version_txt, 4 , 0)
        Layout_01.addWidget(self.version_field, 4 , 1)
        
        Layout_01.addWidget(trg_file_txt, 5 , 0)
        Layout_01.addWidget(self.trg_file_field, 5 , 1)
        
        Layout_01.addWidget(src_file_txt, 6 , 0)
        Layout_01.addWidget(self.src_file_field, 6 , 1)
        
        Layout_02.addWidget(loadfile_button, 1 ,0)
        Layout_02.addWidget(publishfile_button, 1 ,1)
        
        self.setWindowTitle("Register Versions on shotgun")
        
    def load_file(self):
        self.fileDialog = QtGui.QFileDialog.getOpenFileName(self, 'Publish File','/home')
        self.src_file_field.setText(self.fileDialog)
    
    def publish_file(self):
        print "publishing File"
