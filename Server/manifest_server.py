from flask import render_template, request, redirect
from flask import jsonify
from flask_login import login_required

from Controller import manifest_controller
from Controller import thread_controller
from Controller import image_processing
from Controller import dataset_controller
from Controller import annotation_project_controller

import os
import uuid

icon_root = 'static/data/slide_icon/'

def add_manifest_server(app):
    @app.route('/slide_table')
    @login_required
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

    @app.route('/manifest_table_data')
    def table_data():
        page_no = request.args.get('page_no', default=1, type=int)
        item_per_page = request.args.get('item_per_page', default=15, type=int)
        return jsonify(
            manifest_controller.get_table(page_no * item_per_page - item_per_page, page_no * item_per_page, 0))

    @app.route('/refresh_manifest_table_data')
    def refresh_manifest_table_data():
        thread_controller.BackgroundThread(manifest_controller.get_table).start()
        return redirect('/manifest_table')

    @app.route('/continue_slide_id')
    def continue_slide_id():
        manifest_controller.continue_slide_id()
        thread_controller.BackgroundThread(annotation_project_controller.refresh_npy).start()
        return jsonify({"mas": 'None'})

    @app.route('/remove_wsi')
    def remove_wsi():
        slide_id = request.args.get('slide_id', type=int)
        manifest_controller.remove_wsi_by_id(slide_id)
        return jsonify({"info": "Removed Successfully !", "time": "1"})

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
            if not os.path.exists('Data/Original_data/' + slide_uuid):
                os.mkdir('Data/Original_data/' + slide_uuid)
            try:
                file.save('Data/Original_data/' + slide_uuid + '/' + file.filename)
                manifest_controller.add_wsi(slide_uuid, file.filename)
            except Exception as e:
                print(e)
                return render_template('warning.html', info='file uploaded fail')
            try:
                if not os.path.exists(icon_root + slide_uuid + '/'):
                    os.mkdir(icon_root + slide_uuid + '/')
                icon_file_path = icon_root + slide_uuid + '/' + 'icon.png'
                image_processing.generate_icon_image_from_svs_file(
                    'Data/Original_data/' + slide_uuid + '/' + file.filename,
                    icon_file_path)
            except Exception as e:
                print(e)
            return render_template('warning.html', info='file uploaded successfully')
