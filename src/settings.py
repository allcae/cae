# -*- coding: utf-8 -*-


"""
    © Ihor Mirzov, September 2019
    Distributed under GNU General Public License v3.0

    Application's settings.
    Attributes values are maintained through the settings.ENV file.
    User dialog form is maintained through the settings.XML file.
    You may edit settings.XML directly from Qt Designer.
"""


import os, sys, logging, re
from PyQt5 import QtWidgets, uic


# Session settings object used everywhere in the code
class Settings():


    # Read settings from file
    def __init__(self):
        op_sys = '_windows' if os.name=='nt' else '_linux'
        path = os.path.dirname(sys.argv[0])
        self.file_name = os.path.join(path, 'settings' + op_sys + '.env') # full path
        try:
            f = open(self.file_name).read()
            self.lines = f.split('\n')
            exec(f)
        except:
            # Apply default values
            self.path_cgx = ''
            self.path_paraview = ''
            self.path_editor = ''
            self.path_start_model = 'examples/default.inp'
            self.logging_level = 'INFO'
            self.vtk_view = 'WithEdges'
            self.show_maximized = True
            self.show_empty_keywords = False
            self.expanded = True
            self.vtk_show_axes = True
            self.vtk_parallel_view = True
            self.show_help = True
            self.show_vtk = True
            self.error = True


    # Automatically save settings during the workflow
    def save(self):
        with open(self.file_name, 'w') as f:
            new_line = False
            for line in self.lines:
                match = re.search('^self\.(\S+)\s*=\s*(.+)', line)
                if match:
                    param = match.group(1)
                    value = match.group(2)
                    if value.startswith('\'') and value.endswith('\''):
                        value = '\'' + getattr(self, param) + '\''
                    else:
                        value = getattr(self, param)
                    line = 'self.{} = {}'.format(param, value)
                if new_line:
                    f.write('\n')
                f.write(line)
                new_line = True
        logging.info('Settings saved.')


    # Open dialog window and pass settings
    def open(self):
        dialog = Dialog()

        # Warning about Cygwin DLLs
        if os.name=='nt':
            logging.warning('In Windows ccx binary may not work if placed outside \'bin\' directory. It needs Cygwin DLLs!')

        # Get response from dialog window
        if dialog.exec() == Dialog.Accepted: # if user pressed 'OK'
            dialog.onOk()
            logging.warning('For some settings to take effect application\'s restart may be needed.')
        

# User dialog window with all setting attributes: menu File->Settings
class Dialog(QtWidgets.QDialog):


    # Create dialog window
    def __init__(self):

        # Load UI form
        super(Dialog, self).__init__()
        path = os.path.dirname(os.path.abspath(sys.argv[0]))
        settings_xml = os.path.join(path, 'settings.xml') # full path
        uic.loadUi(settings_xml, self)

        # Push settings values to the form
        self.settings = Settings() # read settings from file
        for attr, value in self.settings.__dict__.items():
            try:
                widget = self.findChild(QtWidgets.QCheckBox, attr)
                widget.setChecked(value)
            except:
                try:
                    widget = self.findChild(QtWidgets.QLineEdit, attr)
                    widget.setText(value)
                except:
                    try:
                        widget = self.findChild(QtWidgets.QComboBox, attr)
                        widget.setCurrentText(value)
                    except:
                        pass


    # Save settings updated via dialog
    def onOk(self):
        with open(self.settings.file_name, 'w') as f:

            # Iterate over class attributes
            for attr, value in self.__dict__.items():
                if value.__class__.__name__ in ['QCheckBox', 'QLineEdit', 'QComboBox']:

                    # Update session settings
                    setattr(self.settings, attr, value)

                    # Write settings in file
                    if value.__class__.__name__ == 'QCheckBox':
                        line = 'self.{} = {}'.format(attr, value.isChecked())
                        comment = value.text()
                    if value.__class__.__name__ == 'QLineEdit':
                        text = value.text()
                        if '\\' in text: # reconstruct path for Windows
                            text = '\\\\'.join(value.text().split('\\'))
                        line = 'self.{} = \'{}\''.format(attr, text)
                        value = self.__dict__['label_' + attr]
                        comment = value.text()
                    if value.__class__.__name__ == 'QComboBox':
                        line = 'self.{} = \'{}\''.format(attr, value.currentText())
                        value = self.__dict__['label_' + attr]
                        comment = value.text()
                    f.write('# ' + comment + '\n')
                    f.write(line + '\n\n')
                    logging.debug(line)


# Test module
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)

    # Create application
    app = QtWidgets.QApplication(sys.argv)

    # Create and open settings window
    settings = Settings()
    if hasattr(settings, 'error'):
        logging.error('Error reading ENV settings file. Default values used.')
    settings.open()

    # Clean cached files
    from clean import cleanCache
    cleanCache()