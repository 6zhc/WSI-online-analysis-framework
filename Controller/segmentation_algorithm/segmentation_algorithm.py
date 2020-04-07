# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 16:04:05 2019

@author: Raytine
"""
import skimage.io as io
import skimage.transform as trans
from segmentation_models import Unet
import cv2 as cv
import numpy as np


class SegmentationModel(object):

    def __init__(self, model_path='models/unet_MoNuSeg.hdf5', target_size=(512, 512)):
        self.target_size = target_size
        ## build model
        self.model = Unet('resnet34', input_shape=(512, 512, 3))
        ## load weights
        self.model.load_weights(model_path, skip_mismatch=True, by_name=True)

    def predict(self, image_path):
        '''
        input:
        1. image_path
            str
        return:
        1. mask_pred
            np.array('float32')
            512*512
        tips:
            must use io.imread, model is trained with io.imread image.
            cv.imread is different from io.imread. Could cause a wrong predict.
        '''
        image = io.imread(image_path)
        if image.shape[-1] > 3:
            image = image[:, :, :-1]
        image = trans.resize(image, self.target_size)
        image = image.reshape((1,) + image.shape)
        mask_pred = self.model.predict(image)
        mask_pred = mask_pred.reshape(mask_pred.shape[1:-1])
        return mask_pred

    def water_image(self, mask, thresh=0.3):
        '''
        input:
        1. mask
            np.array('float32')
            512*512
        2. thresh : control the sensitivity of seed.
            float
        return:
        1. markers
            np.array('int32')
            512*512
            -1 indicates boundary
        '''
        mask = mask * 255
        mask = mask.astype('uint8')
        # gray\binary image
        gray = mask
        ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
        # morphology operation
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
        mb = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv.dilate(mb, kernel, iterations=3)
        # distance transform
        dist = cv.distanceTransform(mb, cv.DIST_L2, 3)
        ret, surface = cv.threshold(dist, dist.max() * thresh, 255, cv.THRESH_BINARY)
        surface_fg = np.uint8(surface)
        unknown = cv.subtract(sure_bg, surface_fg)
        ret, markers = cv.connectedComponents(surface_fg)
        # watershed transfrom
        markers += 1
        markers[unknown == 255] = 0
        mask = mask.reshape(mask.shape + (1,))
        mask = np.concatenate((mask, mask, mask), axis=2)
        markers = cv.watershed(mask, markers=markers)
        #        mask[markers == -1] = [0, 0, 255]
        return markers


def water_image(mask, thresh=0.3):
    '''
    input:
    1. mask
        np.array('float32')
        512*512
    2. thresh : control the sensitivity of seed.
        float
    return:
    1. markers
        np.array('int32')
        512*512
        -1 indicates boundary
    '''
    mask = mask * 255
    mask = mask.astype('uint8')
    # gray\binary image
    gray = mask
    ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    # morphology operation
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    mb = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel, iterations=2)
    sure_bg = cv.dilate(mb, kernel, iterations=3)
    # distance transform
    dist = cv.distanceTransform(mb, cv.DIST_L2, 3)
    ret, surface = cv.threshold(dist, dist.max() * thresh, 255, cv.THRESH_BINARY)
    surface_fg = np.uint8(surface)
    unknown = cv.subtract(sure_bg, surface_fg)
    ret, markers = cv.connectedComponents(surface_fg)
    # watershed transfrom
    markers += 1
    markers[unknown == 255] = 0
    mask = mask.reshape(mask.shape + (1,))
    mask = np.concatenate((mask, mask, mask), axis=2)
    markers = cv.watershed(mask, markers=markers)
    #        mask[markers == -1] = [0, 0, 255]
    return markers
