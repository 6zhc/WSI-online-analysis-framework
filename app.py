from flask import Flask, render_template, request, redirect
from flask import jsonify

from flask_login import login_required, current_user

from Server import dzi_online_server
from Server import freehand_annotation_server
from Server import nuclei_annotation_server
from Server import annotation_project_server
from Server import manifest_server
from Server import mission_server
from Server import user_server
from Server import re_annotation_server

from Controller import manifest_controller
from Controller import thread_controller
from Controller import image_processing
from Controller import dataset_controller
from Controller import mission_controller
from Controller import annotation_project_controller
import os, csv

try:
    if os.path.exists('static/data'):
        os.remove('static/data')
    os.symlink(os.getcwd() + '/Data', 'static/data')
except:
    pass

try:
    if os.path.exists('static/export'):
        os.remove('static/export')
    os.symlink(os.getcwd() + '/export', 'static/export')
except:
    pass


app = Flask(__name__)
user_server.add_user_server(app)
dzi_online_server.add_dzi_sever(app)
freehand_annotation_server.add_annotation_sever(app)
nuclei_annotation_server.add_annotation_sever(app)
annotation_project_server.add_annotation_project_sever(app)
mission_server.add_mission_server(app)
manifest_server.add_manifest_server(app)
re_annotation_server.add_re_annotation_sever(app)


@app.route('/')
@login_required
def index():
    return redirect("/annotation_project_table")


@app.route('/items')
@login_required
def items():
    with open('test.csv')as f:
        f_csv = csv.DictReader(f)
        return jsonify({'data': list(f_csv), 'totals': len(list(f_csv))})


@app.route('/table')
@login_required
def table():
    return render_template('table.html')


@app.route('/slide')
@login_required
def slide():
    slide_id = request.args.get('slide_id', default=1, type=int)
    mask_url = request.args.get('mask_url', default="", type=str)
    info = manifest_controller.get_info_by_id(slide_id)
    dzi_file_path = "static/data/dzi_data/" + str(info[1]) + '/' \
                    + str(info[2]) + ".dzi"
    if os.path.exists(dzi_file_path):
        slide_url = dzi_file_path
    else:
        slide_url = "/dzi_online/Data/Original_data/" + str(info[1]) + '/' \
                    + str(info[2]) + ".dzi"
    mask_root = "static/data/analysis_data/" + str(info[1]) + '/'

    return render_template('slide.html', slide_url=slide_url, slide_id=slide_id,
                           mask_url=mask_url, mask_root=mask_root)


@app.route('/available_slide')
@login_required
def available_slide():
    project = request.args.get('project', default="", type=str)
    if project == "":
        return jsonify(manifest_controller.get_available_slide_id())
    else:
        data = []
        for wsi in open('export/' + project + '_slide_table.txt').readlines():
            slide_id = int(wsi.split('\t')[0])
            temp = {"id": slide_id, "text": slide_id}
            data.append(temp)
        return jsonify(data)


@app.route('/available_model')
@login_required
def available_model():
    return jsonify(mission_controller.get_available_model())


@app.route('/make_bg_mask')
@login_required
def make_bg_mask():
    slide_id = request.args.get('slide_id', type=int)
    thread_controller.BackgroundThread(image_processing.make_bg, slide_id).start()
    return jsonify({"info": "Mission Started !", "time": "5"})


@app.route('/make_pre_mask')
@login_required
def make_pre_mask():
    slide_id = request.args.get('slide_id', type=int)
    model_name = request.args.get('model_name', type=str, default="0")
    thread_controller.BackgroundThread(image_processing.predict_mask_with_job_id, slide_id, model_name).start()
    return jsonify({"info": "Mission Started !", "time": "-1"})


@app.route('/clear_db')
@login_required
def clear_db():
    dataset_controller.clear_database()
    return jsonify({"info": "Clear Successfully!", "time": "1"})


@app.route('/upload')
@login_required
def upload_file():
    return render_template('upload.html')


@app.route('/muti-slide')
@login_required
def muti_slide():
    return render_template('multi-slide.html')

# @app.route('/graph')
# def graph():
#     return render_template('graph.html')
#
#
# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')
#
#
# @app.route('/data')
# def data():
#     s = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 10]
#     t = {}
#     t['x'] = copy.deepcopy(s)
#     t['y'] = copy.deepcopy(s)
#     t['y'][5] = 20
#     return jsonify(t)

# app.run(debug=True)
