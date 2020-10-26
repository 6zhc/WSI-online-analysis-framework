import cv2
import math
import numpy
import openslide
import os
import pandas

from Controller import manifest_controller

Patient_data = pandas.read_csv("tcga_info.csv")

Original_data_root = "Data/Original_data/"
Analysis_data_root = "Data/analysis_data/"

Patient_ID_column = "bcr_patient_barcode"

Predict_file = [
    "/home5/hby/subtype/5slide_tcga_be.csv",
    "/home5/hby/subtype/5slide_tcga_re.csv",
    "/home5/hby/subtype/1slide_tcga_be.csv",
    "/home5/hby/subtype/1slide_f2.csv",
    "/home5/hby/subtype/1slide_f1.csv"
]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def save_data(old_files_name, old_mask_region, old_mask_type, predict_file_name):
    if old_files_name != "":
        slide_inform = manifest_controller.get_project_by_similar_svs_file(old_files_name)[0]
        analysis_data_folder = Analysis_data_root + slide_inform[1] + '/'
        if not os.path.exists("test_Data"):
            os.mkdir("test_Data")
        if not os.path.exists(analysis_data_folder):
            os.mkdir(analysis_data_folder)

        sub = ["Cancer", "Health", ]
        result_sub = [0, 0]
        for i in range(2):
            result_sub[i] = numpy.sum(old_mask_region[:, :, i] != 0)
        result_sub_sum = numpy.sum(result_sub)
        summary_region = ""
        for i in range(2):
            result_sub[i] = round(result_sub[i] / result_sub_sum * 100, 2)
            summary_region = summary_region + sub[i] + ":" + str(result_sub[i]) + "%_"
            summary_region = summary_region[:-1]

        cv2.imwrite(analysis_data_folder + predict_file_name + '_' + summary_region + ".png", old_mask_region)
        # alpha = old_mask_region[:, :, 3].copy()
        old_mask_region[:, :, 1:] = 0
        old_mask_region = cv2.blur(old_mask_region, (20, 20))
        old_mask_region = cv2.applyColorMap(old_mask_region[:, :, 0], cv2.COLORMAP_JET)
        # b_channel, g_channel, r_channel = cv2.split(old_mask_region)
        # old_mask_region = cv2.merge((b_channel, g_channel, r_channel, alpha))
        cv2.imwrite(analysis_data_folder + predict_file_name + '_' + "mask_region.png", old_mask_region)

        sub = ["ccRCC", "pRCC", "chRCC"]
        result_sub = [0, 0, 0]
        for i in range(3):
            result_sub[i] = numpy.sum(old_mask_type[:, :, i] != 0)
        result_sub_sum = numpy.sum(result_sub)
        summary_type = ""
        for i in range(3):
            result_sub[i] = round(result_sub[i] / result_sub_sum * 100, 2)
            summary_type = summary_type + sub[i] + ":" + str(result_sub[i]) + "%_"
            summary_type = summary_type[:-1]

        cv2.imwrite(analysis_data_folder + predict_file_name + "_" + summary_type + ".png", old_mask_type)

        for index_temp in range(len(Patient_data[Patient_ID_column])):
            if old_files_name.find(Patient_data[Patient_ID_column][index_temp]) != -1:
                Patient_data["result_" + predict_file_name][index_temp] += sub[numpy.argmax(result_sub)] + " " \
                                                                           + summary_region + " " + summary_type + "; "
        Patient_data.to_csv("test_predict_wjl.csv")
        print(old_files_name)


if __name__ == '__main__':
    for predict_file_url in Predict_file:
        predict_file_name = predict_file_url.split("/")[-1][:-4]
        Patient_data["result_" + predict_file_name] = ""
        csv_data = pandas.read_csv(predict_file_url)
        files = []
        x = []
        y = []
        size = []
        for item in csv_data["filename"]:
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
                save_data(old_files_name, old_mask_region, old_mask_type, predict_file_name)
                old_files_name = files[index]
                slide_inform = manifest_controller.get_project_by_similar_svs_file(files[index])[0]

                original_data_folder = Original_data_root + slide_inform[1] + '/'

                svs_file = original_data_folder + slide_inform[2]
                oslide = openslide.OpenSlide(svs_file)

                w, h = oslide.dimensions
                old_mask_region = numpy.zeros((int(h / 100), int(w / 100), 4), dtype=numpy.uint8)
                old_mask_type = numpy.zeros((int(h / 100), int(w / 100), 4), dtype=numpy.uint8)

            times = int(size[index] / 100)
            region_predict = (int(255 - sigmoid(float(csv_data["normal"][index])) * 255),
                              int(sigmoid(float(csv_data["normal"][index])) * 255))

            type_predict = (int(sigmoid(float(csv_data["ccrcc"][index])) * 255),
                            int(sigmoid(float(csv_data["prcc"][index])) * 255),
                            int(sigmoid(float(csv_data["chrcc"][index])) * 255))
            if region_predict[0] > region_predict[1]:
                old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
                int(x[index] / 100):int(x[index] / 100 + times), 0] \
                    = region_predict[0]
                old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
                int(x[index] / 100):int(x[index] / 100 + times), 3] \
                    = 255
                old_mask_type[int(y[index] / 100):int(y[index] / 100 + times),
                int(x[index] / 100):int(x[index] / 100 + times),
                numpy.argmax(type_predict)] \
                    = type_predict[int(numpy.argmax(type_predict))]
                old_mask_type[int(y[index] / 100):int(y[index] / 100 + times),
                int(x[index] / 100):int(x[index] / 100 + times),
                3] \
                    = 255

            else:
                old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
                int(x[index] / 100):int(x[index] / 100 + times), 1] \
                    = region_predict[1]
                old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
                int(x[index] / 100):int(x[index] / 100 + times), 3] \
                    = 255

        save_data(old_files_name, old_mask_region, old_mask_type, predict_file_name)
