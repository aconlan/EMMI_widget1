import numpy as np
from PIL import Image

class EMMI_image:
    '''class to handle EMMI images for overlay'''
    def __init__(self, path):
        self.path = path
        self.im = None  # original image
        self.contrast_limits = [0, 255]
        self.im_edited = None
        self.is_green = False
        self.alpha = 255
        self.load_images_from_path()

    def rescale_values(self, im):
        im -= np.min(im)
        im = im / np.max(im)
        im *= 255
        return im

    def load_images_from_path(self):
        with Image.open(self.path) as im:
            imm = self.rescale_values(np.array(im))
            im = Image.fromarray(imm)
            rgbimg = im.convert('RGBA')
            self.im = np.array(rgbimg)
            self.im_edited = self.im.copy()

    def change_alpha(self, alpha):
        self.alpha = alpha
        im = Image.fromarray(self.im_edited)
        im.putalpha(alpha)
        self.im_edited = np.array(im)

    def change_to_green(self):
        self.is_green = True
        self.im_edited[:, :, 0] = 0  # r
        self.im_edited[:, :, 2] = 0  # b

    def change_to_rgb(self):
        self.is_green = False
        self.im_edited[:, :, 0] = self.im_edited[:, :, 1]
        self.im_edited[:, :, 2] = self.im_edited[:, :, 1]

    def change_contrast_limits(self, vmin, vmax):
        self.contrast_limits = [vmin, vmax]
        no_alpha = self.im[:, :, [1, 2, 3]].copy()
        self.im_edited = self.im.copy()
        self.im_edited[self.im_edited < vmin] = vmin
        self.im_edited[self.im_edited > vmax] = vmax
        self.change_alpha(self.alpha)
        if self.is_green == True:
            self.change_to_green()

    def max(self):
        return np.max(self.im_edited)