# global
import sys
import os
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit

import sas.sasview
import LocalConfig

from UI.WelcomePanelUI import Ui_WelcomePanelUI

class WelcomePanel(QtGui.QDialog, Ui_WelcomePanelUI):
    def __init__(self, parent=None):
        super(WelcomePanel, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Welcome")

        version = sas.sasview.__version__
        build = sas.sasview.__build__

        ver = "\nSasView %s\nBuild: %s" % (version, build)
        ver += LocalConfig._copyright

        self.lblVersion.setText(ver)