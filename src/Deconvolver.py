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


#os.system("echo {""na"": 0.75, ""wavelength"": 0.425, ""size_z"": 32, ""size_x"": 64, ""size_y"": 64} > ../scans/psf.json")


def cropND(img, bounding):

    start = tuple(map(lambda a, da: a//2-da//2, img.shape, bounding))
    end = tuple(map(operator.add, start, bounding))
    slices = tuple(map(slice, start, end))
    return img[slices]

def deconv(chunk):

    # note that algo and cropped_kernel are from global scope ... ugly
    print("chunk shape", chunk.shape)
    tmp = algo.initialize().run(fd_data.Acquisition(data=chunk, kernel=croppedPSFStack), 200)
    return tmp.data


# Load data and define chunk size
imageStack = io.imread('../scans/scan1/scan1_cropped.tif')
psf = fd_psf.GibsonLanni.load('../scans/psf.json')
psfStack = psf.generate()
#psfStack = io.imread('../scans/scan1/PSF_BW_Z55.tif')

# Crop Image Stack
#croppedImageStack = cropND(imageStack, (20, 700, 700))

algo = RichardsonLucyDeconvolver(imageStack.ndim).initialize()
resultStack = algo.run(fd_data.Acquisition(data=imageStack, kernel=psfStack), niter=40).data

io.imsave('../scans/ORIGINAL.tif', imageStack)
io.imsave('../scans/DECONVOLVED.tif', resultStack)











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






