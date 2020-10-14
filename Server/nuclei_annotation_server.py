import cv2
import numpy as np
import openslide
import os
import uuid
import tensorflow as tf

from flask_login import login_required, current_user
from flask import jsonify, request, render_template

from Controller import manifest_controller
from Model import manifest
from Model import nuclei_annotation_sqlite
from Controller.segmentation_algorithm.segmentation_algorithm import SegmentationModel

# model = SegmentationModel()
# graph = tf.get_default_graph()

original_data_root = 'static/data/Original_data/'
nuclei_annotation_data_root = "static/data/nuclei_annotation_data/"


def add_annotation_sever(app):
    @app.route('/nuclei_annotation', methods=['GET', 'POST'])
    @login_required
    def nuclei_annotation():

        annotator_id = current_user.get_id()
        # annotator_id = request.args.get('annotator_id', default=1, type=int)
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

        return render_template('nuclei_annotation.html', slide_url=slide_url, slide_id=slide_id,
                               annotator_id=annotator_id, slide_uuid=info[1], project=annotation_project)

    @app.route('/nuclei_annotation/_get_info')
    def nuclei_annotation_get_info():

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

    @app.route('/nuclei_annotation/_update_image')
    def nuclei_annotation_update_image():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        mani = manifest.Manifest()
        wsi = mani.get_project_by_id(slide_id)
        svs_file_path = original_data_root + wsi[1] + '/' + wsi[2]
        annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + wsi[1] + '/'

        if not os.path.exists(annotation_root_folder):
            os.mkdir(annotation_root_folder)

        error_message = 'N/A'
        request_status = 0

        v1 = request.args.get('var1', 0, type=int)  # Top-left x coordinate
        v2 = request.args.get('var2', 0, type=int)  # Top-left y coordinate
        v3 = request.args.get('var3', 0, type=int)  # Bottom-right x
        v4 = request.args.get('var4', 0, type=int)  # Bottom-right y
        v5 = request.args.get('var5', 0, type=int)  # Viewer width (pixel)
        v6 = request.args.get('var6', 0, type=int)  # Viewer height (pixel)
        v7 = request.args.get('var7', 0, type=int)  # Region ID

        loc_tl_coor = (v1, v2)
        loc_viewing_size = (v3 - v1, v4 - v2)
        loc_viewer_size = (v5, v6)

        result_pic_url = annotation_root_folder + 'a' + str(annotator_id) + '_r' + str(v7) + '.png'
        if not os.path.exists(result_pic_url):
            original_pic_url = annotation_root_folder + 'r' + str(v7) + '.png'
            if not os.path.exists(original_pic_url):
                oslide = openslide.OpenSlide(svs_file_path)
                patch = oslide.read_region((v1, v2), 0, (v3 - v1 + 1, v4 - v2 + 1))
                patch.save(annotation_root_folder + 'r' + str(v7) + '.png')
                oslide.close()
            original_pic = cv2.imread(original_pic_url)

            region_image_url = annotation_root_folder + 'r' + str(v7) + '.txt'
            if not os.path.exists(region_image_url):
                # with graph.as_default():
                #     mask = model.predict(original_pic_url)
                # print(mask)
                # region_image = model.water_image(mask)
                region_image = np.zeros([512, 512], dtype=np.uint8)
                np.savetxt(region_image_url, region_image, fmt="%d", delimiter=",")
            else:
                region_image = np.loadtxt(region_image_url, delimiter=",", dtype=int)

            annotator_data_url = annotation_root_folder + 'a' + str(annotator_id) + '_r' + str(v7) + '.txt'
            if not os.path.exists(annotator_data_url):
                annotator_data = np.zeros(np.max(region_image) + 1)
                print(annotator_data)
                np.savetxt(annotator_data_url, annotator_data, fmt="%d", delimiter=",")
            else:
                annotator_data = np.loadtxt(annotator_data_url, delimiter=",", dtype=int)

            colour = [tuple([124, 252, 0]), tuple([0, 255, 255]), tuple([137, 43, 224]),
                      tuple([255 * 0.82, 255 * 0.41, 255 * 0.12]), tuple([255, 0, 0]), tuple([0, 128, 255])]
            color_scheme = [
                [0.49, 0.99, 0], [0, 1, 1], [0.54, 0.17, 0.88], [0.82, 0.41, 0.12],
                [1, 0, 0], [0, 0.5, 1]
            ]
            mask = np.zeros(original_pic.shape)
            mask[region_image == -1] = tuple([0, 0, 0])
            for i, val in enumerate(annotator_data):
                if i != 1 and val != 0:
                    # mask[region_image == i] = colour[val - 1]
                    mask[region_image == i] = (original_pic[region_image == i] * 2.7 + colour[val - 1]) / 3.3
                # mask[region_image == i][0] = original_pic[region_image == i][0] *color_scheme[val - 1][0]
                # mask[region_image == i][1] = original_pic[region_image == i][1] *color_scheme[val - 1][1]
                # mask[region_image == i][2] = original_pic[region_image == i][2] *color_scheme[val - 1][2]
                else:
                    mask[region_image == i] = original_pic[region_image == i]  # web.rm_file(last_url)
            mask[region_image == -1] = tuple([255, 0, 0])
            bound_size = 4
            mask[:, 0:bound_size] = tuple([255, 0, 0])
            mask[:, 511 - bound_size:511] = tuple([255, 0, 0])
            mask[0:bound_size, :] = tuple([255, 0, 0])
            mask[511 - bound_size:511, :] = tuple([255, 0, 0])

            cv2.imwrite(result_pic_url, mask)

        # Update URL configuration
        slide_url = 'static/data/nuclei_annotation_data/' + annotation_project + '/' \
                    + wsi[1] + '/a' + str(annotator_id) + '_r' + str(v7) + '.png'
        result_pic = cv2.imread(result_pic_url)
        cv2.imwrite(slide_url, result_pic)

        return jsonify(
            slide_url=slide_url + '?a=' + str(uuid.uuid1()),
            top_left_x=loc_tl_coor[0],
            top_left_y=loc_tl_coor[1],
            viewing_size_x=loc_viewing_size[0],
            viewing_size_y=loc_viewing_size[1],
            exit_code=request_status,
            error_message=error_message
        )

    @app.route('/nuclei_annotation/_record', methods=['GET', 'POST'])
    def nuclei_annotation_record():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        annotation_root_folder = nuclei_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

        req_form = request.form
        num_of_points = int(len(req_form) / 4)

        pt_list_att = ('[x]', '[y]', '[grading]', '[region_id]')
        print(req_form)
        region_image_url = annotation_root_folder + 'r' + str(req_form['0[region_id]']) + '.txt'
        region_image = np.loadtxt(region_image_url, delimiter=",", dtype=int)
        annotator_data_url = annotation_root_folder + 'a' + str(annotator_id) + '_r' + req_form['0[region_id]'] + '.txt'
        annotator_data = np.loadtxt(annotator_data_url, delimiter=",", dtype=int)

        temp = 1
        for i in range(num_of_points):
            temp_new = region_image[int(int(req_form[str(i) + '[y]'])), int(int(req_form[str(i) + '[x]']))]
            if temp != temp_new and temp_new > 1:
                temp = temp_new
                annotator_data[temp] \
                    = int(req_form[str(i) + '[grading]'])
        np.savetxt(annotator_data_url, annotator_data, fmt="%d", delimiter=",")

        result_pic_url = annotation_root_folder + 'a' + str(annotator_id) + '_r' + req_form['0[region_id]'] + '.png'

        if os.path.exists(result_pic_url):
            os.remove(result_pic_url)

        return jsonify(
            pt_false_x=[],
            pt_false_y=[],
            region_id=req_form['0[region_id]']
        )

    @app.route('/nuclei_annotation/_update_tb_list')
    def nuclei_annotation_update_tb_list():
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

    @app.route('/nuclei_annotation/_add_sw')
    def nuclei_annotation_add_sw():
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

    @app.route('/nuclei_annotation/_rm_sw')  # Add sub-window
    def nuclei_annotation_rm_sw():
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

            message = 'Successfully removed diagnostic region'
        else:
            message = message = 'Only annotator ' + str(allowed_annotator) + ' is allowed to remove diagnostic region'

        return jsonify(status=message, num_status=1)
