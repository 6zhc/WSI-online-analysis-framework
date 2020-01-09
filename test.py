from Controller import image_processing
from PIL import Image
import cv2
import numpy
from Model import mission

mask_file_name = "/home1/zhc/wsi-procesing-framework/Data/1b9b7ce6-7dad-4fac-a573-dcbf7127d473/mission31_resnet_34_subtype_model_best.pth.png"
pre_result = cv2.imread(mask_file_name)

result_sub = [0, 0, 0]
for i in range(3):
    result_sub[i] = numpy.sum(pre_result[:, :, i] != 0)
result_sub_sum = numpy.sum(result_sub)
sub = ["ccRCC", "pRCC", "chRCC"]
summary = ""
for i in range(3):
    result_sub[i] = int(result_sub[i] / result_sub_sum * 100)
    summary = summary + sub[i] + ": " + str(result_sub[i]) + "%, "
mission_db = mission.Mission()
mission_db.update_predict_mask_by_id(job_id=31, predict_mask=summary)
