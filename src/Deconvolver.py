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
imageStack = io.imread('../scans/scan1/scan1.tif')
psfStack = io.imread('../scans/scan1/PSF_BW_Z55.tif')
chunkSize = (55,250,250)
padding = (20,40,40)


# Crop Image Stack
croppedImageStack = cropND(imageStack, (110, 500, 500))
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







