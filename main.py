from EMMI_image_library import EMMI_image
from emmi_widget import Ui_MainWindow

import os
import glob2
import numpy as np
import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog
)
import pyqtgraph as pg
import pyqtgraph.exporters
import sys

pg.setConfigOption('imageAxisOrder', 'row-major')  # best performance


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.paths = None
        self.im1 = None
        self.im2 = None
        self.load_images()
        self.connectSignalsSlots()
        self.plot_main_image()

    def connectSignalsSlots(self):
        self.action_Exit.triggered.connect(self.close)
        self.alphaSlider.actionTriggered.connect(self.alpha_change)
        self.pushButton_ExportIm.clicked.connect(self.export_image)

        # Menu items
        self.action_Load_demo.triggered.connect(self.open_demo_file)  # Reopen the demo data.
        self.action_Open.triggered.connect(self.launch_file_dialogue)  # Find a file and load it.
        self.action_Export_Image.triggered.connect(self.export_image)  # Save screenshot.

    def load_images(self):
        """Im2 hotspot will have a median value close to zero.
        We can use this to distinguish between the image types."""
        if self.paths is None:
            paths = glob2.glob('example images/*.tif')
        else:
            paths = self.paths

        first_im = EMMI_image(paths[0])
        second_im = EMMI_image(paths[1])

        if np.median(first_im.im_edited) > np.median(second_im.im_edited):
            # second image is the hotspot --> im2
            self.im1 = first_im
            self.im2 = second_im
        else:
            self.im1 = second_im
            self.im2 = first_im
        self.im2.change_alpha(150)
        self.im2.change_to_green()

    def plot_main_image(self):
        """Initialise the plots and roi."""
        main_widg = self.imageWidget
        print('main_widg  = ' + str(self.imageWidget.size()))
        self.vb = main_widg.addViewBox(lockAspect=True, defaultPadding=0.0)
        self.vb.enableAutoRange()
        self.imitem = pg.ImageItem(image=np.flipud(self.im1.im_edited))
        self.im2item = pg.ImageItem(image=np.flipud(self.im2.im_edited), setCompositionMode='SourceOver')
        self.vb.addItem(self.imitem)
        self.vb.addItem(self.im2item)

        # Add histogram here for Contrast/color control
        self.hist1 = pg.HistogramLUTItem()
        self.hist1.setImageItem(self.imitem)
        self.histoWidget1.addItem(self.hist1)

        self.hist2 = pg.HistogramLUTItem()
        self.hist2.setImageItem(self.im2item)
        self.histoWidget2.addItem(self.hist2)

    def update(self):
        self.imitem.setImage(image=np.flipud(self.im1.im_edited))
        self.im2item.setImage(image=np.flipud(self.im2.im_edited))

    def alpha_change(self):
        """on change of alpha slider, store histogram levels.
        Change image alpha. Update im1 and im2.
        Set histogram levels to previous values."""
        hist1_levels = self.hist1.getLevels()
        hist2_levels = self.hist2.getLevels()

        self.im2.change_alpha(self.alphaSlider.value())
        self.update()
        self.hist1.setLevels(min=hist1_levels[0], max=hist1_levels[1])
        self.hist2.setLevels(min=hist2_levels[0], max=hist2_levels[1])

    def export_image(self):
        # Export viewbox_Main as a png with the measurements baked in.
        exporter = pg.exporters.ImageExporter(self.vb)
        if self.paths is None:
            exporter.export('Export.png')
        else:
            directory = os.path.dirname(self.paths[0])
            exporter.export(directory + '/Export.png')
        print('Image exported as .png')
        self.statusBar().showMessage('Image exported as .png', 1500)

    def open_demo_file(self):
        """Loads the demo image from examples file."""
        self.paths = None
        self.load_images()
        self.update()

    def launch_file_dialogue(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileNames(self, "Open two EMMI image files (.tif). "
                                                         "Select hotspot image first, background image second.",
                                                   "", "Image Files (*.tif)", options=options)
        if filename:
            print(filename)
            self.paths = filename
            self.load_images()
            self.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            filepaths = [f.toLocalFile() for f in event.mimeData().urls()]
            if len(filepaths) < 2:
                self.statusBar().showMessage('Error: Need two EMMI images to form overlay', 1500)
            else:
                path1, path2 = filepaths[0:2]  # Filter for the first two.
                print(path1)
                print(path2)
                self.paths = [path1, path2]
                self.load_images()
                self.update()

            #filepaths = event.mimeData().urls()[0].toLocalFile() # For one file path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
