import os
import numpy
import cv2
import shutil
import uuid
import openslide
from pathlib import Path

from Model import manifest
from Controller import manifest_controller
from Model.freehand_annotation_sqlite import SqliteConnector

manifest_root = "Data/annotation_project_manifest/"
nuclei_annotation_root = "Data/nuclei_annotation_data/"
freehand_annotation_root = "Data/freehand_annotation_data/"
original_data_root = "Data/Original_data/"
export_annotation_root = "export/"


def get_table():
    refresh_nuclei_annotation_export()
    refresh_freehand_annotation_export()
    filename = manifest_root + 'table.npy'
    if not os.path.exists(filename):
        refresh_npy()
    result = numpy.load(filename)
    result = result.tolist()
    return result


def refresh_nuclei_annotation_progress():
    filename = manifest_root + 'table.npy'
    if not os.path.exists(filename):
        refresh_npy()
    else:
        result = numpy.load(filename)
        for i in range(len(result)):
            manifest_txt = open(manifest_root + result[i][0] + '.txt').readlines()
            annotation_project_root = nuclei_annotation_root + result[i][0] + '/'

            annotator_no = 6
            region_no = 0
            finish_region_no = numpy.zeros(annotator_no)
            for wsi in manifest_txt:
                info = wsi.split('\t')
                if not os.path.exists(annotation_project_root + info[0] + '/'):
                    continue
                for annotation_file in os.listdir(annotation_project_root + info[0] + '/'):
                    # print(annotation_file[0], annotation_file[-4:])
                    if annotation_file[0] == 'r' and annotation_file[-4:] == '.txt':
                        region_no = region_no + 1
                        for annotator_id in range(annotator_no):
                            if os.path.exists(annotation_project_root + info[0] + '/' +
                                              'a' + str(annotator_id + 1) + '_' + annotation_file) and \
                                    sum(numpy.loadtxt(annotation_project_root + info[0] + '/' +
                                                      'a' + str(annotator_id + 1) + '_' + annotation_file)) > 0:
                                finish_region_no[annotator_id] += 1
            result_str = ""  # 'Total: ' + str(region_no) + ', <br/>'
            for annotator_id in range(annotator_no):
                result_str += str(annotator_id + 1) + ': ' + \
                              str(int(finish_region_no[annotator_id])) + ' /' + str(region_no) + ', '
                if annotator_id % 2:
                    result_str += '<br/>'
            result[i][4] = result_str

        filename = manifest_root + 'table.npy'
        result = numpy.array(result)
        numpy.save(filename, result)  # 保存为.npy格式
    return


def refresh_freehand_annotation_progress():
    filename = manifest_root + 'table.npy'
    if not os.path.exists(filename):
        refresh_npy()
    else:
        result = numpy.load(filename)
        for i in range(len(result)):
            manifest_txt = open(manifest_root + result[i][0] + '.txt').readlines()
            annotation_project_root = freehand_annotation_root + result[i][0] + '/'

            annotator_no = 6
            region_no = 0
            finish_region_no = numpy.zeros(annotator_no)
            for wsi in manifest_txt:
                info = wsi.split('\t')
                region_no = region_no + 1
                if not os.path.exists(annotation_project_root + info[0] + '/'):
                    continue
                for annotator_id in range(annotator_no):
                    if os.path.exists(annotation_project_root + info[0] + '/' +
                                      'a' + str(annotator_id + 1) + '.db') and \
                            len(SqliteConnector(annotation_project_root + info[0] + '/' +
                                                'a' + str(annotator_id + 1) + '.db').get_lines()) > 0:
                        finish_region_no[annotator_id] += 1
            result_str = ""  # 'Total: ' + str(region_no) + ', <br/>'
            for annotator_id in range(annotator_no):
                result_str += str(annotator_id + 1) + ': ' + \
                              str(int(finish_region_no[annotator_id])) + ' /' + str(region_no) + ', '
                if annotator_id % 2:
                    result_str += '<br/>'
            result[i][5] = result_str

        filename = manifest_root + 'table.npy'
        result = numpy.array(result)
        numpy.save(filename, result)  # 保存为.npy格式
    return


def refresh_nuclei_annotation_export():
    filename = manifest_root + 'table.npy'
    if not os.path.exists(filename):
        refresh_npy()
    else:
        result = numpy.load(filename)
        file_list = sorted(os.listdir("export"))
        file = '<a >Unavailable</ a>'
        for i in range(len(result)):
            result[i][0]
            file_url = '<a >Unavailable</ a>'
            file = result[i][0] + "_nuclei_annotation.zip?a=" + str(uuid.uuid1())
            if result[i][0] + "_nuclei_annotation.zip" in file_list:
                file_url = '<a href="/static/export/' + file + '">Download</ a>'
            result_str = file_url + ' <br/>' + '<a href= "/export_nuclei_annotation?manifest_file=' + \
                         manifest_root + result[i][0] + '.txt">(re)Export</ a>'
            result[i][8] = result_str

        filename = manifest_root + 'table.npy'
        result = numpy.array(result)
        numpy.save(filename, result)  # 保存为.npy格式
    return


def refresh_freehand_annotation_export():
    filename = manifest_root + 'table.npy'
    if not os.path.exists(filename):
        refresh_npy()
    else:
        result = numpy.load(filename)
        file_list = sorted(os.listdir("export"))
        file = '<a >Unavailable</ a>'
        for i in range(len(result)):
            result[i][0]
            file_url = '<a >Unavailable</ a>'
            file = result[i][0] + "_freehand_annotation.zip?a=" + str(uuid.uuid1())
            if result[i][0] + "_freehand_annotation.zip" in file_list:
                file_url = '<a href="/static/export/' + file + '">Download</ a>'
            result_str = file_url + ' <br/>' + '<a href= "/export_freehand_annotation?manifest_file=' + \
                         manifest_root + result[i][0] + '.txt">(re)Export</ a>'
            result[i][9] = result_str

        filename = manifest_root + 'table.npy'
        result = numpy.array(result)
        numpy.save(filename, result)  # 保存为.npy格式
    return


def export_nuclei_annotation_data(manifest_file_url):
    manifest_txt = open(manifest_file_url).readlines()
    annotation_project_root = nuclei_annotation_root + manifest_file_url.rsplit("/", 1)[1][:-4] + '/'

    colour = [tuple([124, 252, 0]), tuple([0, 255, 255]), tuple([137, 43, 224]),
              tuple([255 * 0.82, 255 * 0.41, 255 * 0.12]), tuple([255, 0, 0]), tuple([0, 128, 255])]
    color_scheme = color_scheme = [
        [0.49, 0.99, 0], [0, 1, 1], [0.54, 0.17, 0.88], [0.82, 0.41, 0.12],
        [1, 0, 0], [0, 0.5, 1]
    ]

    if not (not (manifest_file_url.rsplit("/", 1)[1][:-4] == "") and not (
            manifest_file_url.rsplit("/", 1)[1][:-4] is None)):
        return
    export_file = export_annotation_root + manifest_file_url.rsplit("/", 1)[1][:-4] + '_nuclei_annotation.zip'
    if os.path.exists(export_file):
        os.remove(export_file)

    export_path = export_annotation_root + manifest_file_url.rsplit("/", 1)[1][:-4] + '/nuclei_annotation/'
    if os.path.exists(export_path):
        shutil.rmtree(export_path)
    os.mkdir(export_path)

    annotator_no = 6
    for annotator_id in range(annotator_no):
        os.mkdir(export_path + 'a' + str(annotator_id + 1) + '/')

    for wsi in manifest_txt:
        info = wsi.split('\t')
        if not os.path.exists(annotation_project_root + info[0] + '/'):
            continue
        for annotation_file in os.listdir(annotation_project_root + info[0] + '/'):
            # print(annotation_file[0], annotation_file[-4:])
            if annotation_file[0] == 'r' and annotation_file[-4:] == '.txt':
                original_pic_url = annotation_project_root + info[0] + '/' + annotation_file[:-4] + '.png'
                original_pic = cv2.imread(original_pic_url)

                region_image_url = annotation_project_root + info[0] + '/' + annotation_file[:-4] + '.txt'
                region_image = numpy.loadtxt(region_image_url, delimiter=",", dtype=int)

                for annotator_id in range(annotator_no):
                    if os.path.exists(annotation_project_root + info[0] + '/' +
                                      'a' + str(annotator_id + 1) + '_' + annotation_file) and \
                            sum(numpy.loadtxt(annotation_project_root + info[0] + '/' +
                                              'a' + str(annotator_id + 1) + '_' + annotation_file)) > 0:

                        write_path = export_path + 'a' + str(annotator_id + 1) + '/' + info[0] + '/'
                        if not os.path.exists(write_path):
                            os.mkdir(write_path)

                        annotator_data_url = annotation_project_root + info[0] + '/' + \
                                             'a' + str(annotator_id + 1) + '_' + annotation_file
                        annotator_data = numpy.loadtxt(annotator_data_url, delimiter=",", dtype=int)

                        write_url = export_path + 'a' + str(annotator_id + 1) + '/' + info[0] + '/' \
                                    + annotation_file[:-4] + '_original.png'
                        cv2.imwrite(write_url, original_pic)

                        mask = numpy.zeros(original_pic.shape)
                        mask_original = numpy.zeros(original_pic.shape)

                        for i, val in enumerate(annotator_data):
                            if i != 1 and val != 0:
                                mask[region_image == i] = colour[int(val) - 1]
                                mask_original[region_image == i] = (original_pic[region_image == i] * 2.7
                                                                    + colour[val - 1]) / 3.3
                            else:
                                mask_original[region_image == i] = original_pic[region_image == i]

                        write_url = export_path + 'a' + str(annotator_id + 1) + '/' + info[0] + '/' \
                                    + annotation_file[:-4] + '_mask.png'
                        cv2.imwrite(write_url, mask)

                        mask_original[region_image == -1] = tuple([0, 0, 0])
                        write_url = export_path + 'a' + str(annotator_id + 1) + '/' + info[0] + '/' \
                                    + annotation_file[:-4] + '_mask_original.png'
                        cv2.imwrite(write_url, mask_original)

                        write_url = export_path + 'a' + str(annotator_id + 1) + '/' + info[0] + '/' \
                                    + annotation_file[:-4] + '_annotator_data.txt'
                        numpy.savetxt(write_url, annotator_data, fmt="%d", delimiter=",")

                        write_url = export_path + 'a' + str(annotator_id + 1) + '/' + info[0] + '/' \
                                    + annotation_file[:-4] + '_boundary.txt'
                        numpy.savetxt(write_url, region_image, fmt="%d", delimiter=",")

    annotator_no = 6
    for annotator_id in range(annotator_no):
        if not os.listdir(export_path + 'a' + str(annotator_id + 1)):
            shutil.rmtree(export_path + 'a' + str(annotator_id + 1))
    if os.listdir(export_path):
        shutil.make_archive(export_file[:-4], 'zip', export_path)
    return 'static/' + export_file


def export_freehand_annotation_data(manifest_file_url):
    manifest_txt = open(manifest_file_url).readlines()
    annotation_project_root = freehand_annotation_root + manifest_file_url.rsplit("/", 1)[1][:-4] + '/'

    if not (not (manifest_file_url.rsplit("/", 1)[1][:-4] == "") and not (
            manifest_file_url.rsplit("/", 1)[1][:-4] is None)):
        return
    export_file = export_annotation_root + manifest_file_url.rsplit("/", 1)[1][:-4] + '_freehand_annotation.zip'
    if os.path.exists(export_file):
        os.remove(export_file)

    export_path = export_annotation_root + manifest_file_url.rsplit("/", 1)[1][:-4] + '/freehand_annotation/'
    if os.path.exists(export_path):
        shutil.rmtree(export_path)
    os.mkdir(export_path)

    annotator_no = 6
    for annotator_id in range(annotator_no):
        os.mkdir(export_path + 'a' + str(annotator_id + 1) + '/')

    down = 32
    for wsi in manifest_txt:
        info = wsi.split('\t')
        if not os.path.exists(annotation_project_root + info[0] + '/'):
            continue
        dimensions = None
        for annotator_id in range(annotator_no):
            if os.path.exists(annotation_project_root + info[0] + '/' +
                              'a' + str(annotator_id + 1) + '.db') and \
                    len(SqliteConnector(annotation_project_root + info[0] + '/' +
                                        'a' + str(annotator_id + 1) + '.db').get_lines()) > 0:
                if not dimensions:
                    try:
                        dimensions = openslide.open_slide(original_data_root + info[0] + '/' + info[1]).dimensions
                    except:
                        continue
                img_height = dimensions[1]
                img_width = dimensions[0]
                mask = numpy.zeros([int(img_height / down), int(img_width / down), 1], numpy.uint8)
                db = SqliteConnector(annotation_project_root + info[0] + '/' + 'a' + str(annotator_id + 1) + '.db')
                for temp in db.get_lines():
                    if temp[1] < 10:
                        temp1 = 10
                    elif temp[1] >= img_width - 10:
                        temp1 = img_width - 10
                    else:
                        temp1 = temp[1]

                    if temp[2] < 10:
                        temp2 = 10
                    elif temp[2] >= img_height - 10:
                        temp2 = img_height - 10
                    else:
                        temp2 = temp[2]

                    if temp[3] < 10:
                        temp3 = 10
                    elif temp[3] >= img_width - 10:
                        temp3 = img_width - 10
                    else:
                        temp3 = temp[3]

                    if temp[4] < 10:
                        temp4 = 10
                    elif temp[4] >= img_height - 10:
                        temp4 = img_height - 10
                    else:
                        temp4 = temp[4]

                    cv2.line(mask, (int(temp1 / down), int(temp2 / down)),
                             (int(temp3 / down), int(temp4 / down)), 255, 4)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

                contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                cv2.drawContours(mask, contours, -1, 255, -1)

                mask_new = mask.copy()
                contours_new, hierarchy_new = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                cv2.drawContours(mask_new, contours_new, -1, 255, -1)

                while not (mask_new == mask).all():
                    mask = mask_new.copy()
                    contours_new, hierarchy_new = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    cv2.drawContours(mask_new, contours_new, -1, 255, -1)

                mask = mask_new.copy()

                write_url = export_path + 'a' + str(annotator_id + 1) + '/' + info[0] + '.png'
                cv2.imwrite(write_url, mask)

    annotator_no = 6
    for annotator_id in range(annotator_no):
        if not os.listdir(export_path + 'a' + str(annotator_id + 1)):
            shutil.rmtree(export_path + 'a' + str(annotator_id + 1))
    if os.listdir(export_path):
        shutil.make_archive(export_file[:-4], 'zip', export_path)
    return 'static/' + export_file


def refresh_npy():
    result = []
    available_slide_id = []
    for item in manifest_controller.get_available_slide_id():
        available_slide_id.append(item['id'])
    file_list = os.listdir(manifest_root)
    file_list.sort()
    mani = manifest.Manifest()
    for file in file_list:
        temp = []
        if file[-4:] != ".txt":
            continue
        slide_table_file = open('export/' + file[:-4] + '_slide_table.txt', 'w')
        slide_id = []
        missing_slide_uuid = []

        project_name = file[:-4]
        temp.append(project_name)

        manifest_txt = open(manifest_root + file).readlines()
        for wsi in manifest_txt:
            info = wsi.split('\t')
            if info[0] == "id":
                continue
            try:
                info[0] = '[*] ' + info[0]
                wsi = mani.get_project_by_uuid(info[0][4:])
                if int(wsi[0]) not in available_slide_id:
                    info[0] = '[' + str(wsi[0]) + '] ' + info[0][4:]
                    raise Exception
                slide_table_file.write(str(wsi[0]) + '\t' + info[0][4:] + '\n')
                slide_id.append(int(wsi[0]))
            except:
                missing_slide_uuid.append(info[0])
        slide_table_file.close()
        # print(missing_slide_uuid)
        # print(slide_id)

        missing_slide_id_str = ""
        slide_id_str = ""
        if not slide_id:
            temp.append('Empty Manifest!')
            result.append(temp)
            continue

        min_slide_id = min(slide_id)
        for i in range(max(slide_id) + 1):
            if i not in slide_id:
                if i >= min_slide_id:
                    missing_slide_id_str = missing_slide_id_str + str(i) + ', '
            elif i - 1 not in slide_id and i in slide_id:
                slide_id_str = slide_id_str + str(i)
                if i + 1 in slide_id:
                    slide_id_str = slide_id_str + '-'
                else:
                    slide_id_str = slide_id_str + ', '
            elif i - 1 in slide_id and i in slide_id and i + 1 not in slide_id:
                slide_id_str = slide_id_str + str(i) + ', '
        temp.append(slide_id_str)
        temp.append(missing_slide_id_str)
        temp.append('<button type="button" onclick="alert(' + str(missing_slide_uuid) +
                    '.join(\'\\n\'))">see more</button>')

        annotation_project_root = nuclei_annotation_root + project_name + '/'
        if not os.path.exists(annotation_project_root):
            os.mkdir(annotation_project_root)

        temp.append("Unavailable")

        annotation_project_root = freehand_annotation_root + project_name + '/'
        if not os.path.exists(annotation_project_root):
            os.mkdir(annotation_project_root)

        temp.append("Unavailable")

        temp.append('<a href="/nuclei_annotation?' + 'project=' + str(project_name)  # '&slide_id=' + str(slide_id[0])
                    + '" target="_Blank">nuclei annotate </a>')
        temp.append('<a href="/freehand_annotation?' + 'project=' + str(project_name)  # '&slide_id=' + str(slide_id[0])
                    + '" target="_Blank">freehand annotate </a>')

        temp.append("Unavailable")
        temp.append("Unavailable")

        temp.append('<a href="' + '/static/export/' + file[:-4] + '_slide_table.txt" ' + \
                    'download="' + file[:-4] + '_slide_table.txt' + '">Download </a>')

        result.append(temp)

    filename = manifest_root + 'table.npy'
    result = numpy.array(result)
    numpy.save(filename, result)  # 保存为.npy格式

    refresh_freehand_annotation_progress()
    refresh_nuclei_annotation_progress()

    return
