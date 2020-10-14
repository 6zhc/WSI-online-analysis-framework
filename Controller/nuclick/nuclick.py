from time import time

import numpy as np
import tensorflow as tf
from skimage import exposure
from skimage.filters import gaussian
from skimage.morphology import remove_small_objects, remove_small_holes, reconstruction, disk

from Controller.nuclick.data_handler.customImageGenerator import ImageDataGenerator
from Controller.nuclick.models.models import getModel

seeddd = 1
img_rows = 128
img_cols = 128
img_chnls = 3
input_shape = (img_rows, img_cols)
Thresh = 0.5
minSize = 10
minHole = 30
bb = img_rows
testTimeAug = False
testTimeJittering = 'PointJiterring'

weights_path = './'


def gen_mask(dot, image):
    modelType = 'MultiScaleResUnet'
    lossType = 'complexBCEweighted'
    # modelBaseName = 'NuClick_%s_%s_%s' % ('Nucleus', modelType, lossType)
    # modelSaveName = "%s/weights-%s.h5" % (weights_path, modelBaseName)
    modelSaveName = "/home1/zhc/nuClick/weights-NuClick_Nucleus_MultiScaleResUnet_complexBCEweighted.h5"

    graph = tf.Graph()
    with graph.as_default():
        session = tf.Session()
        with session.as_default():

            # loading models
            model = getModel(modelType, lossType, input_shape)
            model.load_weights(modelSaveName)

            ##Reading images
            img = image[:, :, ::-1]
            dot = dot.astype(np.int32)
            cx = dot[:, 0]
            cy = dot[:, 1]
            # imgPath = image_path
            m, n = img.shape[0:2]
            clickMap, boundingBoxes = getClickMapAndBoundingBox(cx, cy, m, n)
            patchs, nucPoints, otherPoints = getPatchs(img, clickMap, boundingBoxes, cx, cy, m, n)
            dists = np.float32(np.concatenate((nucPoints, otherPoints, otherPoints), axis=3))
            # the last one is only dummy!

            # prediction with test time augmentation
            predNum = 0  # augNum*numModel
            preds = np.zeros((len(patchs), img_rows, img_cols), dtype=np.float32)
            starttime = time()
            preds += predictPatchs(model, patchs, dists, testTimeJittering)
            print("=====" + str(time() - starttime))
            predNum += 1
            # print("Original images prediction, DONE!")
            if testTimeAug:
                # print("Test Time Augmentation Started")
                # sharpenning the image
                patchs_shappened = patchs.copy()
                for i in range(len(patchs)):
                    patchs_shappened[i] = sharpnessEnhancement(patchs[i])
                temp = predictPatchs(model, patchs_shappened[:, :, ::-1], dists[:, :, ::-1], testTimeJittering)
                preds += temp[:, :, ::-1]
                predNum += 1
                # print("Sharpenned images prediction, DONE!")

                # contrast enhancing the image
                patchs_contrasted = patchs.copy()
                for i in range(len(patchs)):
                    patchs_contrasted[i] = contrastEnhancement(patchs[i])
                temp = predictPatchs(model, patchs_contrasted[:, ::-1, ::-1], dists[:, ::-1, ::-1], testTimeJittering)
                preds += temp[:, ::-1, ::-1]
                predNum += 1
                # print("Contrasted images prediction, DONE!")
            preds /= predNum
            try:
                masks = postProcessing(preds, thresh=Thresh, minSize=minSize, minHole=minHole, doReconstruction=True,
                                       nucPoints=nucPoints)
            except:
                masks = postProcessing(preds, thresh=Thresh, minSize=minSize, minHole=minHole, doReconstruction=False,
                                       nucPoints=nucPoints)
            instanceMap = generateInstanceMap(masks, boundingBoxes, m, n)

            session.close()

    return instanceMap


# utils
def getClickMapAndBoundingBox(cx, cy, m, n):
    clickMap = np.zeros((m, n), dtype=np.uint8)

    # Removing points out of image dimension (these points may have been clicked unwanted)
    cx_out = [x for x in cx if x >= n]
    cx_out_index = [cx.index(x) for x in cx_out]

    cy_out = [x for x in cy if x >= m]
    cy_out_index = [cy.index(x) for x in cy_out]

    indexes = cx_out_index + cy_out_index
    cx = np.delete(cx, indexes)
    cx = cx.tolist()
    cy = np.delete(cy, indexes)
    cy = cy.tolist()

    clickMap[cy, cx] = 1
    boundingBoxes = []
    for i in range(len(cx)):
        xStart = cx[i] - bb // 2
        yStart = cy[i] - bb // 2
        if xStart < 0:
            xStart = 0
        if yStart < 0:
            yStart = 0
        xEnd = xStart + bb - 1
        yEnd = yStart + bb - 1
        if xEnd > n - 1:
            xEnd = n - 1
            xStart = xEnd - bb + 1
        if yEnd > m - 1:
            yEnd = m - 1
            yStart = yEnd - bb + 1
        boundingBoxes.append([xStart, yStart, xEnd, yEnd])
    return clickMap, boundingBoxes


def getPatchs(img, clickMap, boundingBoxes, cx, cy, m, n):
    total = len(boundingBoxes)
    img = np.array([img])
    clickMap = np.array([clickMap])
    clickMap = clickMap[..., np.newaxis]
    patchs = np.ndarray((total, bb, bb, 3), dtype=np.uint8)
    nucPoints = np.ndarray((total, bb, bb, 1), dtype=np.uint8)
    otherPoints = np.ndarray((total, bb, bb, 1), dtype=np.uint8)
    cx_out = [x for x in cx if x >= n]
    cx_out_index = [cx.index(x) for x in cx_out]

    cy_out = [x for x in cy if x >= m]
    cy_out_index = [cy.index(x) for x in cy_out]

    indexes = cx_out_index + cy_out_index
    cx = np.delete(cx, indexes)
    cx = cx.tolist()
    cy = np.delete(cy, indexes)
    cy = cy.tolist()
    for i in range(len(boundingBoxes)):
        boundingBox = boundingBoxes[i]
        xStart = boundingBox[0]
        yStart = boundingBox[1]
        xEnd = boundingBox[2]
        yEnd = boundingBox[3]
        patchs[i] = img[0, yStart:yEnd + 1, xStart:xEnd + 1, :]
        thisClickMap = np.zeros((1, m, n, 1), dtype=np.uint8)
        thisClickMap[0, cy[i], cx[i], 0] = 1
        othersClickMap = np.uint8((clickMap - thisClickMap) > 0)
        nucPoints[i] = thisClickMap[0, yStart:yEnd + 1, xStart:xEnd + 1, :]
        otherPoints[i] = othersClickMap[0, yStart:yEnd + 1, xStart:xEnd + 1, :]
    return patchs, nucPoints, otherPoints


def _unsharp_mask_single_channel(image, radius, amount):
    """Single channel implementation of the unsharp masking filter."""
    blurred = gaussian(image, sigma=radius, mode='reflect')
    result = image + (image - blurred) * amount
    result = np.clip(result, 0, 1)
    return result


def sharpnessEnhancement(imgs):  # needs the input to be in range of [0,1]
    imgs_out = imgs.copy()
    for channel in range(imgs_out.shape[-1]):
        imgs_out[..., channel] = 255 * _unsharp_mask_single_channel(imgs_out[..., channel] / 255., 2, .5)
    return imgs_out


def contrastEnhancement(imgs):  # needs the input to be in range of [0,255]
    imgs_out = imgs.copy()
    p2, p98 = np.percentile(imgs_out, (2, 98))  #####
    if p2 == p98:
        p2, p98 = np.min(imgs_out), np.max(imgs_out)
    if p98 > p2:
        imgs_out = exposure.rescale_intensity(imgs_out, in_range=(p2, p98), out_range=(0., 255.))
    return imgs_out


def predictPatchs(model, patchs, dists, clickPrtrb='PointJiterring'):
    num_val = len(patchs)
    image_datagen_val = ImageDataGenerator(RandomizeGuidingSignalType=clickPrtrb, rescale=1. / 255)
    batchSizeVal = 128
    val_generator = image_datagen_val.flow(
        patchs, weightMap=dists,
        shuffle=False,
        batch_size=batchSizeVal,
        color_mode='rgb',
        seed=seeddd)
    print('patch_num: ' + str(num_val))
    preds = model.predict_generator(val_generator, steps=(num_val - 1) // batchSizeVal + 1)
    # print(preds)
    # print(preds.shape)
    # preds = preds.reshape(preds.shape[0]*preds.shape[1], )
    preds = np.matrix.squeeze(preds, axis=3)
    return preds


def postProcessing(preds, thresh=0.33, minSize=10, minHole=30, doReconstruction=False, nucPoints=None):
    masks = preds > thresh
    masks = remove_small_objects(masks, min_size=minSize)
    masks = remove_small_holes(masks, area_threshold=minHole)
    if doReconstruction:
        for i in range(len(masks)):
            thisMask = masks[i]
            thisMarker = nucPoints[i, :, :, 0] > 0
            try:
                thisMask = reconstruction(thisMarker, thisMask, selem=disk(1))
                masks[i] = np.array([thisMask])
            except:
                warnings.warn('Nuclei reconstruction error #' + str(i))
    return masks


def generateInstanceMap(masks, boundingBoxes, m, n):
    instanceMap = np.zeros((m, n), dtype=np.uint16)
    for i in range(len(masks)):
        thisBB = boundingBoxes[i]
        thisMaskPos = np.argwhere(masks[i] > 0)
        thisMaskPos[:, 0] = thisMaskPos[:, 0] + thisBB[1]
        thisMaskPos[:, 1] = thisMaskPos[:, 1] + thisBB[0]
        instanceMap[thisMaskPos[:, 0], thisMaskPos[:, 1]] = i + 1
    return instanceMap
