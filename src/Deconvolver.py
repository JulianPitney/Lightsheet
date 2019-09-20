import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
import dask
import dask.array as da
from skimage import io
import operator
import os




class Deconvolver(object):


    def __init__(self):
        self.PSFGenConfigPath = "../config/PSFGenerator_psf_config.txt"
        self.FlowdecPSFConfigPath = "../config/Flowdec_psf_config.json"
        self.JVM_HEAP_MEMORY_MB = 40000
        self.theoreticalPSFAccuracy = "Good"


    def gen_psf_PSFGenerator(self, refractiveIndexImmersion, wavelength, numericalAperture, pixelsizeXY, zStep, sizeX, sizeY, sizeZ, outputPath):

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

        accuracyLine = "psf-BW-accuracy=" + str(self.theoreticalPSFAccuracy)
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
        os.rename("../src/PSF BW.tif", outputPath + "PSFGenerator_psf.tif")
        return outputPath + "PSFGenerator_psf.tif"



    def deconvolve_DeconvLab2(self, imgStackPath, psfStackPath, iterations, outputPath):

        command = "java -Xms" + str(self.JVM_HEAP_MEMORY_MB) + "m -jar ../bin/DeconvolutionLab_2.jar Run "
        command += "-image file " + str(imgStackPath) + " "
        command += "-psf file " + str(psfStackPath) + " "
        command += "-algorithm RL " + str(iterations) + " "
        command += "-out stack noshow " + "DeconvLab2_deconvolved" + " "
        command += "-path " + str(outputPath)
        os.system(command)
        return outputPath + "DeconvLab2_deconvolved.tif"


    def crop_volume(self, img, boundingBox):

        start = tuple(map(lambda a, da: a // 2 - da // 2, img.shape, boundingBox))
        end = tuple(map(operator.add, start, boundingBox))
        slices = tuple(map(slice, start, end))
        return img[slices]








"""
dc = Deconvolver()
# Gen psf
dc.gen_psf_PSFGenerator(1.33, "Good", 530, 0.5, 180, 700, 1440, 1080, 110, "../scans/")
dc.gen_psf_Flowdec(0.5,530,110,1440,1080, "../scans/")
# deconvolve
dc.deconvolve_DeconvLab2("../scans/scan1/scan1.tif", "../scans/PSFGenerator_psf.tif", 50, "../scans/")
dc.deconvolve_Flowdec("../scans/scan1/scan1.tif", "../scans/Flowdec_psf.tif", 50, "../scans/")
"""


"""
    This block is for chunking. Doesn't work right yet. Leaving for later.




def deconvChunk(self, chunk):

    # note that algo and cropped_kernel are from global scope ... ugly
    print("chunk shape", chunk.shape)
    tmp = algo.initialize().run(fd_data.Acquisition(data=chunk, kernel=croppedPSFStack), 200)
    return tmp.data


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






