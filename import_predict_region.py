import cv2
import math
import numpy
import openslide
import os
import pandas
import random

from Controller import manifest_controller

Patient_data = pandas.read_csv("tcga_info.csv")

Original_data_root = "Data/Original_data/"
Analysis_data_root = "Data/analysis_data/"

Patient_ID_column = "bcr_patient_barcode"

Predict_file = [
    "/home1/zhc/cancer_Prcc.txt"
]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def save_data(old_files_name, old_mask_region, predict_file_name):
    if old_files_name != "":
        slide_inform = manifest_controller.get_project_by_similar_svs_file(old_files_name)[0]
        analysis_data_folder = Analysis_data_root + slide_inform[1] + '/'
        if not os.path.exists("test_Data"):
            os.mkdir("test_Data")
        if not os.path.exists(analysis_data_folder):
            os.mkdir(analysis_data_folder)

        result_sub = numpy.sum(old_mask_region[:, :, 1] != 0)
        cv2.imwrite(analysis_data_folder + predict_file_name + '_' + str(result_sub) + ".png", old_mask_region)

        for index_temp in range(len(Patient_data[Patient_ID_column])):
            if old_files_name.find(Patient_data[Patient_ID_column][index_temp]) != -1:
                Patient_data["result_" + predict_file_name][index_temp] += "region_number:" + str(result_sub)
        Patient_data.to_csv("test_predict_hby.csv")
        print(old_files_name)


if __name__ == '__main__':
    for predict_file_url in Predict_file:
        predict_file_name = predict_file_url.split("/")[-1][:-4]
        Patient_data["result_" + predict_file_name] = ""
        f = open(predict_file_url)
        lines = f.readlines()

        files = []
        x = []
        y = []
        size = []
        for item in lines:
            files.append(item.split("/")[-2].split("_")[0])
            x_temp, y_temp, size_temp = item.split("/")[-1].split(".")[0].split("_")
            x.append(int(x_temp))
            y.append(int(y_temp))
            size.append(int(size_temp))

        old_files_name = ""
        old_mask_region = None
        old_mask_type = None

        for index in range(len(files)):
            # print(index, old_files_name)
            if files[index] != old_files_name:
                save_data(old_files_name, old_mask_region, predict_file_name)
                old_files_name = files[index]
                slide_inform = manifest_controller.get_project_by_similar_svs_file(files[index])[0]

                original_data_folder = Original_data_root + slide_inform[1] + '/'

                svs_file = original_data_folder + slide_inform[2]
                oslide = openslide.OpenSlide(svs_file)

                w, h = oslide.dimensions
                old_mask_region = numpy.zeros((int(h / 100), int(w / 100), 4), dtype=numpy.uint8)

            times = int(size[index] / 100)

            old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
            int(x[index] / 100):int(x[index] / 100 + times), 1] \
                = 255
            old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
            int(x[index] / 100):int(x[index] / 100 + times), 3] \
                = 255

        save_data(old_files_name, old_mask_region, predict_file_name)
