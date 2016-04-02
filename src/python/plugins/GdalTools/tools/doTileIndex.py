# -*- coding: utf-8 -*-

"""
***************************************************************************
    doTileIndex.py
    ---------------------
    Date                 : February 2011
    Copyright            : (C) 2011 by Giuseppe Sucameli
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
__date__ = 'February 2011'
__copyright__ = '(C) 2011, Giuseppe Sucameli'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from PyQt.QtWidgets import QWidget

from .ui_widgetTileIndex import Ui_GdalToolsWidget as Ui_Widget
from .widgetPluginBase import GdalToolsBasePluginWidget as BasePluginWidget
from . import GdalTools_utils as Utils


class GdalToolsDialog(QWidget, Ui_Widget, BasePluginWidget):

    def __init__(self, iface):
        QWidget.__init__(self)
        self.iface = iface

        self.setupUi(self)
        BasePluginWidget.__init__(self, self.iface, "gdaltindex")

        self.inSelector.setType(self.inSelector.FILE)
        self.outSelector.setType(self.outSelector.FILE)

        self.setParamsStatus([
            (self.inSelector, "filenameChanged"),
            #( self.recurseCheck, "stateChanged" ),
            (self.outSelector, "filenameChanged"),
            (self.indexFieldEdit, "textChanged", self.indexFieldCheck),
            (self.skipDifferentProjCheck, "stateChanged", None, 1500)
        ])

        self.inSelector.selectClicked.connect(self.fillInputDirEdit)
        self.outSelector.selectClicked.connect(self.fillOutputFileEdit)

    def fillInputDirEdit(self):
        inputDir = Utils.FileDialog.getExistingDirectory(self, self.tr("Select the input directory with raster files"))
        if not inputDir:
            return
        self.inSelector.setFilename(inputDir)

    def fillOutputFileEdit(self):
        lastUsedFilter = Utils.FileFilter.lastUsedVectorFilter()
        outputFile, encoding = Utils.FileDialog.getSaveFileName(self, self.tr("Select where to save the TileIndex output"), Utils.FileFilter.allVectorsFilter(), lastUsedFilter, True)
        if not outputFile:
            return
        Utils.FileFilter.setLastUsedVectorFilter(lastUsedFilter)

        self.outputFormat = Utils.fillVectorOutputFormat(lastUsedFilter, outputFile)
        self.outSelector.setFilename(outputFile)
        self.lastEncoding = encoding

    def getArguments(self):
        arguments = []
        if self.indexFieldCheck.isChecked() and self.indexFieldEdit.text():
            arguments.append("-tileindex")
            arguments.append(self.indexFieldEdit.text())
        if self.skipDifferentProjCheck.isChecked():
            arguments.append("-skip_different_projection")
        arguments.append(self.getOutputFileName())
        arguments.extend(Utils.getRasterFiles(self.getInputFileName(), self.recurseCheck.isChecked()))
        return arguments

    def getOutputFileName(self):
        return self.outSelector.filename()

    def getInputFileName(self):
        return self.inSelector.filename()

    def addLayerIntoCanvas(self, fileInfo):
        vl = self.iface.addVectorLayer(fileInfo.filePath(), fileInfo.baseName(), "ogr")
        if vl is not None and vl.isValid():
            if hasattr(self, 'lastEncoding'):
                vl.setProviderEncoding(self.lastEncoding)
