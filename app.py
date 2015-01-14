"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

App that creates folders on disk from inside of Shotgun.

"""

from tank.platform import Application
import tank
from tank.platform.qt import QtGui, QtCore
import sys, os, shutil

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
        self.asset_type = self.tk.shotgun.find_one("Asset", filters = [["code", "is", self.asset]], fields= ["sg_asset_type"])["sg_asset_type"]
        self.task = self.ctx.task["name"]
        self.template_path = self.engine.get_template_by_name("review_version_path")

        p = {
            "title": "Register Version",
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": True
        }

        self.engine.register_command("register_version", self.register_version, p)

    def register_version(self):
        self.win = Window()
        self.win.project_field.setText(str(self.project_name))
        self.win.asset_type_field.setText(str(self.asset_type))
        self.win.asset_field.setText(str(self.asset))
        self.win.task_field.setText(str(self.task))
        self.win.loadfile_button.released.connect(self.load_file)
        self.win.publishfile_button.released.connect(self.publish_version)
        self.win.show()
        self.win.exec_()

    def load_file(self):
        self.fileDialog = QtGui.QFileDialog.getOpenFileName(self.win, 'Publish File','/home')
        self.ext = os.path.splitext(self.fileDialog[0])[1]
        self.win.src_file_field.setText(str(self.fileDialog[0]))
        self.fields = {}
        self.fields["Asset"] = self.asset
        self.fields["sg_asset_type"] = self.asset_type
        self.fields["Step"] = self.task
        self.fields["name"] = self.asset_name
        self.fields["version"] = 1
        self.fields['ext'] = self.ext.split('.')[1]
        self.path = self.template_path.apply_fields(self.fields)
        self.baseName = os.path.basename(self.path)
        self.file_path = self.path.split(self.baseName)[0]
        list_files = self.listFilesWithParticularExtensions(self.file_path, self.asset_name, self.ext)
        if list_files:
            latest_file = max(list_files)
#             self.version = int(latest_file.split(self.ext)[0].split('.v')[1])
            self.fields = {}
            self.fields["Asset"] = self.asset
            self.fields["sg_asset_type"] = self.asset_type
            self.fields["Step"] = self.task
            self.fields["name"] = self.asset_name
            self.fields['version'] = int(latest_file.split(self.ext)[0].split('.v')[1]) + 1
            self.fields['ext'] = self.ext.split('.')[1]
            self.path = self.template_path.apply_fields(self.fields)
            self.win.version_field.setText(str(self.fields['version']))
            self.win.trg_file_field.setText(str(self.path))
        else:
            self.fields = {}
            self.fields["Asset"] = self.asset
            self.fields["sg_asset_type"] = self.asset_type
            self.fields["Step"] = self.task
            self.fields["name"] = self.asset_name
            self.fields['version'] = 0 + 1
            self.fields['ext'] = self.ext.split('.')[1]
            self.path = self.template_path.apply_fields(self.fields)
            self.win.version_field.setText(str(self.fields['version']))
            self.win.trg_file_field.setText(str(self.path))

    def listFilesWithParticularExtensions(self, file_path, file_prefix, ext):
        files = [ f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path,f)) and f.startswith('%s_' % file_prefix) and f.endswith(ext) and f.__contains__('.v0')]
        if files:
            return files
        else:
            return False
    
    def publish_version(self):
        source_path = self.win.src_file_field.toPlainText()
        dest_path = self.win.trg_file_field.toPlainText()
        if source_path:
            shutil.copyfile(source_path, dest_path)
            data = { 'project': self.ctx.project,
                 'code':  os.path.basename(dest_path),
                 'description': 'Playblast published',
                 'sg_path_to_movie': dest_path,
                 'sg_status_list': '',
                 'entity': self.ctx.entity,
                 'sg_task': self.ctx.task,
                 'user': self.ctx.user}
            create_version = self.tk.shotgun.create('Version', data)
            upload_version = self.tk.shotgun.upload('Version', create_version['id'], dest_path, 'sg_uploaded_movie')
            QtGui.QMessageBox.information(self.win, 'Version registered', 'Version created and uploaded on shotgun', QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.warning(self.win, 'Warning', 'No Input given for uploading.\nLoad file first to version up', QtGui.QMessageBox.Ok)

class Window(QtGui.QDialog):

    def __init__(self, parent=None):
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

        self.loadfile_button = QtGui.QPushButton("Load File")

        self.publishfile_button = QtGui.QPushButton("Version+")
        self.publishfile_button.released.connect(self.publish_file)
        
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
        
        Layout_02.addWidget(self.loadfile_button, 1 ,0)
        Layout_02.addWidget(self.publishfile_button, 1 ,1)
        
        self.setWindowTitle("Register Versions on shotgun")
    
    def publish_file(self):
        print "publishing File"
