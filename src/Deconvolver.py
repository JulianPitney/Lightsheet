import numpy as np
import matplotlib.pyplot as plt
from flowdec.nb import utils as nbutils
from flowdec import data as fd_data
from scipy import ndimage
import dask
import dask.array as da
import tensorflow as tf
from flowdec.restoration import RichardsonLucyDeconvolver
from skimage import io
import operator
import os
from flowdec import psf as fd_psf



class Deconvolver(object):


    def __init__(self):
        self.PSFGenConfigPath = "../config/psf_config.txt"



    def gen_psf_PSFGenerator(self, refractiveIndexImmersion, accuracy, wavelength, numericalAperture, pixelsizeXY, zStep, sizeX, sizeY, sizeZ, scanPath):

        configLines = []

        configLines.append("# PSFGenerator")
        configLines.append("# Wed Apr 17 17:28:22 EDT 2019")
        configLines.append("psf-Circular-Pupil-defocus=100.0")
        configLines.append("psf-Oriented-Gaussian-axial=Linear")
        configLines.append("psf-RW-NI=1.5")

        pixelsizeXYLine = "ResLateral=" + str(pixelsizeXY)
        configLines.append(pixelsizeXYLine)

        configLines.append("psf-Defocus-DBot=30.0")
        configLines.append("psf-Oriented-Gaussian-focus=0.0")
        configLines.append("psf-Astigmatism-axial=Linear")
        configLines.append("psf-TV-NI=1.5")
        configLines.append("psf-RW-accuracy=Good")
        configLines.append("psf-Cardinale-Sine-axial=Linear")
        configLines.append("psf-Lorentz-axial=Linear")
        configLines.append("psf-Gaussian-defocus=100.0")
        configLines.append("psf-Astigmatism-focus=0.0")

        accuracyLine = "psf-BW-accuracy=" + str(accuracy)
        configLines.append(accuracyLine)

        configLines.append("psf-Cardinale-Sine-focus=0.0")
        configLines.append("psf-GL-ZPos=2000.0")
        configLines.append("psf-Koehler-dMid=3.0")
        configLines.append("psf-Lorentz-focus=0.0")
        configLines.append("psf-TV-TI=150.0")
        configLines.append("psf-Koehler-dTop=1.5")
        configLines.append("psf-Koehler-n1=1.0")
        configLines.append("psf-Circular-Pupil-axial=Linear")
        configLines.append("psf-Lorentz-defocus=100.0")
        configLines.append("psf-Koehler-n0=1.5")
        configLines.append("psf-Circular-Pupil-focus=0.0")
        configLines.append("psf-Koehler-dBot=6.0")
        configLines.append("psf-Defocus-ZI=2000.0")
        configLines.append("psf-VRIGL-NS2=1.4")
        configLines.append("psf-VRIGL-NS1=1.33")
        configLines.append("psf-Double-Helix-defocus=100.0")
        configLines.append("psf-TV-ZPos=2000.0")
        configLines.append("psf-Cosine-defocus=100.0")
        configLines.append("Scale=Linear")

        refractiveIndexImmersionLine = "psf-BW-NI=" + str(refractiveIndexImmersion)
        configLines.append(refractiveIndexImmersionLine)

        configLines.append("psf-GL-NS=1.33")

        wavelengthLine = "Lambda=" + str(wavelength)
        configLines.append(wavelengthLine)

        configLines.append("PSF-shortname=BW")
        configLines.append("psf-GL-NI=1.5")
        configLines.append("psf-Astigmatism-defocus=100.0")

        zStepLine = "ResAxial=" + str(zStep)
        configLines.append(zStepLine)

        configLines.append("psf-GL-TI=150.0")
        configLines.append("psf-Double-Helix-axial=Linear")
        configLines.append("LUT=Fire")
        configLines.append("psf-VRIGL-RIvary=Linear")

        sizeZLine = "NZ=" + str(sizeZ)
        configLines.append(sizeZLine)

        configLines.append("psf-Double-Helix-focus=0.0")

        sizeYLine = "NY=" + str(sizeY)
        configLines.append(sizeYLine)

        sizeXLine = "NX=" + str(sizeX)
        configLines.append(sizeXLine)

        configLines.append("psf-VRIGL-accuracy=Good")
        configLines.append("psf-Gaussian-axial=Linear")
        configLines.append("psf-VRIGL-ZPos=2000.0")
        configLines.append("psf-Gaussian-focus=0.0")
        configLines.append("psf-Cardinale-Sine-defocus=100.0")
        configLines.append("psf-VRIGL-NI=1.5")
        configLines.append("Type=32-bits")

        numericalApertureLine = "NA=" + str(numericalAperture)
        configLines.append(numericalApertureLine)

        configLines.append("psf-Oriented-Gaussian-defocus=100.0")
        configLines.append("psf-VRIGL-NG=1.5")
        configLines.append("psf-VRIGL-TI=150.0")
        configLines.append("psf-Defocus-DMid=1.0")
        configLines.append("psf-VRIGL-TG=170.0")
        configLines.append("psf-Defocus-K=275.0")
        configLines.append("psf-Cosine-axial=Linear")
        configLines.append("psf-TV-NS=1.0")
        configLines.append("psf-Cosine-focus=0.0")
        configLines.append("psf-Defocus-DTop=30.0")
        configLines.append("psf-GL-accuracy=Good")

        with open(self.PSFGenConfigPath, 'w') as file:
            for line in configLines:
                file.write(line + "\n")
            file.close()

        os.system("java -cp ../bin/PSFGenerator.jar PSFGenerator " + self.PSFGenConfigPath)
        os.rename("../src/PSF BW.tif", scanPath + "psf.tif")

    def deconvolve_DeconvLab2(self):
        pass

    def gen_psf_Flowdec(self):
        pass

    def deconvolve_Flowdec(self):
        pass

    def crop_volume(self):
        pass

    def chunk_volume(self):
        pass




# Crop around the center of a 3D volume
def cropND(img, bounding):

    start = tuple(map(lambda a, da: a//2-da//2, img.shape, bounding))
    end = tuple(map(operator.add, start, bounding))
    slices = tuple(map(slice, start, end))
    return img[slices]


# Deconvolve a chunk
def deconv(chunk):

    # note that algo and cropped_kernel are from global scope ... ugly
    print("chunk shape", chunk.shape)
    tmp = algo.initialize().run(fd_data.Acquisition(data=chunk, kernel=croppedPSFStack), 200)
    return tmp.data




dc = Deconvolver()
dc.gen_psf_PSFGenerator(1.5, "Good", 300, 0.9, 370, 500, 1440, 1080, 10, "../scans/")



# Load data and define chunk size
#imageStack = io.imread('../scans/FLOWDEC_TESTING/scan1.tif')
#imageStack = cropND(imageStack, (50,500,500))
# Gen psf from config
#psfStack = io.imread('../scans/FLOWDEC_TESTING/PSF_3400XY.tif')
#psfStack = cropND(psfStack, (50,500,500))
"""
os.system("echo {\"na\": 0.5, \"wavelength\": 0.530, \"size_z\": 50, \"size_x\": 500, \"size_y\": 500} > ../scans/FLOWDEC_TESTING/psf.json")
psf = fd_psf.GibsonLanni.load('../scans/FLOWDEC_TESTING/psf.json')
psfStack = psf.generate()
"""

# Crop Image Stack
#croppedImageStack = cropND(imageStack, (20, 700, 700))


#algo = RichardsonLucyDeconvolver(imageStack.ndim).initialize()
#resultStack = algo.run(fd_data.Acquisition(data=imageStack, kernel=psfStack), niter=500).data





# save output
#io.imsave('../scans/FLOWDEC_TESTING/result.tif', resultStack)











"""
    This block is for chunking. Doesn't work right yet. Leaving for later.


chunkSize = (55,250,250)
padding = (20,40,40)


# Chunk array using dask
chunkedImageStack = da.from_array(croppedImageStack, chunks=chunkSize)
# Crop kernel to chunk size
croppedPSFStack = cropND(psfStack, chunkSize)


# Create deconvolver
algo = RichardsonLucyDeconvolver(chunkedImageStack.ndim, pad_mode="LOG2", pad_min=padding)
# Run chunked deconvolution on GPU
result_overlap = chunkedImageStack.map_overlap(deconv,depth=padding, boundary='reflect', dtype='int16').compute(num_workers=1)

print("DONE!")
io.imsave('FLOWDEC_200_3.tif', result_overlap)
"""






