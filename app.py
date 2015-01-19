"""
Copyright (c) Vipul Jain
----------------------------------------------------

App that Registers versions and publishes files on Shotgun.

"""

from tank.platform import Application
import tank
from tank.platform.qt import QtGui, QtCore
import sys, os, shutil, subprocess, time

class RegisterVersion(tank.platform.Application):
    """
    Class that determines the functionality of registering versions and publishing files on Shotgun.
    """

    def init_app(self):

        #    Parameters for registering the app command
        deny_permissions = self.get_setting("deny_permissions")
        deny_platforms = self.get_setting("deny_platforms")
        
        p = {
            "title": "Register Version",
            "deny_permissions": deny_permissions,
            "deny_platforms": deny_platforms,
            "supports_multiple_selection": True
        }

        self.engine.register_command("register_version", self.register_version, p)
       
    def register_version(self):
        self.tk = self.engine._TankBundle__tk
        self.ctx = self.engine._TankBundle__context
        self.project_name = self.ctx.project["name"]
        if self.ctx.entity["name"].__contains__("_"):
            self.asset_name = self.ctx.entity["name"].replace("_", "")
        elif self.ctx.entity["name"].__contains__(" "):
            self.asset_name = self.ctx.entity["name"].replace(" ", "")
        else:
            self.asset_name = self.ctx.entity["name"]
        self.entity_type = self.ctx.entity['type']
        self.asset = self.ctx.entity["name"]
        self.asset_type = self.tk.shotgun.find_one(self.entity_type, filters = [["code", "is", self.asset]], fields= ["sg_asset_type"])["sg_asset_type"]
        self.task = self.ctx.task["name"]
        self.step = self.ctx.step["name"]
        self.step_name = self.tk.shotgun.find_one('Step', filters = [['code', 'is', self.step]], fields = ['short_name'])['short_name']
        self.app_name = self.tk.shotgun.find_one('Step', filters = [['code', 'is', self.step]], fields = ['custom_non_project_entity02_sg_apps_used_custom_non_project_entity02s'])['custom_non_project_entity02_sg_apps_used_custom_non_project_entity02s']
        self.template_path = self.engine.get_template_by_name("review_version_path")
        self.publish_template_path = self.engine.get_template_by_name("app_publish_path")

        tk_register_version = self.import_module("tk_register_version")
        self.win = tk_register_version.dialog.show_dialog(self)
        self.win.project_field.setText(str(self.project_name))
        self.win.asset_type_field.setText(str(self.asset_type))
        self.win.asset_field.setText(str(self.asset))
        self.win.task_field.setText(str(self.step_name))
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

    def fields_for_review(self, asset, asset_type, step_name, asset_name, version, ext):
        fields = {}
        fields["Asset"] = asset
        fields["sg_asset_type"] = asset_type
        fields["Step"] = step_name
        fields["name"] = asset_name
        fields["version"] = version
        fields["date"] = time.strftime("%y%m%d")
        fields['ext'] = ext.split('.')[1]
        return fields

    def load_version_file_fn(self):
        self.ext = os.path.splitext(self.versionFileDialog[0])[1]
        self.fields = self.fields_for_review(self.asset, self.asset_type, self.step_name, self.asset_name, 1, self.ext)
        self.path = self.template_path.apply_fields(self.fields)
        self.baseName = os.path.basename(self.path)
        self.file_path = self.path.split(self.baseName)[0]
        if os.path.exists(self.file_path):
            pass
        else:
            os.makedirs(self.file_path)
        list_files = self.listFilesWithParticularExtensions(self.file_path, self.asset_name, self.ext)
        if list_files:
            latest_file = max(list_files)
            version = int(latest_file.split(self.ext)[0].split('.v')[1]) + 1
            self.fields = self.fields_for_review(self.asset, self.asset_type, self.step_name, self.asset_name, version, self.ext)
            self.path = self.template_path.apply_fields(self.fields)
            self.win.trg_file_field.setText(str(self.path))
        else:
            self.fields = self.fields_for_review(self.asset, self.asset_type, self.step_name, self.asset_name, 1, self.ext)
            self.path = self.template_path.apply_fields(self.fields)
            self.win.trg_file_field.setText(str(self.path))

    def fields_for_publish(self, asset, asset_type, step_name, asset_name, version, apps, ext):
        publish_fields={}
        publish_fields["Asset"] = asset
        publish_fields["sg_asset_type"] = asset_type
        publish_fields["Step"] = step_name
        publish_fields["apps"] = apps
        publish_fields["name"] = asset_name
        publish_fields['version'] = version
        publish_fields['ext'] = ext.split('.')[1]
        return publish_fields

    def load_publish_file_fn(self):
        self.ext = os.path.splitext(self.publishFileDialog[0])[1]
        if self.win.apps_combobox.currentText() != "None":
            apps = self.win.apps_combobox.currentText()
            self.publish_fields = self.fields_for_publish(self.asset, self.asset_type, self.step_name, self.asset_name, 1, apps, self.ext)
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
                apps = self.win.apps_combobox.currentText()
                version = int(latest_file.split(self.ext)[0].split('.v')[1]) + 1
                self.publish_fields = self.fields_for_publish(self.asset, self.asset_type, self.step_name, self.asset_name, version, apps, self.ext)
                self.publish_final_path = self.publish_template_path.apply_fields(self.publish_fields)
                self.win.trg_publish_file_field.setText(str(self.publish_final_path))
            else:
                apps = self.win.apps_combobox.currentText()
                self.publish_fields = self.fields_for_publish(self.asset, self.asset_type, self.step_name, self.asset_name, 1, apps, self.ext)
                self.publish_final_path = self.publish_template_path.apply_fields(self.publish_fields)
                self.win.trg_publish_file_field.setText(str(self.publish_final_path))
        else:
            QtGui.QMessageBox.warning(self.win, 'Warning', 'Please select the app from the drop box', QtGui.QMessageBox.Ok)
    def listFilesWithParticularExtensions(self, file_path, file_prefix, ext):
        files = [ f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path,f)) and f.startswith('%s' % file_prefix) and f.endswith(ext) and f.__contains__('.v')]
        if files:
            return files
        else:
            return False

    def publish_version_fn(self):
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
        reply = QtGui.QMessageBox.question(self.win, 'Confirm Publishing',"Are you sure, You want to Publish the file?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            shutil.copyfile(self.publishFileDialog[0], self.publish_final_path)
            tank.util.register_publish(self.tk, self.ctx, self.publish_final_path, self.asset_name, self.publish_fields["version"])
            self.load_publish_file_fn()
            QtGui.QMessageBox.information(self.win, 'Publish Finished', 'File has been published.', QtGui.QMessageBox.Ok)
        else:
            pass