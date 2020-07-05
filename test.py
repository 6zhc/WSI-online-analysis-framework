from Controller import image_processing
from PIL import Image
import cv2
import numpy
from Model import mission

mask_file_name = "/home1/zhc/wsi-procesing-framework/static/data/analysis_data/cd8418fc-f83a-41db-87cb-5779ba97362a/mission21_resnet_34_subtype_hybrid_loss_model.pth.png"
pre_result = cv2.imread(mask_file_name)

result = numpy.zeros((pre_result.shape[0], pre_result.shape[1], 3))

i = 1
result[:, :, 0] = pre_result[:, :, i] * [15] / 255
result[:, :, 1] = pre_result[:, :, i] * [147] / 255
result[:, :, 2] = pre_result[:, :, i] * [254] / 255
i = 0
result[:, :, i] += pre_result[:, :, i]
i = 2
result[:, :, i] += pre_result[:, :, i]

mask_file_name = "/home1/zhc/wsi-procesing-framework/static/data/analysis_data/cd8418fc-f83a-41db-87cb-5779ba97362a/" \
                 "result_mission21_resnet_34_subtype_hybrid_loss_model.pth.png"
cv2.imwrite(mask_file_name, result)

# result_sub = [0, 0, 0]
# for i in range(3):
#     result_sub[i] = numpy.sum(pre_result[:, :, i] != 0)
# result_sub_sum = numpy.sum(result_sub)
# sub = ["ccRCC", "pRCC", "chRCC"]
# summary = ""
# for i in range(3):
#     result_sub[i] = int(result_sub[i] / result_sub_sum * 100)
#     summary = summary + sub[i] + ": " + str(result_sub[i]) + "%, "
# mission_db = mission.Mission()
# mission_db.update_predict_mask_by_id(job_id=31, predict_mask=summary)
