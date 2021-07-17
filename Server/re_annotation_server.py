from flask import render_template, redirect, request
from flask import jsonify
import uuid
import os
import numpy
from PIL import Image
import cv2

from flask_login import login_required, current_user
from Controller import re_annotation_controller
from Controller import thread_controller

from Controller import manifest_controller
from Model import freehand_annotation_sqlite
from Model import manifest

# annotation_result_root = "/home1/zhc/resnet/annotation_record/whole/" # "/home1/zhc/Dr-Wang-Grading/"
# boundary_result_root = "/home1/zhc/resnet/boundary_record/"
# region_image_root = "/home1/zhc/resnet/anno_data/"

# annotation_result_root = "/home1/gzy/NucleiSegmentation/Smear/Categories/"
# boundary_result_root = "/home1/gzy/NucleiSegmentation/Smear/Masks/"
# region_image_root = "/home1/gzy/NucleiSegmentation/Smear/Images/"

original_result_root = 'static/data/re_annotation_data/results/'
annotation_result_root = "/home5/sort/annotation/"
boundary_result_root = "/home5/sort/masks/"
region_image_root = "/home5/sort/images_small/"


result_root = "Data/re_annotation_data/" + "results/"
points_root = "Data/re_annotation_data/" + "points/"
grades_root = "Data/re_annotation_data/" + "grades/"

# first_image_name = "1"
first_image_name = "152031_1"
image_type = ".jpg"


def add_re_annotation_sever(app):
    @app.route('/re_annotation')
    @login_required
    def re_annotation():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default="")

        if anno_name == "":
            try:
                anno_name = current_user.slideID[annotator_id + "_" + "re-annotation"]
            except:
                anno_name = first_image_name
        current_user.slideID[annotator_id + "_" + "re-annotation"] = anno_name

        image_root = request.args.get('image_root', type=str,
                                      default='static/data/re_annotation_data/results/a' + annotator_id + '/')
        rand = '?a=' + str(uuid.uuid4())
        if not os.path.exists(result_root + 'a' + annotator_id + '/' + 'mask_' + anno_name + '_U-net.png'):
            re_annotation_controller.boundary_2_point(anno_name, annotator_id)
            re_annotation_controller.point_2_boundary(anno_name, 'nuClick', annotator_id)
            re_annotation_controller.boundary_2_mask(anno_name, 'nuClick', annotator_id)
            re_annotation_controller.boundary_2_mask_separate_nuclei(anno_name, 'nuClick', annotator_id)
            re_annotation_controller.boundary_2_mask_u_net(anno_name, annotator_id)
        return render_template('multi-slide.html', anno_name=anno_name, rand=rand,
                               image_root=image_root, image_type=image_type)

    @login_required
    @app.route('/available_re_annotation_region')
    def available_re_annotation_region():
        annotator_id = current_user.get_id()
        result = []
        index = 0
        file_list = os.listdir(annotation_result_root)
        file_list.sort()
        for file in file_list:
            if file[-4:] == ".txt":
                # print(result_root + 'a' + annotator_id + '/' + file.split('.')[0] + "_annotation_file_nuClick.txt")
                if os.path.exists(
                        result_root + 'a' + annotator_id + '/' + file.split('.')[0] + "_annotation_file_nuClick.txt"):
                    temp = {"id": file.split('.')[0], "text": '【' + str(index) + '】 ' + file.split('.')[0] + ' *'}
                else:
                    temp = {"id": file.split('.')[0], "text": '【' + str(index) + '】 ' + file.split('.')[0]}
                result.append(temp)
                index += 1
        return jsonify(result)

    @app.route('/make_mask')
    @login_required
    def make_mask():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default=first_image_name)
        mask_name = request.args.get('mask_name', type=str, default="nuClick")
        re_annotation_make_mask(anno_name, annotator_id)
        result = {
            "mask1": 'mask_' + anno_name + '_' + mask_name + '.png' + '?a=' + str(uuid.uuid4()),
            "mask2": 'mask_' + anno_name + '_' + mask_name + '_separate_nuclei.png' + '?a=' + str(uuid.uuid4()),
        }
        return jsonify(result)

    @app.route('/update_grades', methods=['POST'])
    @login_required
    def update_grades():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default=first_image_name)
        mask_name = request.args.get('mask_name', type=str, default="nuClick")
        data = {}
        for key, value in request.form.items():
            if key.endswith('[]'):
                data[key[:-2]] = request.form.getlist(key)
            else:
                data[key] = value
        print(data)

        boundary_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + mask_name + ".txt"
        points_file_name = points_root + 'a' + annotator_id + '/' + anno_name + '.txt'
        grades_file_name = grades_root + 'a' + annotator_id + '/' + anno_name + '.txt'

        points_file = open(points_file_name, 'w')
        grades_file = open(grades_file_name, 'w')
        boundary_file = numpy.loadtxt(boundary_file_name, dtype=numpy.int16, delimiter=',')

        for i in range(len(data['grade'])):
            nuclei_id = int(boundary_file[int(data['points_y'][i]), int(data['points_x'][i])])
            if nuclei_id == -1:
                try:
                    nuclei_id = int(boundary_file[int(data['points_y'][i]), int(data['points_x'][i]) - 1])
                except:
                    pass
                if nuclei_id == 0:
                    try:
                        nuclei_id = int(boundary_file[int(data['points_y'][i]), int(data['points_x'][i]) + 1])
                    except:
                        pass
            if nuclei_id != i + 1 and nuclei_id != 0:
                if nuclei_id != -1:
                    try:
                        data['grade'][nuclei_id - 1] = data['grade'][i]
                        if int(data['grade'][i]) == 0:
                            boundary_file[boundary_file == nuclei_id] = 0
                    except:
                        print("------------- error: " + nuclei_id + "++++++++++++")
                data['grade'][i] = 0

        current_nuclei_id = 0
        for i in range(len(data['grade'])):
            try:
                if int(data['grade'][i]) != 0:
                    points_file.write(str(data['points_x'][i]) + ' ' + str(data['points_y'][i]) + '\n')
                    grades_file.write(str(data['grade'][i]) + '\n')
                    old_nuclei_id = boundary_file[int(data['points_y'][i]), int(data['points_x'][i])]
                    current_nuclei_id += 1
                    if old_nuclei_id > 0:
                        boundary_file[boundary_file == old_nuclei_id] = current_nuclei_id

            except:
                pass

        numpy.savetxt(boundary_file_name, boundary_file, fmt='%d', delimiter=",")
        grades_file.close()
        points_file.close()
        return jsonify({"msg": "True"})

    def re_annotation_make_mask(anno_name, annotator_id):
        re_annotation_controller.point_2_boundary(anno_name, 'nuClick', annotator_id)
        re_annotation_controller.boundary_2_mask(anno_name, 'nuClick', annotator_id)
        re_annotation_controller.boundary_2_mask_separate_nuclei(anno_name, 'nuClick', annotator_id)

    @app.route('/points_grades')
    @login_required
    def points_grades():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default=first_image_name)
        mask_name = request.args.get('mask_name', type=str, default="nuClick")

        points_file_name = points_root + 'a' + annotator_id + '/' + anno_name + '.txt'
        grades_file_name = grades_root + 'a' + annotator_id + '/' + anno_name + '.txt'
        points_file = open(points_file_name).readlines()
        grades_file = open(grades_file_name).readlines()

        points = []
        grades = []

        for item in points_file:
            points.append([int(item.split(' ')[0]), int(item.split(' ')[1])])

        for item in grades_file:
            grades.append(int(item))
        return jsonify({"grades": grades, "points": points})

    @app.route('/re_annotation/_wipe', methods=['GET', 'POST'])
    @login_required
    def re_annotation_wipe():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default=first_image_name)
        mask_name = request.args.get('mask_name', type=str, default="nuClick")
        boundary_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + mask_name + ".txt"
        annotation_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_annotation_file_" + mask_name + ".txt"

        draw = request.form
        num_of_points = int(len(draw) / 3)

        boundary_file = numpy.loadtxt(boundary_file_name, dtype=numpy.int16, delimiter=',')
        data_x = []
        data_y = []
        mask = numpy.zeros(boundary_file.shape, dtype=numpy.uint8)
        for i in range(num_of_points):
            data_x.append(int(draw[str(i) + '[x]']))
            data_y.append(int(draw[str(i) + '[y]']))
        pts = numpy.vstack((data_x, data_y)).astype(numpy.int32).T
        cv2.fillPoly(mask, [pts], (255))
        p_x = numpy.where(mask == 255)[1]
        p_y = numpy.where(mask == 255)[0]

        for i in range(len(p_x)):
            boundary_file[p_y[i]][p_x[i]] = 0

        annotation_file = numpy.loadtxt(annotation_file_name, dtype=numpy.int16, delimiter=',')
        numpy.savetxt(result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + "Middle" + ".txt",
                      boundary_file, fmt='%d', delimiter=",")
        numpy.savetxt(result_root + 'a' + annotator_id + '/' + anno_name + "_annotation_file_" + "Middle" + ".txt",
                      annotation_file, fmt='%d', delimiter=",")
        re_annotation_controller.boundary_2_mask(anno_name, 'Middle', annotator_id)
        re_annotation_controller.boundary_2_mask_separate_nuclei(anno_name, 'Middle', annotator_id)
        file_name = original_result_root + 'a' + annotator_id + '/' + "mask_" + anno_name + "_Middle" + ".png" + "?a=" + str(
            uuid.uuid4())
        return (file_name)

    @app.route('/re_annotation/_fill', methods=['GET', 'POST'])
    @login_required
    def re_annotation_fill():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default=first_image_name)
        mask_name = request.args.get('mask_name', type=str, default="nuClick")
        boundary_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + mask_name + ".txt"
        annotation_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_annotation_file_" + mask_name + ".txt"

        draw = request.form
        num_of_points = int(len(draw) / 3)
        grade = ''

        boundary_file = numpy.loadtxt(boundary_file_name, dtype=numpy.int16, delimiter=',')
        data_x = []
        data_y = []
        temp = []
        mask = numpy.zeros(boundary_file.shape, dtype=numpy.uint8)
        for i in range(num_of_points):
            data_x.append(int(draw[str(i) + '[x]']))
            data_y.append(int(draw[str(i) + '[y]']))
        pts = numpy.vstack((data_x, data_y)).astype(numpy.int32).T
        cv2.fillPoly(mask, [pts], (255))
        p_x = numpy.where(mask == 255)[1]
        p_y = numpy.where(mask == 255)[0]

        for i in range(len(p_x)):
            temp.append(boundary_file[p_y[i]][p_x[i]] + 2)

        temp = numpy.array(temp)
        bincount = numpy.bincount(temp)
        bincount_list = bincount.tolist()
        max_index = bincount_list.index(max(bincount_list))
        grade = max_index - 2
        for i in range(len(p_x)):
            boundary_file[p_y[i]][p_x[i]] = grade

        annotation_file = numpy.loadtxt(annotation_file_name, dtype=numpy.int16, delimiter=',')
        numpy.savetxt(result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + "Middle" + ".txt",
                      boundary_file, fmt='%d', delimiter=",")
        numpy.savetxt(result_root + 'a' + annotator_id + '/' + anno_name + "_annotation_file_" + "Middle" + ".txt",
                      annotation_file, fmt='%d', delimiter=",")
        re_annotation_controller.boundary_2_mask(anno_name, 'Middle', annotator_id)
        re_annotation_controller.boundary_2_mask_separate_nuclei(anno_name, 'Middle', annotator_id)
        file_name = original_result_root + 'a' + annotator_id + '/' + "mask_" + anno_name + "_Middle" + ".png" + "?a=" + str(
            uuid.uuid4())
        return (file_name)

    @app.route('/update_image', methods=['GET', 'POST'])
    @login_required
    def update_image():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default=first_image_name)
        mask_name = request.args.get('mask_name', type=str, default="nuClick")
        boundary_file_name = result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + "Middle" + ".txt"

        result = numpy.loadtxt(boundary_file_name, dtype=numpy.int16, delimiter=',')
        contours, hierarchy = cv2.findContours(cv2.convertScaleAbs(result), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        result = cv2.drawContours(result, contours, -1, 255, 1)
        result = result.astype(numpy.int16)
        result[result == 255] = -1

        numpy.savetxt(result_root + 'a' + annotator_id + '/' + anno_name + "_boundary_" + mask_name + ".txt",
                      result, fmt='%d', delimiter=",")
        re_annotation_controller.boundary_2_mask(anno_name, 'nuClick', annotator_id)
        re_annotation_controller.boundary_2_mask_separate_nuclei(anno_name, 'nuClick', annotator_id)
        file_name = original_result_root + 'a' + annotator_id + '/' + "mask_" + anno_name + "_nuClick" + ".png" + "?a=" + str(
            uuid.uuid4())
        return (file_name)

    @app.route('/get_info')
    def get_info():
        anno_name = request.args.get('anno_name', type=str, default=first_image_name)
        file_path = region_image_root + anno_name + '.jpg'
        img = Image.open(file_path)
        dimensions = img.size
        MPP = 0
        properties = img.format

        w = dimensions[0]
        h = dimensions[1]
        return jsonify(
            img_width=w,
            img_height=h,
            um_per_px=0.25,
            max_image_zoom=0,  # max_image_zoom,
            toggle_status=0,  # toggle_status
            properties=properties
        )
