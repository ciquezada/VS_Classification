import numpy as np
from skimage.io import imread, imshow
from skimage.transform import resize
from skimage import feature
from skimage import exposure
import matplotlib.pyplot as plt


class HogExtractor:
    def __init__(self):
        pass

    def _hog_inspect(self, img, hog_image):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), sharex=True, sharey=True)

        ax1.imshow(img, cmap=plt.cm.gray)
        ax1.set_title('Input image')

        # Rescale histogram for better display
        hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 10))

        ax2.imshow(hog_image_rescaled, cmap=plt.cm.gray)
        ax2.set_title('Histogram of Oriented Gradients')

        plt.show()

    def _get_image_data(self, phase, mag, emag):
        fig = plt.figure(figsize=(10,5), dpi=72)
        plt.ylim(-1,1)
        plt.gca().invert_yaxis()
        err = lambda x: [0, 0, 0, 1 - 0.7*((x - emag.min())/(emag.max()-emag.min()))]
        plt.scatter(phase, mag, color=[err(x) for x in emag.values])
        plt.scatter(phase+1, mag, color=[err(x) for x in emag.values])

        #Image from plot
        plt.axis('off')
        fig.tight_layout(pad=0)

        # To remove the huge white borders
        plt.margins(0)

        fig.canvas.draw()
        image_from_plot = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        image_from_plot = image_from_plot.reshape((360, 720, 3))
        plt.close()
        img = resize(image_from_plot, (64,128))
        return img

    def extract(self, time, magnitude, error, period):
        phaser = lambda mjd, P: (mjd/P)%1.
        phase = phaser(time.values, period)
        # CREAITNG HOG FEATURES
        img = self._get_image_data(phase, magnitude, error)
        fd, hog_image = feature.hog(img, orientations=9, pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2), visualize=True, multichannel=True)
        # self._hog_inspect(img, hog_image)
        hog_dict = {f"{i}":x for i, x in enumerate(fd)}
        return hog_dict
