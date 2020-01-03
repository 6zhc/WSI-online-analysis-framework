import os
import cv2
import openslide
import numpy
import os
from PIL import Image
from Model import mission
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


def predict_mask_with_job_id(slide_id, model_name="0"):
    # if str(model_name) == '0':
    #     model_path = "Model/resnet_34_crd_model_59.pth"
    # elif str(model_name) == '1':
    #     model_path = "Model/resnet_34_transfer_predicted_crd_model_best.pth"
    # else:
    model_path = "Model/" + model_name
    manifest_db = manifest.Manifest()
    info = manifest_db.get_project_by_id(slide_id)
    mission_db = mission.Mission()
    job_id = mission_db.insert(slide_uuid=info[1], slide_id=info[0], job_type=model_name, total=-1)

    myModule = predict_module.ResNetClassification(model_path=model_path,
                                                   num_classes=2, batch_size=64, num_workers=0)
    data_folder = data_root + info[1] + '/'
    svs_file = data_folder + info[2]
    if not os.path.exists(data_folder + 'patch/'):
        os.mkdir(data_folder + 'patch/')
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
    probablity_list = []
    times = mask.shape[1] / w * 2000
    mission_db.update_total_by_id(job_id=job_id, total=w // 2000 * h // 2000)
    for x in range(w // 2000):
        for y in range(h // 2000):
            if available_region(mask[int(y * times):int(y * times + times), int(x * times):int(x * times + times)]):
                # if os.path.exists(data_folder + 'patch/' + str(x) + '_' + str(y) + '.png'):
                #     patch = Image.open(data_folder + 'patch/' + str(x) + '_' + str(y) + '.png')
                # else:
                #     patch = oslide.read_region((x * 2000, y * 2000), 0, (2000, 2000))
                #     patch.save(data_folder + 'patch/' + str(x) + '_' + str(y) + '.png')
                patch = oslide.read_region((x * 2000, y * 2000), 0, (2000, 2000))
                patch = numpy.array(patch.convert('RGB'))
                result = myModule.predict(numpy.resize(patch, tuple([1, 2000, 2000, 3])))
                # result = myModule.predict(total_image)
                probablity_list.append((x, y, result[0]))
                pre_result[int(y * times):int(y * times + times), int(x * times):int(x * times + times),
                numpy.argmax(result[0])] = result[0, numpy.argmax(result[0])] * 255
            mission_db.update_finished_by_id(job_id=job_id, finished=x * h // 2000 + y + 1)
    if str(model_name) != '0':
        pre_result = post_processing(pre_result)
    cv2.imwrite(data_folder + 'pre' + str(model_name) + '.png', pre_result)
    mission_db.update_predict_mask_by_id(job_id=job_id, predict_mask='pre' + str(model_name) + '.png')
    # file = open(data_folder + 'log.txt', 'w')
    # for fp in probablity_list:
    #     file.write(str(fp))
    #     file.write('\n')
    # file.close()


def post_processing(image):
    image[:, :, 1:] = 0
    return image


def available_region(region):
    # print(numpy.sum(region == 255), numpy.sum(region == 0))
    return numpy.sum(region == 255) < numpy.sum(region == 0)
