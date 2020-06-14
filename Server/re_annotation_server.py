from flask import render_template, redirect, request
from flask import jsonify
import uuid
import os
import numpy

from flask_login import login_required, current_user
from Controller import re_annotation_controller

annotation_result_root = "/home1/zhc/resnet/annotation_record/whole/"
boundary_result_root = "/home1/zhc/resnet/boundary_record/"
region_image_root = "/home1/zhc/resnet/anno_data/"

result_root = "Data/re_annotation_data/" + "results/"
points_root = "Data/re_annotation_data/" + "points/"
grades_root = "Data/re_annotation_data/" + "grades/"


def add_re_annotation_sever(app):
    @app.route('/re_annotation')
    @login_required
    def re_annotation():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default="s178_r1974")
        image_root = request.args.get('image_root', type=str,
                                      default='static/data/re_annotation_data/results/a' + annotator_id + '/')
        rand = '?a=' + str(uuid.uuid4())
        if not os.path.exists(result_root + 'a' + annotator_id + '/' + 'mask_' + anno_name + '_U-net.png'):
            re_annotation_controller.boundary_2_point(anno_name, annotator_id)
            re_annotation_controller.point_2_boundary(anno_name, 'nuClick', annotator_id)
            re_annotation_controller.boundary_2_mask(anno_name, 'nuClick', annotator_id)
            re_annotation_controller.boundary_2_mask_u_net(anno_name, annotator_id)
        return render_template('multi-slide.html', anno_name=anno_name, rand=rand, image_root=image_root)

    @app.route('/available_re_annotation_region')
    def available_re_annotation_region():
        result = []
        index = 0
        file_list = os.listdir(annotation_result_root)
        for file in file_list:
            if file[-4:] == ".txt":
                temp = {"id": file.split('.')[0], "text": '【' + str(index) + '】 ' + file.split('.')[0]}
                result.append(temp)
                index += 1
        return jsonify(result)

    @app.route('/make_mask')
    @login_required
    def make_mask():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default="s178_r1974")
        mask_name = request.args.get('mask_name', type=str, default="nuClick")
        re_annotation_controller.boundary_2_mask(anno_name, mask_name, annotator_id)
        return True

    @app.route('/update_grades', methods=['POST'])
    @login_required
    def update_grades():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default="s178_r1974")
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
        boundary_file = numpy.loadtxt(boundary_file_name, dtype=int, delimiter=',')

        for i in range(len(data['grade'])):
            nuclei_id = int(boundary_file[int(data['points_y'][i]), int(data['points_x'][i])])
            if nuclei_id != i + 1 and nuclei_id != 0:
                data['grade'][nuclei_id - 1] = data['grade'][i]
                data['grade'][i] = 0
        for i in range(len(data['grade'])):
            if int(data['grade'][i]) != 0:
                points_file.write(str(data['points_x'][i]) + ' ' + str(data['points_y'][i]) + '\n')
                grades_file.write(str(data['grade'][i]) + '\n')

        grades_file.close()
        points_file.close()

        re_annotation_controller.point_2_boundary(anno_name, 'nuClick', annotator_id)
        re_annotation_controller.boundary_2_mask(anno_name, 'nuClick', annotator_id)

        return jsonify({"msg": "True"})

    @app.route('/points_grades')
    @login_required
    def points_grades():
        annotator_id = current_user.get_id()
        anno_name = request.args.get('anno_name', type=str, default="s178_r1974")
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
