import pandas, os, math
import openslide, numpy
import cv2
from Controller import manifest_controller

tcga_data = pandas.read_csv("test.csv")
tcga_data["predict_result"] = ""

original_data_root = "Data/Original_data/"
analysis_data_root = "Data/analysis_data/"


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def save_data(old_files_name, old_mask_region, old_mask_type):
    if old_files_name != "":
        slide_inform = manifest_controller.get_project_by_similar_svs_file(old_files_name)[0]
        analysis_data_folder = analysis_data_root + slide_inform[1] + '/'
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

        cv2.imwrite(analysis_data_folder + predict_file + '_' + summary_region + ".png", old_mask_region)
        # alpha = old_mask_region[:, :, 3].copy()
        old_mask_region[:, :, 1:] = 0
        old_mask_region = cv2.blur(old_mask_region, (20, 20))
        old_mask_region = cv2.applyColorMap(old_mask_region[:, :, 0], cv2.COLORMAP_JET)
        # b_channel, g_channel, r_channel = cv2.split(old_mask_region)
        # old_mask_region = cv2.merge((b_channel, g_channel, r_channel, alpha))
        cv2.imwrite(analysis_data_folder + predict_file + '_' + "mask_region.png", old_mask_region)

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

        cv2.imwrite(analysis_data_folder + predict_file + "_" + summary_type + ".png", old_mask_type)

        for index_temp in range(len(tcga_data["bcr_patient_barcode"])):
            if old_files_name.find(tcga_data["bcr_patient_barcode"][index_temp]) != -1:
                tcga_data["predict_result"][index_temp] += summary_region + " " + summary_type + "; "
        tcga_data.to_csv("test_predict.csv")
        print(old_files_name)


predict_file = "tcga_result_details"
csv_data = pandas.read_csv(predict_file + ".csv")
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
        save_data(old_files_name, old_mask_region, old_mask_type)
        old_files_name = files[index]
        slide_inform = manifest_controller.get_project_by_similar_svs_file(files[index])[0]

        original_data_folder = original_data_root + slide_inform[1] + '/'

        svs_file = original_data_folder + slide_inform[2]
        oslide = openslide.OpenSlide(svs_file)

        w, h = oslide.dimensions
        old_mask_region = numpy.zeros((int(h / 100), int(w / 100), 4), dtype=numpy.uint8)
        old_mask_type = numpy.zeros((int(h / 100), int(w / 100), 4), dtype=numpy.uint8)

    times = int(size[index] / 100)
    region_predict = (int(sigmoid(float(csv_data["cancer"][index])) * 255),
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
        numpy.argmax(type_predict[0])] \
            = type_predict[int(numpy.argmax(type_predict[0]))]
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

save_data(old_files_name, old_mask_region, old_mask_type)

# print(files)
# print(x)
# print(y)
# print(size)
