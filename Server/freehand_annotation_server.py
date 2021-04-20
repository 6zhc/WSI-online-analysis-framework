import cv2
import numpy
import openslide
import os
import uuid

from flask import jsonify, request, render_template
from flask_login import login_required, current_user

from Controller import manifest_controller
from Model import freehand_annotation_sqlite
from Model import manifest

original_data_root = 'static/data/Original_data/'
freehand_annotation_data_root = "static/data/freehand_annotation_data/"


def add_annotation_sever(app):
    @app.route('/freehand_annotation', methods=['GET', 'POST'])
    @login_required
    def freehand_annotation():

        annotator_id = current_user.get_id()
        # annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)

        slide_id = request.args.get('slide_id', default=-1, type=int)
        if slide_id == -1:
            try:
                slide_id = current_user.slideID[annotator_id + '_' + annotation_project + "_" + "freehand"]
            except:
                temp = []
                for wsi in open('export/' + annotation_project + '_slide_table.txt').readlines():
                    slide_id = int(wsi.split('\t')[0])
                    temp.append(slide_id)
                slide_id = int(numpy.min(temp))
        current_user.slideID[annotator_id + '_' + annotation_project + "_" + "freehand"] = slide_id

        info = manifest_controller.get_info_by_id(slide_id)
        dzi_file_path = "/static/data/dzi_data/" + str(info[1]) + '/' \
                        + str(info[2]) + ".dzi"
        if os.path.exists(dzi_file_path):
            slide_url = dzi_file_path
        else:
            slide_url = "/dzi_online/Data/Original_data/" + str(info[1]) + '/' \
                        + str(info[2]) + ".dzi"

        return render_template('freehand_annotation.html', slide_url=slide_url, slide_id=slide_id,
                               annotator_id=annotator_id, slide_uuid=info[1], project=annotation_project)

    @app.route('/freehand_annotation/_get_info')
    def freehand_annotation_get_info():

        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        mani = manifest.Manifest()
        wsi = mani.get_project_by_id(slide_id)
        svs_file_path = original_data_root + wsi[1] + '/' + wsi[2]
        dimensions = openslide.OpenSlide(svs_file_path).dimensions
        MPP = openslide.OpenSlide(svs_file_path).properties.get("aperio.MPP")
        properties = dict(openslide.OpenSlide(svs_file_path).properties)

        w = dimensions[0]
        h = dimensions[1]
        return jsonify(
            img_width=w,
            img_height=h,
            um_per_px=MPP if MPP else 0.25,
            max_image_zoom=0,  # max_image_zoom,
            toggle_status=0,  # toggle_status
            properties=properties
        )

    @app.route('/freehand_annotation/_clear_lines')
    def freehand_annotation_clear_lines():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        annotation_root_folder = freehand_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

        if not os.path.exists(annotation_root_folder):
            os.mkdir(annotation_root_folder)
        annotaion_db = annotation_root_folder + 'a' + str(annotator_id) + '.db'

        db = freehand_annotation_sqlite.SqliteConnector(annotaion_db)
        db.delete_all_lines()
        return jsonify(
            exit_code=True,
        )

    @app.route('/freehand_annotation/_undo_lines')
    def freehand_annotation_undo_lines():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        annotation_root_folder = freehand_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

        if not os.path.exists(annotation_root_folder):
            os.mkdir(annotation_root_folder)
        annotaion_db = annotation_root_folder + 'a' + str(annotator_id) + '.db'

        db = freehand_annotation_sqlite.SqliteConnector(annotaion_db)
        db.del_max_branch()
        return jsonify(
            exit_code=True,
        )

    @app.route('/freehand_annotation/_update_image')
    def freehand_annotation_update_image():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        annotation_root_folder = freehand_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

        if not os.path.exists(annotation_root_folder):
            os.mkdir(annotation_root_folder)
        annotaion_db = annotation_root_folder + 'a' + str(annotator_id) + '.db'

        error_message = 'N/A'
        request_status = 0

        v1 = request.args.get('var1', 0, type=int)  # Top-left x coordinate
        v2 = request.args.get('var2', 0, type=int)  # Top-left y coordinate
        v3 = request.args.get('var3', 0, type=int)  # Bottom-right x
        v4 = request.args.get('var4', 0, type=int)  # Bottom-right y
        v5 = request.args.get('var5', 0, type=int)  # Viewer width (pixel)
        v6 = request.args.get('var6', 0, type=int)  # Viewer height (pixel)

        loc_tl_coor = (v1, v2)
        loc_viewing_size = (v3 - v1, v4 - v2)
        loc_viewer_size = (v5, v6)

        # Update URL configuration
        slide_url = 'static/cache/' + str(uuid.uuid1())[:13] + '.png'

        mask = numpy.zeros([v6, v5, 4])

        db = freehand_annotation_sqlite.SqliteConnector(annotaion_db)
        color = [[0, 0, 255, 255], [0, 255, 0, 255], [255, 0, 0, 255], [0, 0, 0, 255]]
        # print(db.get_lines())

        for temp in db.get_lines_in_area(int(v1), int(v2), int(v3), int(v4)):
            cv2.line(mask, (int((temp[1] - v1) / (v3 - v1) * v5), int((temp[2] - v2) / (v4 - v2) * v6)),
                     (int((temp[3] - v1) / (v3 - v1) * v5),
                      int((temp[4] - v2) / (v4 - v2) * v6)), color[temp[5] - 1], 3)
        write_url = slide_url
        cv2.imwrite(write_url, mask)

        return jsonify(
            slide_url=slide_url + '?a=' + str(uuid.uuid1()),
            top_left_x=loc_tl_coor[0],
            top_left_y=loc_tl_coor[1],
            viewing_size_x=loc_viewing_size[0],
            viewing_size_y=loc_viewing_size[1],
            exit_code=request_status,
            error_message=error_message
        )

    @app.route('/freehand_annotation/_record', methods=['GET', 'POST'])
    def freehand_annotation_record():
        slide_id = request.args.get('slide_id', default=1, type=int)
        annotator_id = request.args.get('annotator_id', default=1, type=int)
        annotation_project = request.args.get('project', default="None", type=str)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)

        annotation_root_folder = freehand_annotation_data_root + annotation_project + '/' + slide_uuid + '/'

        if not os.path.exists(annotation_root_folder):
            os.mkdir(annotation_root_folder)
        annotaion_db = annotation_root_folder + 'a' + str(annotator_id) + '.db'

        req_form = request.form
        num_of_points = int(len(req_form) / 3)

        pt_list_att = ('[x]', '[y]', '[grading]')

        db = freehand_annotation_sqlite.SqliteConnector(annotaion_db)

        # In one round, the grading and pslv could be updated only once.
        data = []
        for i in range(num_of_points):
            if int(req_form[str(i) + '[grading]']) > 0:
                if i == 0:
                    continue
                if (int(req_form[str(i - 1) + '[x]']) == int(req_form[str(i) + '[x]'])) \
                        and (int(req_form[str(i - 1) + '[y]']) == int(req_form[str(i) + '[y]'])):
                    continue
                data.append(tuple([int(req_form[str(i - 1) + '[x]']), int(req_form[str(i - 1) + '[y]']),
                                   int(req_form[str(i) + '[x]']), int(req_form[str(i) + '[y]']),
                                   int(req_form[str(i) + '[grading]'])]))
            elif int(req_form[str(i) + '[grading]']) == 0:
                db.delete_points(int(req_form[str(i) + '[x]']), int(req_form[str(i) + '[y]']))
            elif int(req_form[str(i) + '[grading]']) == -1:
                db.delete_lines(int(req_form[str(i) + '[x]']), int(req_form[str(i) + '[y]']))

        if len(data):
            db.incert_lines(data)

        return jsonify(
            pt_false_x=[],
            pt_false_y=[],
            region_id=0
        )
