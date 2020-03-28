from flask import Flask, render_template, request, redirect
from flask import jsonify
from Controller import dzi_online_controller
from Controller import manifest_controller
from Controller import thread_controller
from Controller import image_processing
from Controller import dataset_controller
from Controller import mission_controller
import os
import uuid


app = Flask(__name__)
dzi_online_controller.add_dzi_sever(app)

try:
    if not os.path.exists("Data"):
        os.mkdir("Data")
    if os.path.exists('static/data'):
        os.remove('static/data')
    os.symlink(os.getcwd() + '/Data', 'static/data')
except:
    pass


@app.route('/')
@app.route('/slide_table')
def slide_table():
    page_no = request.args.get('page_no', default=1, type=int)
    item_per_page = request.args.get('item_per_page', default=15, type=int)
    total_page = (manifest_controller.get_total_number() + item_per_page - 1) // item_per_page
    if total_page == 0:
        page_no = 1
    elif page_no <= 0:
        page_no = 1
    elif page_no > total_page:
        page_no = total_page
    return render_template('slide_table.html', page_no=page_no, total_page=total_page, item_per_page=item_per_page)


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
    thread_controller.BackgroundThread(image_processing.make_bg, slide_id).start()
    return jsonify({"info": "Mission Started !", "time": "5"})


@app.route('/make_pre_mask')
def make_pre_mask():
    slide_id = request.args.get('slide_id', type=int)
    model_name = request.args.get('model_name', type=str, default="0")
    thread_controller.BackgroundThread(image_processing.predict_mask_with_job_id, slide_id, model_name).start()
    return jsonify({"info": "Mission Started !", "time": "-1"})


@app.route('/remove_wsi')
def remove_wsi():
    slide_id = request.args.get('slide_id', type=int)
    manifest_controller.remove_wsi_by_id(slide_id)
    return jsonify({"info": "Removed Successfully !", "time": "1"})


@app.route('/remove_mission')
def remove_mission():
    job_id = request.args.get('slide_id', type=int)
    mission_controller.remove_mission_by_id(job_id)
    return jsonify({"info": "Removed Successfully !", "time": "-1"})


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
    page_no = request.args.get('page_no', default=1, type=int)
    item_per_page = request.args.get('item_per_page', default=15, type=int)
    return jsonify(manifest_controller.get_table(page_no * item_per_page - item_per_page, page_no * item_per_page))


@app.route('/mission_table')
def mission_table():
    page_no = request.args.get('page_no', default=1, type=int)
    item_per_page = request.args.get('item_per_page', default=15, type=int)
    slide_uuid = request.args.get('slide_uuid', default="", type=str)
    total_page = (len(mission_controller.get_table(slide_uuid)) + item_per_page - 1) // item_per_page
    if total_page == 0:
        page_no = 1
    elif page_no <= 0:
        page_no = 1
    elif page_no > total_page:
        page_no = total_page
    return render_template('mission_table.html', page_no=page_no, total_page=total_page,
                           item_per_page=item_per_page, slide_uuid=slide_uuid)


# @app.route('/predict_mask_make', methods=['GET', 'POST'])
# def predict_mask_make():
#     slide_id = request.form['slide_id']
#     slide_uuid = request.form['uuid']
#     model_name = request.form['model_name']
#     thread.BackgroundThread(image_processing.predict_mask_with_job_id, slide_id, model_name).start()
#     return redirect('mission_table')


@app.route('/mission_table_data')
def mission_table_data():
    page_no = request.args.get('page_no', default=1, type=int)
    item_per_page = request.args.get('item_per_page', default=15, type=int)
    slide_uuid = request.args.get('slide_uuid', default="", type=str)
    return jsonify(
        mission_controller.get_table(slide_uuid)[page_no * item_per_page - item_per_page:page_no * item_per_page])


@app.route('/available_slide')
def available_slide():
    return jsonify(manifest_controller.get_available_slide_id())


@app.route('/available_model')
def available_model():
    return jsonify(mission_controller.get_available_model())


@app.route('/upload')
def upload_file():
    return render_template('upload.html')

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
