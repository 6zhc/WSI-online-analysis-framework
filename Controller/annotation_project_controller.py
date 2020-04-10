import os
import numpy
import json
from Model import manifest
from Controller import manifest_controller
from Model.freehand_annotation_sqlite import SqliteConnector

manifest_root = "Data/annotation_project_manifest/"
nuclei_annotation_root = "Data/nuclei_annotation_data/"
freehand_annotation_root = "Data/freehand_annotation_data/"


def get_table():
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
            annotation_project_root = nuclei_annotation_root + result[i][0] + '/'

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


def refresh_npy():
    result = []
    available_slide_id = []
    for item in manifest_controller.get_available_slide_id():
        available_slide_id.append(item['id'])
    file_list = os.listdir(manifest_root)
    mani = manifest.Manifest()
    for file in file_list:
        temp = []
        if file[-4:] != ".txt":
            continue
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
                slide_id.append(int(wsi[0]))
            except:
                missing_slide_uuid.append(info[0])
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

        temp.append('<a href="/nuclei_annotation?slide_id=' + str(slide_id[0]) + '&project=' + str(project_name)
                    + '" target="_Blank">nuclei annotate </a>')
        temp.append('<a href="/freehand_annotation?slide_id=' + str(slide_id[0]) + '&project=' + str(project_name)
                    + '" target="_Blank">freehand annotate </a>')

        result.append(temp)

    filename = manifest_root + 'table.npy'
    result = numpy.array(result)
    numpy.save(filename, result)  # 保存为.npy格式

    refresh_freehand_annotation_progress()
    refresh_nuclei_annotation_progress()

    return
