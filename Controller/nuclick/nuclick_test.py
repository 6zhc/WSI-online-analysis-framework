import sys

sys.path.append("/home1/zhc/wsi-procesing-framework/Controller/nuclick/customImageGenerator.py")

from time import time

import numpy as np
import tensorflow as tf
from skimage import exposure
from skimage.filters import gaussian
from skimage.morphology import remove_small_objects, remove_small_holes, reconstruction, disk

# sys.path.append("/home1/zhc/wsi-procesing-framework/Controller/nuclick/models.py")
# from models import getModel
# from Controller.nuclick.data_handler.customImageGenerator import ImageDataGenerator
from customImageGenerator import ImageDataGenerator
# from Controller.nuclick.models.models import getModel

import sys

sys.path.append("/home1/zhc/wsi-procesing-framework/Controller/nuclick/losses.py")

from keras.models import Model
from keras.layers import Input, concatenate, Conv2D, MaxPooling2D, Conv2DTranspose
from keras.layers import BatchNormalization, Activation
from keras.layers import Lambda, add
from keras.optimizers import Adam
from keras.regularizers import l2
from keras import backend as K
from keras.utils import multi_gpu_model
from losses import getLoss, dice_coef
import tensorflow as tf

# from config import config


multiGPU = False  # config.multiGPU
learningRate = 4e-4  # config.LearningRate

K.set_image_data_format('channels_last')  # TF dimension ordering in this code
img_chls = 3

weight_decay = 5e-5
bn_axis = -1 if K.image_data_format() == 'channels_last' else 1

'''    
##################### DEFINING MAIN BLOCKS #######################################
'''


def _conv_bn_relu(input, features=32, kernelSize=(3, 3), strds=(1, 1), actv='relu', useBias=False, useRegulizer=False,
                  dilatationRate=(1, 1), doBatchNorm=True):
    if useRegulizer:
        kernelRegularizer = l2(weight_decay)
    else:
        kernelRegularizer = None
    if actv == 'selu':
        kernel_init = 'lecun_normal'
    else:
        kernel_init = 'glorot_uniform'
    convB1 = Conv2D(features, kernelSize, strides=strds, padding='same', use_bias=useBias,
                    kernel_regularizer=kernelRegularizer, kernel_initializer=kernel_init, dilation_rate=dilatationRate)(
        input)
    if actv != 'selu' and doBatchNorm:
        convB1 = BatchNormalization(axis=bn_axis, epsilon=1.001e-5)(convB1)
    if actv != 'None':
        convB1 = Activation(actv)(convB1)
    return convB1


def multiScaleConv_block(input_map, features, sizes, dilatationRates, strds=(1, 1), actv='relu', useBias=False,
                         useRegulizer=False, isDense=True):
    if isDense:
        conv0 = _conv_bn_relu(input_map, 4 * features, 1, strds, actv, useBias, useRegulizer)
    else:
        conv0 = input_map
    conv1 = _conv_bn_relu(conv0, features, sizes[0], strds, actv, useBias, useRegulizer,
                          (dilatationRates[0], dilatationRates[0]))
    conv2 = _conv_bn_relu(conv0, features, sizes[1], strds, actv, useBias, useRegulizer,
                          (dilatationRates[1], dilatationRates[1]))
    conv3 = _conv_bn_relu(conv0, features, sizes[2], strds, actv, useBias, useRegulizer,
                          (dilatationRates[2], dilatationRates[2]))
    conv4 = _conv_bn_relu(conv0, features, sizes[3], strds, actv, useBias, useRegulizer,
                          (dilatationRates[3], dilatationRates[3]))
    output_map = concatenate([conv1, conv2, conv3, conv4], axis=bn_axis)
    if isDense:
        output_map = _conv_bn_relu(output_map, features, 3, strds, actv, useBias, useRegulizer)
        output_map = concatenate([input_map, output_map], axis=bn_axis)
    return output_map


def residual_conv(input, features=32, kernelSize=(3, 3), strds=(1, 1), actv='relu', useBias=False, useRegulizer=False,
                  dilatationRate=(1, 1)):
    if actv == 'selu':
        conv1 = _conv_bn_relu(input, features, kernelSize, strds, actv='None', useBias=useBias,
                              useRegulizer=useRegulizer, dilatationRate=dilatationRate, doBatchNorm=False)
        conv2 = _conv_bn_relu(conv1, features, kernelSize, strds, actv='None', useBias=useBias,
                              useRegulizer=useRegulizer, dilatationRate=dilatationRate, doBatchNorm=False)
    else:
        conv1 = _conv_bn_relu(input, features, kernelSize, strds, actv='None', useBias=useBias,
                              useRegulizer=useRegulizer, dilatationRate=dilatationRate, doBatchNorm=True)
        conv2 = _conv_bn_relu(conv1, features, kernelSize, strds, actv='None', useBias=useBias,
                              useRegulizer=useRegulizer, dilatationRate=dilatationRate, doBatchNorm=True)
    out = add([conv1, conv2])
    out = Activation(actv)(out)
    return out


'''    
##################### DEFINING NETWORKS #######################################
'''


def get_MultiScale_ResUnet(input_shape, lossType):
    if multiGPU:
        with tf.device("/cpu:0"):
            img = Input(input_shape + (img_chls,), name='main_input')  # size: 1024
            auxInput = Input(input_shape + (3,), name='dists_input')
            weights = Lambda(lambda x: x[:, :, :, 2])(auxInput)
            dists = Lambda(lambda x: x[:, :, :, 0:2])(auxInput)

            inputs = concatenate([img, dists], axis=bn_axis)

            conv1 = _conv_bn_relu(inputs, 64, 7)  # 128
            conv1 = _conv_bn_relu(conv1, 32, 5)
            conv1 = _conv_bn_relu(conv1, 32, 3)
            pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

            conv2 = residual_conv(pool1, features=64)  # 64*64
            conv2 = residual_conv(conv2, features=64)
            pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

            conv3 = residual_conv(pool2, features=128)  # 32*32
            conv3 = multiScaleConv_block(conv3, 32, sizes=[3, 3, 5, 5], dilatationRates=[1, 3, 3, 6],
                                         isDense=False)  # FOV = [3,7,13,25]
            conv3 = residual_conv(conv3, features=128)
            pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

            conv4 = residual_conv(pool3, features=256)  # 16*16
            conv4 = residual_conv(conv4, features=256)
            conv4 = residual_conv(conv4, features=256)
            pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)

            conv5 = residual_conv(pool4, features=512)  # 8*8
            conv5 = residual_conv(conv5, features=512)
            conv5 = residual_conv(conv5, features=512)
            pool5 = MaxPooling2D(pool_size=(2, 2))(conv5)

            conv51 = residual_conv(pool5, features=1024)  # 8*8
            conv51 = residual_conv(conv51, features=1024)

            up61 = concatenate([Conv2DTranspose(512, 2, strides=(2, 2), padding='same')(conv51), conv5], axis=3)
            conv61 = residual_conv(up61, features=512)  # 16*16
            conv61 = residual_conv(conv61, features=256)

            up6 = concatenate([Conv2DTranspose(256, 2, strides=(2, 2), padding='same')(conv61), conv4], axis=3)
            conv6 = residual_conv(up6, features=256)  # 16*16
            conv6 = multiScaleConv_block(conv6, 64, sizes=[3, 3, 5, 5], dilatationRates=[1, 3, 2, 3],
                                         isDense=False)  # FOV = [3,7,9,13]
            conv6 = residual_conv(conv6, features=256)

            up7 = concatenate([Conv2DTranspose(128, 2, strides=(2, 2), padding='same')(conv6), conv3], axis=3)
            conv7 = residual_conv(up7, features=128)  # 32*32
            conv7 = residual_conv(conv7, features=128)

            up8 = concatenate([Conv2DTranspose(64, 2, strides=(2, 2), padding='same')(conv7), conv2], axis=3)
            conv8 = residual_conv(up8, features=64)  # 64*64
            conv8 = multiScaleConv_block(conv8, 16, sizes=[3, 3, 5, 7], dilatationRates=[1, 3, 3, 6],
                                         isDense=False)  # FOV = [3,7,13,37]
            conv8 = residual_conv(conv8, features=64)

            up9 = concatenate([Conv2DTranspose(32, 2, strides=(2, 2), padding='same')(conv8), conv1], axis=3)
            conv9 = _conv_bn_relu(up9, 64)
            conv9 = _conv_bn_relu(conv9, 32)
            conv9 = _conv_bn_relu(conv9, 32)

            conv10 = Conv2D(1, (1, 1), activation='sigmoid')(conv9)

            model = Model(inputs=[img, auxInput], outputs=[conv10])

            model = multi_gpu_model(model, 2)
            model.compile(optimizer=Adam(lr=learningRate), loss=getLoss(lossType, weightMap=weights),
                          metrics=[dice_coef])  # adding the momentum

            return model
    else:
        img = Input(input_shape + (img_chls,), name='main_input')  # size: 1024
        auxInput = Input(input_shape + (3,), name='dists_input')
        weights = Lambda(lambda x: x[:, :, :, 2])(auxInput)
        dists = Lambda(lambda x: x[:, :, :, 0:2])(auxInput)

        inputs = concatenate([img, dists], axis=bn_axis)

        conv1 = _conv_bn_relu(inputs, 64, 7)  # 128
        conv1 = _conv_bn_relu(conv1, 32, 5)
        conv1 = _conv_bn_relu(conv1, 32, 3)
        pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

        conv2 = residual_conv(pool1, features=64)  # 64*64
        conv2 = residual_conv(conv2, features=64)
        pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

        conv3 = residual_conv(pool2, features=128)  # 32*32
        conv3 = multiScaleConv_block(conv3, 32, sizes=[3, 3, 5, 5], dilatationRates=[1, 3, 3, 6],
                                     isDense=False)  # FOV = [3,7,13,25]
        conv3 = residual_conv(conv3, features=128)
        pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

        conv4 = residual_conv(pool3, features=256)  # 16*16
        conv4 = residual_conv(conv4, features=256)
        conv4 = residual_conv(conv4, features=256)
        pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)

        conv5 = residual_conv(pool4, features=512)  # 8*8
        conv5 = residual_conv(conv5, features=512)
        conv5 = residual_conv(conv5, features=512)
        pool5 = MaxPooling2D(pool_size=(2, 2))(conv5)

        conv51 = residual_conv(pool5, features=1024)  # 8*8
        conv51 = residual_conv(conv51, features=1024)

        up61 = concatenate([Conv2DTranspose(512, 2, strides=(2, 2), padding='same')(conv51), conv5], axis=3)
        conv61 = residual_conv(up61, features=512)  # 16*16
        conv61 = residual_conv(conv61, features=256)

        up6 = concatenate([Conv2DTranspose(256, 2, strides=(2, 2), padding='same')(conv61), conv4], axis=3)
        conv6 = residual_conv(up6, features=256)  # 16*16
        conv6 = multiScaleConv_block(conv6, 64, sizes=[3, 3, 5, 5], dilatationRates=[1, 3, 2, 3],
                                     isDense=False)  # FOV = [3,7,9,13]
        conv6 = residual_conv(conv6, features=256)

        up7 = concatenate([Conv2DTranspose(128, 2, strides=(2, 2), padding='same')(conv6), conv3], axis=3)
        conv7 = residual_conv(up7, features=128)  # 32*32
        conv7 = residual_conv(conv7, features=128)

        up8 = concatenate([Conv2DTranspose(64, 2, strides=(2, 2), padding='same')(conv7), conv2], axis=3)
        conv8 = residual_conv(up8, features=64)  # 64*64
        conv8 = multiScaleConv_block(conv8, 16, sizes=[3, 3, 5, 7], dilatationRates=[1, 3, 3, 6],
                                     isDense=False)  # FOV = [3,7,13,37]
        conv8 = residual_conv(conv8, features=64)

        up9 = concatenate([Conv2DTranspose(32, 2, strides=(2, 2), padding='same')(conv8), conv1], axis=3)
        conv9 = _conv_bn_relu(up9, 64)
        conv9 = _conv_bn_relu(conv9, 32)
        conv9 = _conv_bn_relu(conv9, 32)

        conv10 = Conv2D(1, (1, 1), activation='sigmoid')(conv9)

        model = Model(inputs=[img, auxInput], outputs=[conv10])
        # model.compile(optimizer=Adam(lr=learningRate), loss=getLoss(lossType, weightMap=weights), metrics=[dice_coef]) # adding the momentum
        model.compile(optimizer=Adam(lr=learningRate), loss='categorical_crossentropy',
                      metrics=[dice_coef])  # adding the momentum

        return model


def getModel(network, lossType, input_shape):
    if network in {'MultiScaleResUnet'}:
        return get_MultiScale_ResUnet(input_shape, lossType)
    else:
        raise ValueError('unknown network ' + network)


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
