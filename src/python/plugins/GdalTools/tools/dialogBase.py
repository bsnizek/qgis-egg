# -*- coding: utf-8 -*-

"""
***************************************************************************
    dialogBase.py
    ---------------------
    Date                 : June 2010
    Copyright            : (C) 2010 by Giuseppe Sucameli
    Email                : brush dot tyler at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Giuseppe Sucameli'
__date__ = 'June 2010'
__copyright__ = '(C) 2010, Giuseppe Sucameli'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from PyQt.QtCore import Qt, QProcess, QUrl, QIODevice, QCoreApplication, pyqtSignal
from PyQt.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QErrorMessage, QApplication
from PyQt.QtGui import QIcon, QDesktopServices

# to know the os
import platform

from .ui_dialogBase import Ui_GdalToolsDialog as Ui_Dialog
from . import GdalTools_utils as Utils
from .. import resources_rc  # NOQA

import string


class GdalToolsBaseDialog(QDialog, Ui_Dialog):
    refreshArgs = pyqtSignal()
    okClicked = pyqtSignal()
    closeClicked = pyqtSignal()
    helpClicked = pyqtSignal()
    processError = pyqtSignal(QProcess.ProcessError)
    processFinished = pyqtSignal(int, QProcess.ExitStatus)
    finished = pyqtSignal(bool)
    valuesChanged = pyqtSignal(list)

    def __init__(self, parent, iface, pluginBase, pluginName, pluginCommand):
        QDialog.__init__(self, parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.iface = iface

        self.process = QProcess(self)
        Utils.setProcessEnvironment(self.process)
        self.process.error.connect(self.processError)
        self.process.finished.connect(self.processFinished)

        self.setupUi(self)
        self.arguments = []

        self.editCmdBtn.setIcon(QIcon(":/icons/edit.png"))
        self.editCmdBtn.toggled.connect(self.editCommand)
        self.resetCmdBtn.setIcon(QIcon(":/icons/reset.png"))
        self.resetCmdBtn.clicked.connect(self.resetCommand)
        self.editCommand(False)

        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.helpRequested.connect(self.help)

        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

        self.plugin = pluginBase
        self.valuesChanged.connect(self.handleRefreshArgs)

        self.pluginLayout.addWidget(self.plugin)
        self.plugin.setFocus()

        self.setWindowTitle(pluginName)
        self.setPluginCommand(pluginCommand)

    def setPluginCommand(self, cmd):
        # on Windows replace the .py with .bat extension
        if platform.system() == "Windows" and cmd[-3:] == ".py":
            self.command = cmd[:-3] + ".bat"
        else:
            self.command = cmd

        if cmd[-3:] == ".py":
            self.helpFileName = cmd[:-3] + ".html"
        else:
            self.helpFileName = cmd + ".html"

    def editCommand(self, enabled):
        if not self.commandIsEnabled():
            return
        self.editCmdBtn.setChecked(enabled)
        self.resetCmdBtn.setEnabled(enabled)
        self.textEditCommand.setReadOnly(not enabled)
        self.controlsWidget.setEnabled(not enabled)
        self.refreshArgs.emit()

    def resetCommand(self):
        if not self.commandIsEditable():
            return
        self.refreshArgs.emit()

    def commandIsEditable(self):
        return self.commandIsEnabled() and self.editCmdBtn.isChecked()

    def setCommandViewerEnabled(self, enable):
        if not enable:
            self.editCommand(False)
        self.commandWidget.setEnabled(enable)

    def commandIsEnabled(self):
        return self.commandWidget.isEnabled()

    def reject(self):
        if self.process.state() != QProcess.NotRunning:
            ret = QMessageBox.warning(self, self.tr("Warning"), self.tr("The command is still running. \nDo you want terminate it anyway?"), QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return

            self.process.error.disconnect(self.processError)
            self.process.finished.disconnect(self.processFinished)

        self.closeClicked.emit()

    def accept(self):
        self.okClicked.emit()

    def help(self):
        self.helpClicked.emit()

    # show the online tool documentation in the default browser
    def onHelp(self):
        helpPath = Utils.getHelpPath()
        if helpPath == '':
            url = QUrl("http://www.gdal.org/" + self.helpFileName)
        else:
            url = QUrl.fromLocalFile(helpPath + '/' + self.helpFileName)
        QDesktopServices.openUrl(url)

    # called when a value in the plugin widget interface changed
    def handleRefreshArgs(self, args):
        self.arguments = [unicode(a) for a in args]

        if not self.commandIsEnabled():
            self.textEditCommand.setPlainText(self.command)
        else:
            self.textEditCommand.setPlainText(self.command + " " + Utils.escapeAndJoin(self.arguments))

    # enables the OK button
    def enableRun(self, enable=True):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    # start the command execution
    def onRun(self):
        self.enableRun(False)
        self.setCursor(Qt.WaitCursor)
        if not self.commandIsEditable():
            #print(self.command+' '+unicode(self.arguments))
            self.process.start(self.command, self.arguments, QIODevice.ReadOnly)
        else:
            self.process.start(self.textEditCommand.toPlainText(), QIODevice.ReadOnly)

    # stop the command execution
    def stop(self):
        self.enableRun(True)
        self.setCursor(Qt.ArrowCursor)
        self.process.kill()

    # called on closing the dialog, stop the process if it's running
    def onClosing(self):
        self.stop()
        QDialog.reject(self)

    # called if an error occurs when the command has not already finished, shows the occurred error message
    def onError(self, error):
        if error == QProcess.FailedToStart:
            msg = QCoreApplication.translate("GdalTools", "The process failed to start. Either the invoked program is missing, or you may have insufficient permissions to invoke the program.")
        elif error == QProcess.Crashed:
            msg = QCoreApplication.translate("GdalTools", "The process crashed some time after starting successfully.")
        else:
            msg = QCoreApplication.translate("GdalTools", "An unknown error occurred.")

        QErrorMessage(self).showMessage(msg)
        QApplication.processEvents()  # give the user chance to see the message

        self.stop()

    # called when the command finished its execution, shows an error message if there's one
    # and, if required, load the output file in canvas
    def onFinished(self, exitCode, status):
        if status == QProcess.CrashExit:
            self.stop()
            return

        if self.command.find("gdalinfo") != -1 and exitCode == 0:
            self.finished.emit(self.loadCheckBox.isChecked())
            self.stop()
            return

        # show the error message if there's one, otherwise show the process output message
        msg = unicode(self.process.readAllStandardError())
        if msg == '':
            outMessages = unicode(self.process.readAllStandardOutput()).splitlines()

            # make sure to not show the help
            for m in outMessages:
                m = string.strip(m)
                if m == '':
                    continue
                # TODO fix this
                #if m.contains( QRegExp( "^(?:[Uu]sage:\\s)?" + QRegExp.escape(self.command) + "\\s" ) ):
                #  if msg.isEmpty():
                #    msg = self.tr ( "Invalid parameters." )
                #  break
                #if m.contains( QRegExp( "0(?:\\.+[1-9]0{1,2})+" ) ):
                #  continue

                if msg:
                    msg += "\n"
                msg += m

        QErrorMessage(self).showMessage(msg.replace("\n", "<br>"))

        if exitCode == 0:
            self.finished.emit(self.loadCheckBox.isChecked())

        self.stop()
