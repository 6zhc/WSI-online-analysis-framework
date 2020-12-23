import numpy as np
import openslide
import os
import uuid

from flask_login import login_required, current_user
from flask import jsonify, request, render_template

from Controller import manifest_controller
from Model import manifest
from Model import nuclei_annotation_sqlite
from Controller import thread_controller
from Controller import nuclei_annotation_v2_controller

original_data_root = 'static/data/Original_data/'
nuclei_annotation_data_root = "static/data/nuclei_annotation_data/"


def add_annotation_sever(app):
    @app.route('/nuclei_annotation_v2', methods=['GET', 'POST'])
    @login_required
    def nuclei_annotation_v2():

        annotator_id = current_user.get_id()
        annotation_project = request.args.get('project', default="None", type=str)

        slide_id = request.args.get('slide_id', default=-1, type=int)
        if slide_id == -1:
            try:
                slide_id = current_user.slideID[annotator_id + '_' + annotation_project + "_" + "nuclei"]
            except:
                temp = []
                for wsi in open('export/' + annotation_project + '_slide_table.txt').readlines():
                    slide_id = int(wsi.split('\t')[0])
                    temp.append(slide_id)
                slide_id = int(np.min(temp))
        current_user.slideID[annotator_id + '_' + annotation_project + "_" + "nuclei"] = slide_id

        info = manifest_controller.get_info_by_id(slide_id)
        dzi_file_path = "/static/data/dzi_data/" + str(info[1]) + '/' \
                        + str(info[2]) + ".dzi"
        if os.path.exists(dzi_file_path):
            slide_url = dzi_file_path
        else:
            slide_url = "/dzi_online/Data/Original_data/" + str(info[1]) + '/' \
                        + str(info[2]) + ".dzi"

        return render_template('nuclei_annotation_v2.html', slide_url=slide_url, slide_id=slide_id,
                               annotator_id=annotator_id, slide_uuid=info[1], project=annotation_project)

    @app.route('/nuclei_annotation_v2/_get_info')
    def nuclei_annotation_v2_get_info():

        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        mani = manifest.Manifest()
        wsi = mani.get_project_by_id(slide_id)
        svs_file_path = original_data_root + wsi[1] + '/' + wsi[2]
        dimensions = openslide.OpenSlide(svs_file_path).dimensions

        w = dimensions[0]
        h = dimensions[1]
        return jsonify(
            img_width=w,
            img_height=h,
            um_per_px=0.25,
            max_image_zoom=0,  # max_image_zoom,
            toggle_status=0  # toggle_status
        )

    @app.route('/nuclei_annotation_v2/_update_image')
    def nuclei_annotation_v2_update_image():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        v1 = request.args.get('var1', 0, type=int)  # Top-left x coordinate
        v2 = request.args.get('var2', 0, type=int)  # Top-left y coordinate
        v3 = request.args.get('var3', 0, type=int)  # Bottom-right x
        v4 = request.args.get('var4', 0, type=int)  # Bottom-right y
        v5 = request.args.get('var5', 0, type=int)  # Viewer width (pixel)
        v6 = request.args.get('var6', 0, type=int)  # Viewer height (pixel)
        v7 = request.args.get('var7', 0, type=int)  # Region ID

        region_id = v7

        region_inform = {}
        region_inform["annotator_id"] = annotator_id
        region_inform["annotation_project"] = annotation_project
        region_inform["slide_uuid"] = slide_uuid
        region_inform["region_id"] = region_id

        mani = manifest.Manifest()
        wsi = mani.get_project_by_id(slide_id)
        svs_file_path = original_data_root + wsi[1] + '/' + wsi[2]
        annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + wsi[1] + '/'

        if not os.path.exists(annotation_root_folder):
            os.mkdir(annotation_root_folder)

        loc_tl_coor = (v1, v2)
        loc_viewing_size = (v3 - v1, v4 - v2)

        mask_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                         str(region_id) + '_mask' + '.txt'
        original_pic_url = annotation_root_folder + 'r' + str(v7) + '.png'
        if not os.path.exists(mask_file_name):
            if not os.path.exists(original_pic_url):
                oslide = openslide.OpenSlide(svs_file_path)
                patch = oslide.read_region((v1, v2), 0, (v3 - v1 + 1, v4 - v2 + 1))
                patch.save(annotation_root_folder + 'r' + str(v7) + '.png')
                oslide.close()
            mask_file_name = nuclei_annotation_v2_controller.boundary_2_mask(region_inform)

        return jsonify(
            background_url=original_pic_url + '?a=' + str(uuid.uuid1()),
            mask_url=mask_file_name + '?a=' + str(uuid.uuid1()),
            top_left_x=loc_tl_coor[0],
            top_left_y=loc_tl_coor[1],
            viewing_size_x=loc_viewing_size[0],
            viewing_size_y=loc_viewing_size[1],
        )

    @app.route('/nuclei_annotation_v2/_update_tb_list')
    def nuclei_annotation_v2_update_tb_list():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

        if not os.path.exists(annotation_root_folder):
            os.mkdir(annotation_root_folder)
        tba_list_db = annotation_root_folder + 'tba_list.db'
        db = nuclei_annotation_sqlite.SqliteConnector(tba_list_db)
        tba_result = db.get_RegionID_Centre()
        return jsonify(max_region=len(tba_result), reg_list=tba_result)

    @app.route('/nuclei_annotation_v2/_add_sw')
    def nuclei_annotation_v2_add_sw():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        allowed_annotator = range(7)
        if annotator_id in allowed_annotator:
            x = request.args.get('x', 0, type=int)
            y = request.args.get('y', 0, type=int)

            annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

            if not os.path.exists(annotation_root_folder):
                os.mkdir(annotation_root_folder)

            tba_list_db = annotation_root_folder + 'tba_list.db'
            db = nuclei_annotation_sqlite.SqliteConnector(tba_list_db)
            db.incert_RegionCentre(-1, x, y)

            message = 'Successfully added diagnostic region'
        else:
            message = 'Only annotator ' + str(allowed_annotator) + ' is allowed to add diagnostic region'

        return jsonify(status=message, num_status=1)

    @app.route('/nuclei_annotation_v2/_rm_sw')  # Add sub-window
    def nuclei_annotation_v2_rm_sw():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        allowed_annotator = range(7)

        if annotator_id in allowed_annotator:
            sw_id = request.args.get('sw_id', 0, type=int)

            annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

            tba_list_db = annotation_root_folder + 'tba_list.db'
            db = nuclei_annotation_sqlite.SqliteConnector(tba_list_db)
            db.delete_RegionCentre(sw_id)

            original_pic_url = annotation_root_folder + 'r' + str(sw_id) + '.png'
            if os.path.exists(original_pic_url):
                os.remove(original_pic_url)
            region_image_url = annotation_root_folder + 'r' + str(sw_id) + '.txt'
            if os.path.exists(region_image_url):
                os.remove(region_image_url)
            for annotator_id in range(7):
                annotator_data_url = annotation_root_folder + 'a' + str(annotator_id) + '_r' + str(sw_id) + '.txt'
                if os.path.exists(annotator_data_url):
                    os.remove(annotator_data_url)
                result_pic_url = annotation_root_folder + 'a' + str(annotator_id) + '_r' + str(sw_id) + '.png'
                if os.path.exists(result_pic_url):
                    os.remove(result_pic_url)
                points_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                                   str(sw_id) + '_points' + '.txt'
                if os.path.exists(points_file_name):
                    os.remove(points_file_name)
                grades_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                                   str(sw_id) + '_grades' + '.txt'
                if os.path.exists(grades_file_name):
                    os.remove(grades_file_name)

            message = 'Successfully removed diagnostic region'
        else:
            message = message = 'Only annotator ' + str(allowed_annotator) + ' is allowed to remove diagnostic region'

        return jsonify(status=message, num_status=1)

    @app.route('/nuclei_annotation_v2/update_grades', methods=['POST'])
    @login_required
    def nuclei_annotation_v2_update_grades():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)
        region_id = request.args.get('region_id', default="", type=str)

        region_inform = {}
        region_inform["annotator_id"] = annotator_id
        region_inform["annotation_project"] = annotation_project
        region_inform["slide_uuid"] = slide_uuid
        region_inform["region_id"] = region_id

        data = {}
        for key, value in request.form.items():
            if key.endswith('[]'):
                data[key[:-2]] = request.form.getlist(key)
            else:
                data[key] = value
        print(data)

        nuclei_annotation_v2_controller.update_grade(region_inform, data)
        return jsonify({"msg": "True"})

    @app.route('/nuclei_annotation_v2/points_grades')
    @login_required
    def nuclei_annotation_v2_points_grades():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)
        region_id = request.args.get('region_id', default="", type=str)

        annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

        points_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                           str(region_id) + '_points' + '.txt'
        grades_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                           str(region_id) + '_grades' + '.txt'

        if not os.path.exists(points_file_name):
            f_temp = open(points_file_name, 'w')
            f_temp.close()
        if not os.path.exists(grades_file_name):
            f_temp = open(grades_file_name, 'w')
            f_temp.close()

        points_file = open(points_file_name).readlines()
        grades_file = open(grades_file_name).readlines()

        points = []
        grades = []
        for item in points_file:
            points.append([int(item.split(' ')[0]), int(item.split(' ')[1])])
        for item in grades_file:
            grades.append(int(item))

        return jsonify({"grades": grades, "points": points})

    @app.route('/nuclei_annotation_v2/make_mask')
    @login_required
    def nuclei_annotation_v2_make_mask():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)
        region_id = request.args.get('region_id', default="", type=str)

        region_inform = {}
        region_inform["annotator_id"] = annotator_id
        region_inform["annotation_project"] = annotation_project
        region_inform["slide_uuid"] = slide_uuid
        region_inform["region_id"] = region_id

        nuclei_annotation_v2_controller.point_2_boundary(region_inform)
        nuclei_annotation_v2_controller.boundary_2_mask(region_inform)

        annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + slide_uuid + '/'
        result = {
            "background_url": annotation_root_folder + 'r' + str(region_id) + '.png'
                              + '?a=' + str(uuid.uuid4()),
            "mask_url": annotation_root_folder + 'a' + str(annotator_id) + '_r'
                        + str(region_id) + '_mask' + '.txt' + '?a=' + str(uuid.uuid4()),
        }
        return jsonify(result)

    @app.route('/nuclei_annotation_v2/_auto_predict')
    def nuclei_annotation_v2_auto_predict():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        v7 = request.args.get('var7', 0, type=int)  # Region ID

        region_id = v7

        region_inform = {}
        region_inform["annotator_id"] = annotator_id
        region_inform["annotation_project"] = annotation_project
        region_inform["slide_uuid"] = slide_uuid
        region_inform["region_id"] = region_id

        mani = manifest.Manifest()
        wsi = mani.get_project_by_id(slide_id)
        annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + wsi[1] + '/'

        if not os.path.exists(annotation_root_folder):
            os.mkdir(annotation_root_folder)

        original_pic_url = annotation_root_folder + 'r' + str(v7) + '.png'
        print(original_pic_url)

        boundary_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                             str(region_id) + '_boundary' + '.txt'
        annotation_file_name = annotation_root_folder + 'a' + str(annotator_id) + '_r' + \
                               str(region_id) + '_annotation' + '.txt'
        command = "/home1/zhc/.conda/envs/hovernet/bin/python3.6 " \
                  "/home1/zhc/singleInfer/demo.py " \
                  + original_pic_url + ' ' + boundary_file_name + ' ' + annotation_file_name
        print(command)
        os.system(command)
        nuclei_annotation_v2_controller.boundary_2_point(region_inform)
        nuclei_annotation_v2_controller.boundary_2_mask(region_inform)

        return jsonify({})
