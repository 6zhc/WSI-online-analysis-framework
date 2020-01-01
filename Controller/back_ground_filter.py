# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 16:03:45 2019

@author: ZeyuGao
"""
import cv2
import openslide
from PIL import Image


def generate_smaller_image_from_svs_file(svs_file_path, output_file_path):
    oslide = openslide.OpenSlide(svs_file_path)
    level = oslide.level_count - 1
    w, h = oslide.level_dimensions[level]
    if level < 1:
        print(svs_file_path)
        oslide.close()
        patch = oslide.read_region((0, 0), 0, (w, h))
        patch = patch.resize((int(w / 32), int(h / 32)), Image.ANTIALIAS)
    else:
        patch = oslide.read_region((0, 0), level, (w, h))
    patch.save(output_file_path)
    oslide.close()


def generate_binary_mask_from_smaller_image(smaller_image_path, output_file_path):
    img = cv2.imread(smaller_image_path)
    # img = cv2.cvtColor(np.asarray(patch),cv2.COLOR_RGB2GRAY)
    img = cv2.GaussianBlur(img, (61, 61), 0)
    ret, img_filtered = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(output_file_path, img_filtered)
