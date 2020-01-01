from flask import Flask, render_template, request
from flask import jsonify
from Controller import dzi_online
from Controller import manifest_controller
from Controller import thread
from Controller import image_processing
from Controller import dataset_controller
import copy
import os
import uuid

app = Flask(__name__)
dzi_online.add_dzi_sever(app)

try:
    if os.path.exists('static/data'):
        os.remove('static/data')
    os.symlink(os.getcwd() + '/Data', 'static/data')
except:
    pass


@app.route('/')
@app.route('/table')
def table():
    return render_template('table.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader_file():
    slide_uuid = request.form['uuid']
    file = request.files['file']
    print(file.filename[-3:])
    if file.filename[-3:] == "txt":
        if not os.path.exists('manifest_temp/'):
            os.mkdir('manifest_temp/')
        file.save('manifest_temp/' + file.filename)
        dataset_controller.import_manifest('manifest_temp/' + file.filename)
        return render_template('warning.html', info='file uploaded successfully')
    else:
        if slide_uuid == "":
            slide_uuid = str(uuid.uuid4())
        if not os.path.exists('Data/' + slide_uuid):
            os.mkdir('Data/' + slide_uuid)
        try:
            file.save('Data/' + slide_uuid + '/' + file.filename)
            manifest_controller.add_wsi(slide_uuid, file.filename)
        except Exception as e:
            print(e)
            return render_template('warning.html', info='file uploaded fail')
        try:
            image_processing.generate_icon_image_from_svs_file('Data/' + slide_uuid + '/' + f.filename,
                                                               'Data/' + slide_uuid + '/icon.png')
        except Exception as e:
            print(e)
        return render_template('warning.html', info='file uploaded successfully')


@app.route('/make_bg_mask')
def make_bg_mask():
    slide_id = request.args.get('slide_id', type=int)
    thread.BackgroundThread(image_processing.make_bg, slide_id).start()
    return jsonify({"info": "Mission Started !", "time": "5"})


@app.route('/remove_wsi')
def remove_wsi():
    slide_id = request.args.get('slide_id', type=int)
    manifest_controller.remove_wsi_by_id(slide_id)
    return jsonify({"info": "Removed Successfully !", "time": "1"})


@app.route('/clear_db')
def clear_db():
    dataset_controller.clear_database()
    return jsonify({"info": "Clear Successfully!", "time": "1"})


@app.route('/slide')
def slide():
    slide_id = request.args.get('slide_id', default=1, type=int)
    mask_url = request.args.get('mask_url', default="", type=str)
    info = manifest_controller.get_info_by_id(slide_id)
    dzi_file_path = "static/data/" + str(info[1]) + '/' \
                    + str(info[2]) + ".dzi"
    if os.path.exists(dzi_file_path):
        slide_url = dzi_file_path
    else:
        slide_url = "/dzi_online/Data/" + str(info[1]) + '/' \
                    + str(info[2]) + ".dzi"
    mask_root = "static/data/" + str(info[1]) + '/'

    return render_template('slide.html', slide_url=slide_url, slide_id=slide_id,
                           mask_url=mask_url, mask_root=mask_root)


@app.route('/manifest_table_data')
def table_data():
    return jsonify(manifest_controller.get_table())


@app.route('/graph')
def graph():
    return render_template('graph.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/upload')
def upload_file():
    return render_template('upload.html')


@app.route('/data')
def data():
    s = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 10]
    t = {}
    t['x'] = copy.deepcopy(s)
    t['y'] = copy.deepcopy(s)
    t['y'][5] = 20
    return jsonify(t)

# app.run(debug=True)
