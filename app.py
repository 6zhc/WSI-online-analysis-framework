import tensorflow as tf

config = tf.ConfigProto()
# config.gpu_options.per_process_gpu_memory_fraction = 0.4 # 占用GPU90%的显存
# config.gpu_options.allow_growth = True
session = tf.Session(config=config)
import uuid
import json

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
from Server import nuclei_annotation_v2_server

from Controller import manifest_controller
from Controller import thread_controller
from Controller import image_processing
from Controller import dataset_controller
from Controller import mission_controller
from Controller import annotation_project_controller
import os, csv, openslide, shutil

from Model import nuclei_annotation_sqlite
from Model import manifest


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
nuclei_annotation_v2_server.add_annotation_sever(app)

app.config['JSON_AS_ASCII'] = False


@app.after_request
def cors(environ):
    environ.headers['Access-Control-Allow-Origin'] = '*'
    environ.headers['Access-Control-Allow-Method'] = '*'
    environ.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return environ

@app.route('/')
@login_required
def index():
    return redirect("/annotation_project_table")


@app.route('/table')
@login_required
def table1():
    table = request.args.get('table', type=str)
    # print(table)
    if table is None:
        return redirect("table?table=test_predict.csv")

    keys = []
    with open(table, encoding='utf-8')as f:
        f_csv = csv.DictReader(f)
        f_csv = list(f_csv)
        for key in f_csv[0]:
            if key[:6] == "result":
                keys.append({
                    "field": key, "headerName": key[7:],
                    "sortable": True, "resizable": True, "filter": 'agTextColumnFilter',
                })

    # table = request.args.get('table', default='test_predict.csv', type=str)
    return render_template('table.html', table=table, column_addition=json.dumps(keys))


@app.route('/items')
@login_required
def items():
    table = request.args.get('table', type=str)
    with open(table, encoding='utf-8')as f:
        f_csv = csv.DictReader(f)
        f_csv = list(f_csv)
        for i in range(len(f_csv)):
            for key in f_csv[i]:
                if is_number(f_csv[i][key]):
                    try:
                        f_csv[i][key] = int(f_csv[i][key])
                    except:
                        pass

        return jsonify({'data': f_csv, 'totals': len(f_csv)})


@app.route('/table2')
@login_required
def table2():
    table = request.args.get('table', type=str)
    if table is None:
        return redirect("table2?table=test2.csv")

    keys = []
    with open(table, encoding='utf-8')as f:
        f_csv = csv.DictReader(f)
        f_csv = list(f_csv)
        for key in f_csv[0]:
            if key[:6] == "result":
                keys.append({
                    "field": key, "headerName": key[7:],
                    "sortable": True, "resizable": True, "filter": 'agTextColumnFilter',
                })
    return render_template('table2.html', table=table, column_addition=json.dumps(keys))


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


# @app.route('/items_column')
# @login_required
# def items_column():
#     keys = []
#     table = request.args.get('table', type=str)
#     with open(table, encoding='utf-8')as f:
#         f_csv = csv.DictReader(f)
#         f_csv = list(f_csv)
#         for key in f_csv[0]:
#             if key[:6] == "result":
#                 keys.append(key)
#         return jsonify(keys)


# @app.route('/item2')
# @login_required
# def items2():
#     with open('test2.csv', encoding='utf-8')as f:
#         f_csv = csv.DictReader(f)
#         f_csv = list(f_csv)
#         for i in range(len(f_csv)):
#             for key in f_csv[i]:
#                 if is_number(f_csv[i][key]):
#                     f_csv[i][key] = int(f_csv[i][key])
#
#         return jsonify({'data': f_csv, 'totals': len(f_csv)})


@app.route('/find_slide')
@login_required
def find_slide():
    svs_file = request.args.get('svs_file', default="None", type=str)
    annotation_project = request.args.get('project', default="None", type=str)
    result = manifest_controller.get_project_by_similar_svs_file(svs_file)
    if 0 == len(result):
        return "未查询到相关切片。"
    # elif 1 == len(result):
    #     return redirect("/slide?slide_id=" + str(result[0][0]))
    else:
        result_string = ""
        count = 0
        for item in result:
            count += 1
            result_string += "<p><a href='" + "/slide?slide_id=" + str(item[0]) + "'>【" + str(count) + "】</a> "
            result_string += str(item)
            result_string += " <a target='_blank' href='" + "/freehand_annotation?slide_id=" \
                             + str(item[0]) + "&project=" + annotation_project + "'>【区域标注】</a> "
            result_string += " <a target='_blank' href='" + "/nuclei_annotation?slide_id=" \
                             + str(item[0]) + "&project=" + annotation_project + "'>【细胞核标注】</a> "
            if os.path.exists("static/data/analysis_data/" + str(item[1]) + '/'):
                for mask in sorted(os.listdir("static/data/analysis_data/" + str(item[1]) + '/')):
                    result_string += "<p style='text-indent:3em;'> <a target='_blank' href='" + "/slide?slide_id=" \
                                     + str(item[0]) + "&mask_url=" + mask + "'>" + str(mask) + "</a> </p>"
            result_string += " </p>"
        return result_string


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
        count = 0
        if os.path.exists('export/' + project + '_slide_table.txt'):
            for wsi in open('export/' + project + '_slide_table.txt').readlines():

                slide_id = int(wsi.split('\t')[0])
                temp = {"id": slide_id, "text": wsi.replace('\t', ' ')}
                data.append(temp)

        def takeSecond(elem):
            return elem["id"]

        data.sort(key=takeSecond)
        for index in range(len(data)):
            count += 1
            data[index]["text"] = "【" + str(count) + "】" + data[index]["text"]
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


@app.route('/export_region')
@login_required
def export_region():
    return render_template('export_region.html')


@app.route('/make_region')
@login_required
def make_region():
    manifest_name = request.args.get('manifest_name', type=str)
    region_size = request.args.get('region_size', type=int)
    if os.path.exists("static/export/" + manifest_name + "_" + str(region_size) + ".zip"):
        os.remove("static/export/" + manifest_name + "_" + str(region_size) + ".zip")

    thread_controller.BackgroundThread(make_region_back, manifest_name, region_size).start()
    return "static/export/" + manifest_name + "_" + str(region_size) + ".zip" + "?random=" + str(uuid.uuid4())


def make_region_back(manifest_name, region_size):
    original_data_root = 'static/data/Original_data/'
    nuclei_annotation_data_root = "static/data/nuclei_annotation_data/"
    export_folder = "region/" + manifest_name + "_" + str(region_size) + "/"
    if os.path.exists(export_folder):
        shutil.rmtree(export_folder)
    os.mkdir(export_folder)
    manifest_file = open(export_folder + "manifest.txt", "w")
    slide_ids = os.listdir(nuclei_annotation_data_root + manifest_name + '/')
    for slide_ID in slide_ids:
        print(slide_ID)
        wsi = manifest_controller.get_info_by_uuid(slide_ID)
        svs_file_path = original_data_root + wsi[1] + '/' + wsi[2]
        tba_list_db = nuclei_annotation_data_root + manifest_name + '/' + wsi[1] + '/' + 'tba_list.db'
        db = nuclei_annotation_sqlite.SqliteConnector(tba_list_db)
        tba_result = db.get_RegionID_Centre()
        if len(tba_result) > 0:
            if not os.path.exists(export_folder + wsi[2]):
                os.mkdir(export_folder + wsi[2])
            oslide = openslide.OpenSlide(svs_file_path)
            manifest_file.writelines(wsi[1] + '\t' + wsi[2] + '\t' + 'None' + os.linesep)
            for item in tba_result:
                patch = oslide.read_region((item[1] - 256 - int(region_size / 2), item[2] - 256 - int(region_size / 2)),
                                           0, (region_size, region_size))
                patch.save(
                    export_folder + wsi[2] + '/' + str(item[1]) + '_' + str(item[2]) + '_' + str(region_size) + '.png')
            oslide.close()

    manifest_file.close()
    shutil.make_archive("export/" + manifest_name + "_" + str(region_size) + "/", 'zip', export_folder)


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
