import matplotlib.pyplot as plt
import random
import numpy as np
from openslide import open_slide, __library_version__ as openslide_version
import os
from PIL import Image
import pathlib
from skimage.color import rgb2gray
from google.colab import drive

def read_slide(slide, x, y, level, width, height, as_float=False):
	"""
	function: read_slide => array with shape (height, width, 3)
	inputs: (x, y) => the coordinate of the top-left point
	        level => zoom level
	        width => output width
	        height => output hight
	        as_float => whether return array with float
	"""
	im = slide.read_region((x,y), level, (width, height))
	im = im.convert('RGB') # drop the alpha channel
	if as_float:
		im = np.asarray(im, dtype=np.float32)
	else:
	    im = np.asarray(im)
	assert im.shape == (height, width, 3)
	return im

def find_tissue_pixels(image, intensity=0.8):
	"""
	function: image => (indices 0, indices 1), the location of tissue pixels

	"""
	im_gray = rgb2gray(image)
	assert im_gray.shape == (image.shape[0], image.shape[1])
	indices = np.where(im_gray <= intensity) # the darker the more likely to be tissue
	return zip(indices[0], indices[1])
  
def apply_mask(im, mask, color=(255,0,0)):
    masked = np.copy(im)
    for x,y in mask: 
      masked[x][y] = color
    return masked

def center_tumor_check(mask, center_size = 128, patch_size = 299):
 	gap = (patch_size - center_size) // 2
 	return np.sum(mask[gap : gap + center_size, gap : gap + center_size]) > 0


def generate_patch_random(image_slide, mask_slide, base_level=4, level=0, x=None, y=None, patch_size=299):

    slide_image = read_slide(image_slide, 
                0, 
                0, 
                level, 
                width=mask_slide.level_dimensions[base_level][0], 
                height=mask_slide.level_dimensions[base_level][1])
    downsample = image_slide.level_downsamples[base_level]
    if x is None:
        x = np.random.randint(0, slide_image.shape[1] - patch_size)
    if y is None:
	    y = np.random.randint(0, slide_image.shape[0] - patch_size)
    patch_image = read_slide(image_slide, 
		                     x=int(x*downsample-patch_size//2 * image_slide.level_downsamples[level]),
		                     y=int(y*downsample-patch_size//2 * image_slide.level_downsamples[level]),
		                     level=level,
		                     width=patch_size,
		                     height=patch_size)
    patch_image_mask = read_slide(mask_slide, 
		                     x=int(x*downsample-patch_size//2 * image_slide.level_downsamples[level]),
		                     y=int(y*downsample-patch_size//2 * image_slide.level_downsamples[level]),
		                     level=level,
		                     width=patch_size,
		                     height=patch_size)
    return patch_image, patch_image_mask
