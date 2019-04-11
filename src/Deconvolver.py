import numpy as np
import matplotlib.pyplot as plt
from skimage import exposure
from scipy import ndimage, signal
from flowdec import data as fd_data
from flowdec import restoration as fd_restoration
from skimage import io
import tensorflow as tf
import matplotlib




imageStack = io.imread('../scans/scan1/scan1.tif')
psfStack = io.imread('../scans/scan1/PSF_BW.tif')

sub_stack = imageStack[:,:,:]
sub_psf = psfStack[:,:,:]
#TODO: Create PSF with correct dimmensions using psfgenerator

algo = fd_restoration.RichardsonLucyDeconvolver(sub_stack.ndim).initialize()
session_config = tf.ConfigProto()
session_config.gpu_options.allow_growth = True
session_config.gpu_options.per_process_gpu_memory_fraction = 1.0
res = algo.run(fd_data.Acquisition(data=sub_stack, kernel=sub_psf), niter=1).data

for i in range(0,20):
    io.imsave(str(i) + '.tif', res[i,:,:])





