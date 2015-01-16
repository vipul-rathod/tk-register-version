"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------

App that creates folders on disk from inside of Shotgun.

"""

from tank.platform import Application
import tank
from tank.platform.qt import QtGui, QtCore
import sys, os, shutil, subprocess

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
        self.entity_type = self.ctx.entity['type']
        self.asset_type = self.tk.shotgun.find_one(self.entity_type, filters = [["code", "is", self.asset]], fields= ["sg_asset_type"])["sg_asset_type"]
        self.task = self.ctx.task["name"]
        self.step = self.ctx.step["name"]
        self.step_name = self.tk.shotgun.find_one('Step', filters = [['code', 'is', self.step]], fields = ['short_name'])['short_name']
        self.app_name = self.tk.shotgun.find_one('Step', filters = [['code', 'is', self.step]], fields = ['custom_non_project_entity02_sg_apps_used_custom_non_project_entity02s'])['custom_non_project_entity02_sg_apps_used_custom_non_project_entity02s']
        self.template_path = self.engine.get_template_by_name("review_version_path")
        self.publish_template_path = self.engine.get_template_by_name("app_publish_path")

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
        self.win.task_field.setText(str(self.step_name))
#         self.win.connect(self.win.trg_file_txt, QtCore.SIGNAL('clicked()'), self.trg_label_clicked)
        self.win.trg_file_txt.released.connect(self.trg_version_label_clicked)
        self.win.trg_publish_file_txt.released.connect(self.trg_publish_label_clicked)
        self.win.loadVersionFile_button.released.connect(self.load_version_file)
        self.win.loadPublishFile_button.released.connect(self.load_publish_file)
        self.win.versionUpFile_button.released.connect(self.publish_version_fn)
        self.win.publishFile_button.released.connect(self.publish_file_fn)
        if self.app_name:
            for each in sorted(self.app_name):
                self.win.apps_combobox.addItem(each["name"])
            self.win.show()
            self.win.exec_()
        else:
            QtGui.QMessageBox.warning(self.win, 'Warning', 'sg_apps_used field is empty.\nPlease specify the application used for the selected task', QtGui.QMessageBox.Ok)

    def trg_version_label_clicked(self):
        subprocess.check_call(['explorer', self.file_path])

    def trg_publish_label_clicked(self):
        subprocess.check_call(['explorer', self.publish_path])

    def load_version_file(self):
        self.versionFileDialog = QtGui.QFileDialog.getOpenFileName(self.win, 'Version File','/home')
        self.load_version_file_fn()

    def load_publish_file(self):
        self.publishFileDialog = QtGui.QFileDialog.getOpenFileName(self.win, 'Publish File','/home')
        self.load_publish_file_fn()

    def load_version_file_fn(self):
        self.ext = os.path.splitext(self.versionFileDialog[0])[1]
        self.fields = {}
        self.fields["Asset"] = self.asset
        self.fields["sg_asset_type"] = self.asset_type
        self.fields["Step"] = self.step_name
        self.fields["name"] = self.asset_name
        self.fields["version"] = 1
        self.fields['ext'] = self.ext.split('.')[1]
        self.path = self.template_path.apply_fields(self.fields)
        self.win.trg_file_field.setText(str("Vipul"))
        self.baseName = os.path.basename(self.path)
        self.file_path = self.path.split(self.baseName)[0]
        if os.path.exists(self.file_path):
            pass
        else:
            os.makedirs(self.file_path)
        self.win.trg_file_field.setText(str("Vipul"))
        list_files = self.listFilesWithParticularExtensions(self.file_path, self.asset_name, self.ext)
        if list_files:
            latest_file = max(list_files)
#             self.version = int(latest_file.split(self.ext)[0].split('.v')[1])
            self.fields = {}
            self.fields["Asset"] = self.asset
            self.fields["sg_asset_type"] = self.asset_type
            self.fields["Step"] = self.step_name
            self.fields["name"] = self.asset_name
            self.fields['version'] = int(latest_file.split(self.ext)[0].split('.v')[1]) + 1
            self.fields['ext'] = self.ext.split('.')[1]
            self.path = self.template_path.apply_fields(self.fields)
#             self.win.version_field.setText(str(self.fields['version']))
            self.win.trg_file_field.setText(str(self.path))
        else:
            self.fields = {}
            self.fields["Asset"] = self.asset
            self.fields["sg_asset_type"] = self.asset_type
            self.fields["Step"] = self.step_name
            self.fields["name"] = self.asset_name
            self.fields['version'] = 0 + 1
            self.fields['ext'] = self.ext.split('.')[1]
            self.path = self.template_path.apply_fields(self.fields)
#             self.win.version_field.setText(str(self.fields['version']))
            self.win.trg_file_field.setText(str(self.path))

    def load_publish_file_fn(self):
        self.ext = os.path.splitext(self.publishFileDialog[0])[1]
        if self.win.apps_combobox.currentText() != "None":
            self.publish_fields={}
            self.publish_fields["Asset"] = self.asset
            self.publish_fields["sg_asset_type"] = self.asset_type
            self.publish_fields["Step"] = self.step_name
            self.publish_fields["apps"] = self.win.apps_combobox.currentText()
            self.publish_fields["name"] = self.asset_name
            self.publish_fields['version'] = 1
            self.publish_fields['ext'] = self.ext.split('.')[1]
            self.publish_file_path = self.publish_template_path.apply_fields(self.publish_fields)
            self.publish_baseName = os.path.basename(self.publish_file_path)
            self.publish_path = self.publish_file_path.split(self.publish_baseName)[0]

            if os.path.exists(self.publish_path):
                pass
            else:
                os.makedirs(self.publish_path)

            list_files = self.listFilesWithParticularExtensions(self.publish_path, self.asset_name, self.ext)
            if list_files:
                latest_file = max(list_files)
                self.publish_fields = {}
                self.publish_fields["Asset"] = self.asset
                self.publish_fields["sg_asset_type"] = self.asset_type
                self.publish_fields["Step"] = self.step_name
                self.publish_fields["apps"] = self.win.apps_combobox.currentText()
                self.publish_fields["name"] = self.asset_name
                self.publish_fields['version'] = int(latest_file.split(self.ext)[0].split('.v')[1]) + 1
                self.publish_fields['ext'] = self.ext.split('.')[1]
                self.publish_final_path = self.publish_template_path.apply_fields(self.publish_fields)
#                 self.win.version_field.setText(str(self.publish_fields['version']))
                self.win.trg_publish_file_field.setText(str(self.publish_final_path))
            else:
                self.publish_fields = {}
                self.publish_fields["Asset"] = self.asset
                self.publish_fields["sg_asset_type"] = self.asset_type
                self.publish_fields["Step"] = self.step_name
                self.publish_fields["apps"] = self.win.apps_combobox.currentText()
                self.publish_fields["name"] = self.asset_name
                self.publish_fields['version'] = 0 + 1
                self.publish_fields['ext'] = self.ext.split('.')[1]
                self.publish_final_path = self.publish_template_path.apply_fields(self.publish_fields)
#                 self.win.version_field.setText(str(self.publish_fields['version']))
                self.win.trg_publish_file_field.setText(str(self.publish_final_path))
        else:
            QtGui.QMessageBox.warning(self.win, 'Warning', 'Please select the app from the drop box', QtGui.QMessageBox.Ok)
    def listFilesWithParticularExtensions(self, file_path, file_prefix, ext):
        files = [ f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path,f)) and f.startswith('%s_' % file_prefix) and f.endswith(ext) and f.__contains__('.v0')]
        if files:
            return files
        else:
            return False
    
    def publish_version_fn(self):
#         self.win.src_file_field.setText(str(self.versionFileDialog[0]))
        source_path = self.versionFileDialog[0]
        dest_path = self.win.trg_file_field.toPlainText()
        if source_path:
            shutil.copyfile(source_path, dest_path)
            data = { 'project': self.ctx.project,
                 'code':  os.path.basename(dest_path),
                 'description': 'Version registered',
                 'sg_path_to_movie': dest_path,
                 'sg_status_list': '',
                 'entity': self.ctx.entity,
                 'sg_task': self.ctx.task,
                 'user': self.ctx.user}
            create_version = self.tk.shotgun.create('Version', data)
            upload_version = self.tk.shotgun.upload('Version', create_version['id'], dest_path, 'sg_uploaded_movie')
            QtGui.QMessageBox.information(self.win, 'Version registered', 'Version created and uploaded on shotgun', QtGui.QMessageBox.Ok)
            self.load_version_file_fn()
        else:
            QtGui.QMessageBox.warning(self.win, 'Warning', 'No Input given for uploading.\nLoad file first to version up', QtGui.QMessageBox.Ok)

    def publish_file_fn(self):            
            shutil.copyfile(self.publishFileDialog[0], self.publish_final_path)
            tank.util.register_publish(self.tk, self.ctx, self.publish_final_path, self.asset_name, self.publish_fields["version"])
            self.load_publish_file_fn()
            reply = QtGui.QMessageBox.question(self.win, 'Open directory',"Do you want to open publish directory?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                subprocess.check_call(['explorer', self.publish_path])
            else:
                pass

class Window(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        
        #Custom code here
        self.resize(500,100)
        
        #Creating Layout
        mainLayout = QtGui.QVBoxLayout(self)
        Layout_01 = QtGui.QGridLayout(self)
        Layout_02 = QtGui.QGridLayout(self)
        horBoxLayout = QtGui.QHBoxLayout()
        
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

#         version_txt = QtGui.QLabel("Version:")
#         self.version_field = QtGui.QTextEdit()
#         self.version_field.setMaximumSize(5000, 25)

        self.trg_file_txt = QtGui.QPushButton("Target Version Path:")
        self.trg_file_field = QtGui.QTextEdit()
        self.trg_file_field.setMaximumSize(5000, 25)

        self.trg_publish_file_txt = QtGui.QPushButton("Target Publish Path:")
        self.trg_publish_file_field = QtGui.QTextEdit()
        self.trg_publish_file_field.setMaximumSize(5000, 25)

#         src_file_txt = QtGui.QLabel("Source File Path:")
#         self.src_file_field = QtGui.QTextEdit()
#         self.src_file_field.setMaximumSize(5000, 25)
#         self.src_file_field.setEnabled(False)

        self.loadVersionFile_button = QtGui.QPushButton("Load Version")
        self.loadPublishFile_button = QtGui.QPushButton("Load Publish")

        self.versionUpFile_button = QtGui.QPushButton("Version+")
#         self.versionUpFile_button.released.connect(self.publish_file)
        
        apps_txt = QtGui.QLabel("Apps Used:")
        self.apps_combobox = QtGui.QComboBox()
        self.apps_combobox.addItem("None")
        
        self.publishFile_button = QtGui.QPushButton("Publish")
        
        #adding widgets
        Layout_01.addWidget(project_txt, 0, 0)
        Layout_01.addWidget(self.project_field, 0 , 1)

        Layout_01.addWidget(aseet_type_txt, 1 , 0)
        Layout_01.addWidget(self.asset_type_field, 1 , 1)

        Layout_01.addWidget(aseet_txt, 2 , 0)
        Layout_01.addWidget(self.asset_field, 2 , 1)
        
        Layout_01.addWidget(task_txt, 3 , 0)
        Layout_01.addWidget(self.task_field, 3 , 1)
        
#         Layout_01.addWidget(version_txt, 4 , 0)
#         Layout_01.addWidget(self.version_field, 4 , 1)
        
        Layout_01.addWidget(self.trg_file_txt, 4 , 0)
        Layout_01.addWidget(self.trg_file_field, 4 , 1)

        Layout_01.addWidget(self.trg_publish_file_txt, 5 , 0)
        Layout_01.addWidget(self.trg_publish_file_field, 5 , 1)
        
#         Layout_01.addWidget(src_file_txt, 6 , 0)
#         Layout_01.addWidget(self.src_file_field, 6 , 1)

        Layout_02.addWidget(self.loadVersionFile_button, 1 ,0)
        Layout_02.addWidget(self.versionUpFile_button, 1, 1)

        horBoxLayout.addWidget(self.apps_combobox)
        horBoxLayout.addWidget(self.loadPublishFile_button)
        horBoxLayout.addWidget(self.publishFile_button)
        
        mainLayout.addLayout(horBoxLayout)

        self.setWindowTitle("Register Versions on shotgun")
    
    def publish_file(self):
        QtGui.QMessageBox.information(self, 'Version registered', 'Version created and uploaded on shotgun', QtGui.QMessageBox.Ok)

