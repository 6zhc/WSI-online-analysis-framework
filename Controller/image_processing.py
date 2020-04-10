import cv2
import openslide
import numpy
import os
from PIL import Image
from Model import mission
from Model import manifest
from Controller.predict_module import predict_module2, predict_module

original_data_root = "Data/Original_data/"
analysis_data_root = "Data/analysis_data/"


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
    original_data_folder = original_data_root + info[1] + '/'
    svs_file = original_data_folder + info[2]
    analysis_data_folder = analysis_data_root + info[1] + '/'
    if not os.path.exists(analysis_data_folder):
        os.mkdir(analysis_data_folder)
    if info[4] is None or not os.path.exists(analysis_data_folder + info[4]):
        if info[3] is None or not os.path.exists(analysis_data_folder + info[3]):
            generate_smaller_image_from_svs_file(svs_file, analysis_data_folder + 'smaller_image.png')
            manifest_db.update_smaller_image_by_id(info[0], 'smaller_image.png')
            info = manifest_db.get_project_by_id(slide_id)
        smaller_image = analysis_data_folder + info[3]
        generate_background_mask_from_smaller_image(smaller_image, analysis_data_folder + 'background_mask.png')
        manifest_db.update_background_mask_by_id(info[0], 'background_mask.png')


def predict_mask_with_job_id(slide_id, model_name="0"):
    # if str(model_name) == '0':
    #     model_path = "Model/resnet_34_crd_model_59.pth"
    # elif str(model_name) == '1':
    #     model_path = "Model/resnet_34_transfer_predicted_crd_model_best.pth"
    # else:
    model_path = "models/" + model_name

    make_bg(slide_id)

    manifest_db = manifest.Manifest()
    info = manifest_db.get_project_by_id(slide_id)
    mission_db = mission.Mission()
    job_id = mission_db.insert(slide_uuid=info[1], slide_id=info[0], job_type=model_name, total=-1)

    original_data_folder = original_data_root + info[1] + '/'
    analysis_data_folder = analysis_data_root + info[1] + '/'

    svs_file = original_data_folder + info[2]
    # if not os.path.exists(analysis_data_folder + 'patch/'):
    #     os.mkdir(analysis_data_folder + 'patch/')

    mask = cv2.imread(analysis_data_folder + info[4], cv2.IMREAD_GRAYSCALE)
    oslide = openslide.OpenSlide(svs_file)
    w, h = oslide.dimensions
    pre_result = numpy.zeros((mask.shape[0], mask.shape[1], 4), dtype=numpy.uint8)
    times = mask.shape[1] / w * 2000
    mission_db.update_total_by_id(job_id=job_id, total=w // 2000 * h // 2000)

    if "subtype" not in str(model_name):
        myModule = predict_module.ResNetClassification(model_path=model_path,
                                                       num_classes=2, batch_size=64, num_workers=0)

        for x in range(w // 2000):
            for y in range(h // 2000):
                if available_region(mask[int(y * times):int(y * times + times), int(x * times):int(x * times + times)]):
                    # if os.path.exists(analysis_data_folder + 'patch/' + str(x) + '_' + str(y) + '.png'):
                    #     patch = Image.open(analysis_data_folder + 'patch/' + str(x) + '_' + str(y) + '.png')
                    # else:
                    #     patch = oslide.read_region((x * 2000, y * 2000), 0, (2000, 2000))
                    #     patch.save(analysis_data_folder + 'patch/' + str(x) + '_' + str(y) + '.png')
                    patch = oslide.read_region((x * 2000, y * 2000), 0, (2000, 2000))
                    patch = numpy.array(patch.convert('RGB'))
                    result = myModule.predict(numpy.resize(patch, tuple([1, 2000, 2000, 3])))
                    # result = myModule.predict(total_image)
                    # probablity_list.append((x, y, result[0]))
                    pre_result[int(y * times):int(y * times + times), int(x * times):int(x * times + times),
                    numpy.argmax(result[0])] = result[0, numpy.argmax(result[0])] * 255
                mission_db.update_finished_by_id(job_id=job_id, finished=x * h // 2000 + y + 1)

        pre_result = post_processing(pre_result)
        mask_file_name = 'mission' + str(job_id) + '_' + str(model_name) + '.png'
        cv2.imwrite(analysis_data_folder + mask_file_name, pre_result)
        mission_db.update_predict_mask_by_id(job_id=job_id, predict_mask=mask_file_name)

        mask_file = cv2.imread(analysis_data_folder + mask_file_name)
        
        original_file_name = "smaller_image.png"
        original_file = cv2.imread(analysis_data_folder + original_file_name)
        
        alpha = numpy.zeros(mask_file.shape)
        alpha[:, :, 0] = mask_file[:, :, 0]
        alpha[:, :, 1] = mask_file[:, :, 0]
        alpha[:, :, 2] = mask_file[:, :, 0]
        alpha = alpha.astype(float)/128 
        
        mask_file = mask_file.astype(float)
        original_file = original_file.astype(float)
        mask_file = cv2.multiply((1-alpha)*0.7, mask_file)
        original_file = cv2.multiply(0.3 + alpha * 0.7, original_file)

        out_image = original_file + mask_file
        result_file_name = 'mission' + str(job_id) + '_result.png'
        cv2.imwrite(analysis_data_folder + result_file_name, out_image)

    elif "subtype" in str(model_name) and "hybrid" in str(model_name):
        myModule = predict_module.ResNetClassification(model_path=model_path,
                                                       num_classes=4, batch_size=64, num_workers=0)
        for x in range(w // 2000):
            for y in range(h // 2000):
                if available_region(mask[int(y * times):int(y * times + times), int(x * times):int(x * times + times)]):
                    patch = oslide.read_region((x * 2000, y * 2000), 0, (2000, 2000))
                    patch = numpy.array(patch.convert('RGB'))
                    result = myModule.predict(numpy.resize(patch, tuple([1, 2000, 2000, 3])))
                    pre_result[int(y * times):int(y * times + times), int(x * times):int(x * times + times),
                    numpy.argmax(result[0])] = result[0, numpy.argmax(result[0])] * 255
                mission_db.update_finished_by_id(job_id=job_id, finished=x * h // 2000 + y + 1)

        sub = ["health", "ccRCC", "pRCC", "chRCC"]
        result_sub = [0, 0, 0, 0]
        for i in range(4):
            result_sub[i] = numpy.sum(pre_result[:, :, i] != 0)
        result_sub_sum = numpy.sum(result_sub)
        summary = ""
        for i in range(4):
            result_sub[i] = int(result_sub[i] / result_sub_sum * 100)
            summary = summary + sub[i] + ": " + str(result_sub[i]) + "%, "
        
        result = numpy.zeros((pre_result.shape[0], pre_result.shape[1], 3))
        for i in range(3):
            result[:, :, i] = pre_result[:, :, i + 1]
        mask_file_name = 'mission' + str(job_id) + '_' + str(model_name) + '.png'
        cv2.imwrite(analysis_data_folder + mask_file_name, result)
        
        mission_db.update_predict_mask_by_id(job_id=job_id, predict_mask=summary)

    elif "_subtype" in str(model_name) and "hybrid" not in str(model_name):
        myModule = predict_module.ResNetClassification(model_path=model_path,
                                                       num_classes=3, batch_size=64, num_workers=0)

        for x in range(w // 2000):
            for y in range(h // 2000):
                if available_region(mask[int(y * times):int(y * times + times), int(x * times):int(x * times + times)]):
                    patch = oslide.read_region((x * 2000, y * 2000), 0, (2000, 2000))
                    patch = numpy.array(patch.convert('RGB'))
                    result = myModule.predict(numpy.resize(patch, tuple([1, 2000, 2000, 3])))
                    pre_result[int(y * times):int(y * times + times), int(x * times):int(x * times + times),
                    numpy.argmax(result[0])] = result[0, numpy.argmax(result[0])] * 255
                mission_db.update_finished_by_id(job_id=job_id, finished=x * h // 2000 + y + 1)

        sub = ["ccRCC", "pRCC", "chRCC"]
        result_sub = [0, 0, 0]
        for i in range(3):
            result_sub[i] = numpy.sum(pre_result[:, :, i] != 0)
        result_sub_sum = numpy.sum(result_sub)
        summary = ""
        for i in range(3):
            result_sub[i] = int(result_sub[i] / result_sub_sum * 100)
            summary = summary + sub[i] + ": " + str(result_sub[i]) + "%, "
            
        result = numpy.zeros((pre_result.shape[0], pre_result.shape[1], 3))
        for i in range(3):
            result[:,:,i] = pre_result[:,:,i]
        mask_file_name = 'mission' + str(job_id) + '_' + str(model_name) + '.png'
        cv2.imwrite(analysis_data_folder + mask_file_name, result)
        
        mission_db.update_predict_mask_by_id(job_id=job_id, predict_mask=summary)

    elif "MixMatch-subtype" in str(model_name):
        myModule = predict_module2.ResNetClassification(model_path=model_path,
                                                        batch_size=64, num_workers=0)

        for x in range(w // 2000):
            for y in range(h // 2000):
                if available_region(mask[int(y * times):int(y * times + times), int(x * times):int(x * times + times)]):
                    patch = oslide.read_region((x * 2000, y * 2000), 0, (2000, 2000))
                    patch = numpy.array(patch.convert('RGB'))
                    result1, result2 = myModule.predict(numpy.resize(patch, tuple([1, 2000, 2000, 3])))
                    if result1[0, 1] > 0.5:
                        pre_result[int(y * times):int(y * times + times), int(x * times):int(x * times + times),
                        0] = result1[0, 1] * 255
                    elif result1[0, 0] > 0.5:
                        pre_result[int(y * times):int(y * times + times), int(x * times):int(x * times + times),
                        numpy.argmax(result2[0]) + 1] = result2[0, numpy.argmax(result2[0])] * 255
                mission_db.update_finished_by_id(job_id=job_id, finished=x * h // 2000 + y + 1)

        sub = ["health", "ccRCC", "pRCC", "chRCC"]
        result_sub = [0, 0, 0, 0]
        for i in range(4):
            result_sub[i] = numpy.sum(pre_result[:, :, i] != 0)
        result_sub_sum = numpy.sum(result_sub)
        summary = ""
        for i in range(4):
            result_sub[i] = int(result_sub[i] / result_sub_sum * 100)
            summary = summary + sub[i] + ": " + str(result_sub[i]) + "%, "

        result = numpy.zeros((pre_result.shape[0], pre_result.shape[1], 3))
        for i in range(3):
            result[:, :, i] = pre_result[:, :, i + 1]
        mask_file_name = 'mission' + str(job_id) + '_' + str(model_name) + '.png'
        cv2.imwrite(analysis_data_folder + mask_file_name, result)

        mission_db.update_predict_mask_by_id(job_id=job_id, predict_mask=summary)

    # file = open(analysis_data_folder + 'log.txt', 'w')
    # for fp in probablity_list:
    #     file.write(str(fp))
    #     file.write('\n')
    # file.close()


def post_processing(image):
    image[:, :, 1:] = 0
    image = cv2.blur(image, (200, 200))
    image = cv2.applyColorMap(image[:, :, 0], cv2.COLORMAP_JET)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # image[image < 140] = 0
    # image[image > 180] = 180
    #
    # image[image > 140] = (image[image > 140] - 140) / 40 * 255
    # image = Image.fromarray(image).convert('RGBA')
    # # print("convert finished")
    # image = numpy.array(image)
    # image[:, :, 3] = image[:, :, 2]
    # image[:, :, 2] = 255

    # image = 255 - image
    return image


def available_region(region):
    # print(numpy.sum(region == 255), numpy.sum(region == 0))
    return numpy.sum(region == 255) < numpy.sum(region == 0)
