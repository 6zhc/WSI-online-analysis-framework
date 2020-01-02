import os
import cv2
import openslide
import numpy
from PIL import Image
from Model import predictMask
from Model import manifest
from Controller import predict_module


data_root = "Data/"


def generate_icon_image_from_svs_file(svs_file_path, output_file_path):
    oslide = openslide.open_slide(svs_file_path)
    level = oslide.level_count - 1
    w, h = oslide.level_dimensions[level]
    if level < 1:
        print(svs_file_path)
        oslide.close()
        patch = oslide.read_region((0, 0), 0, (w, h))
    else:
        patch = oslide.read_region((0, 0), level, (w, h))
    icon_size = (int(w * 60 / h), 60)
    patch = patch.resize(icon_size, Image.ANTIALIAS)
    patch.save(output_file_path)
    oslide.close()


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


def generate_background_mask_from_smaller_image(smaller_image_path, output_file_path):
    img = cv2.imread(smaller_image_path)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.GaussianBlur(img, (61, 61), 0)
    ret, img_filtered = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(output_file_path, img_filtered)


def make_bg(slide_id):
    manifest_db = manifest.Manifest()
    info = manifest_db.get_project_by_id(slide_id)
    data_folder = data_root + info[1] + '/'
    svs_file = data_folder + info[2]
    if info[4] is None or not os.path.exists(data_folder + info[4]):
        if info[3] is None or not os.path.exists(data_folder + info[4]):
            generate_smaller_image_from_svs_file(svs_file, data_folder + 'smaller_image.png')
            manifest_db.update_smaller_image_by_id(info[0], 'smaller_image.png')
            info = manifest_db.get_project_by_id(slide_id)
        smaller_image = data_folder + info[3]
        generate_background_mask_from_smaller_image(smaller_image, data_folder + 'background_mask.png')
        manifest_db.update_background_mask_by_id(info[0], 'background_mask.png')


def predict_mask_with_job_id(slide_id, job_type="0"):
    if str(job_type) == '0':
        model_path = "Model/resnet_34_crd_model_59.pth"
    elif str(job_type) == '1':
        model_path = "Model/resnet_34_transfer_predicted_crd_model_best.pth"
    else:
        model_path = "Model/" + job_type
    manifest_db = manifest.Manifest()
    info = manifest_db.get_project_by_id(slide_id)
    predict_mask_db = predictMask.PredictMask()
    job_id = predict_mask_db.insert(slide_uuid=info[1], job_type=job_type, total=-1)

    myModule = predict_module.ResNetClassification(model_path=model_path,
                                                   num_classes=2, batch_size=1, num_workers=0)
    data_folder = data_root + info[1] + '/'
    svs_file = data_folder + info[2]
    if info[4] is None or not os.path.exists(data_folder + info[4]):
        if info[3] is None or not os.path.exists(data_folder + info[4]):
            generate_smaller_image_from_svs_file(svs_file, data_folder + 'smaller_image.png')
            manifest_db.update_smaller_image_by_id(info[0], 'smaller_image.png')
            info = manifest_db.get_project_by_id(slide_id)
        smaller_image = data_folder + info[3]
        generate_background_mask_from_smaller_image(smaller_image, data_folder + 'background_mask.png')
        manifest_db.update_background_mask_by_id(info[0], 'background_mask.png')
        info = manifest_db.get_project_by_id(slide_id)

    mask = cv2.imread(data_folder + info[4], cv2.IMREAD_GRAYSCALE)
    oslide = openslide.OpenSlide(svs_file)
    w, h = oslide.dimensions
    pre_result = numpy.zeros((mask.shape[0], mask.shape[1], 3))
    times = mask.shape[1] / w * 2000
    predict_mask_db.update_total_by_id(job_id=job_id, total=w // 2000 * h // 2000)
    for y in range(w // 2000):
        for x in range(h // 2000):
            if available_region(mask[int(x * times):int(x * times + times), int(y * times):int(y * times + times)]):
                patch = oslide.read_region((x * 2000, y * 2000), 0, (2000, 2000))
                result = myModule.predict(numpy.resize(numpy.array(patch), tuple([1, 2000, 2000, 3])))
                pre_result[int(x * times):int(x * times + times), int(y * times):int(y * times + times),
                numpy.argmax(result[0])] = result[0, numpy.argmax(result[0])] * 255
            predict_mask_db.update_finished_by_id(job_id=job_id, finished=y * h // 2000 + x + 1)
    cv2.imwrite(data_folder + 'pre' + str(job_type) + '.png', pre_result)
    predict_mask_db.update_predict_mask_by_id(job_id=job_id, predict_mask='pre' + str(job_type) + '.png')


def available_region(region):
    # print(numpy.sum(region == 255), numpy.sum(region == 0))
    return numpy.sum(region == 255) < numpy.sum(region == 0)
