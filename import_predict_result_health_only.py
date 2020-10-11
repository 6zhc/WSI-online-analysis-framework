import pandas, os, math
import openslide, numpy
import cv2
from Controller import manifest_controller

tcga_data = pandas.read_csv("test_predict.csv")

original_data_root = "Data/Original_data/"
analysis_data_root = "Data/analysis_data/"

predict_file = [
    "/home1/gzy/Subtype/SSLDataIndex/0.5/f2_testwsi_crd_details.csv",
    "/home1/gzy/Subtype/SSLDataIndex/0.5/fully_testwsi_crd_details.csv",
    "/home1/gzy/Subtype/SSLDataIndex/0.5/meta_testwsi_crd_details.csv"
]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def save_data(old_files_name, old_mask_region, predict_file_name):
    if old_files_name != "":
        slide_inform = manifest_controller.get_project_by_similar_svs_file(old_files_name)[0]
        analysis_data_folder = analysis_data_root + slide_inform[1] + '/'
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
        old_mask_region[:, :, 1:] = 0
        old_mask_region = cv2.blur(old_mask_region, (20, 20))
        old_mask_region = cv2.applyColorMap(old_mask_region[:, :, 0], cv2.COLORMAP_JET)
        cv2.imwrite(analysis_data_folder + predict_file_name + '_' + summary_region + "mask_region.png",
                    old_mask_region)

        for index_temp in range(len(tcga_data["bcr_patient_barcode"])):
            if old_files_name.find(tcga_data["bcr_patient_barcode"][index_temp]) != -1:
                tcga_data["result_" + predict_file_name][index_temp] += summary_region + "; "
        tcga_data.to_csv("test_predict_region_only.csv")
        print(old_files_name)


for predict_file_url in predict_file:
    predict_file_name = predict_file_url.split("/")[-1][:-4]
    tcga_data["result_" + predict_file_name] = ""
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

    for index in range(len(files)):
        # print(index, old_files_name)
        if files[index] != old_files_name:
            save_data(old_files_name, old_mask_region, predict_file_name)
            old_files_name = files[index]
            slide_inform = manifest_controller.get_project_by_similar_svs_file(files[index])[0]

            original_data_folder = original_data_root + slide_inform[1] + '/'

            svs_file = original_data_folder + slide_inform[2]
            oslide = openslide.OpenSlide(svs_file)

            w, h = oslide.dimensions
            old_mask_region = numpy.zeros((int(h / 100), int(w / 100), 4), dtype=numpy.uint8)

        times = int(size[index] / 100)
        region_predict = (int((float(csv_data["cancer_prob"][index])) * 255),
                          int((1 - float(csv_data["cancer_prob"][index])) * 255))

        if region_predict[0] > region_predict[1]:
            old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
            int(x[index] / 100):int(x[index] / 100 + times), 0] \
                = region_predict[0]
            old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
            int(x[index] / 100):int(x[index] / 100 + times), 3] \
                = 255
        else:
            old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
            int(x[index] / 100):int(x[index] / 100 + times), 1] \
                = region_predict[1]
            old_mask_region[int(y[index] / 100):int(y[index] / 100 + times),
            int(x[index] / 100):int(x[index] / 100 + times), 3] \
                = 255

    save_data(old_files_name, old_mask_region, predict_file_name)

    # print(files)
    # print(x)
    # print(y)
    # print(size)
