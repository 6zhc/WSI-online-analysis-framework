import json
import os
import time

from flask import render_template, redirect, request, Response
from flask import jsonify

from flask_login import login_required

from Controller import thread_controller
from Controller import annotation_project_controller


def add_annotation_project_sever(app):
    @app.route('/annotation_project_table')
    @login_required
    def annotation_project_table():
        return render_template('annotation_project_table.html')

    @app.route('/annotation_project_table_data')
    def annotation_project_table_data():
        return jsonify(
            annotation_project_controller.get_table())

    @app.route('/refresh_annotation_slide')
    def refresh_annotation_slide():
        thread_controller.BackgroundThread(annotation_project_controller.refresh_npy).start()
        # annotation_project_controller.refresh_npy()
        return redirect('/annotation_project_table')

    @app.route('/refresh_nuclei_annotation_progress')
    def refresh_nuclei_annotation_progress():
        annotation_project_controller.refresh_nuclei_annotation_progress()
        return redirect('/annotation_project_table')

    @app.route('/refresh_freehand_annotation_progress')
    def refresh_freehand_annotation_progress():
        annotation_project_controller.refresh_freehand_annotation_progress()
        return redirect('/annotation_project_table')

    @app.route('/export_freehand_annotation')
    def export_freehand_annotation():
        manifest_file = request.args.get('manifest_file', type=str)

        thread_controller.BackgroundThread(annotation_project_controller.export_freehand_annotation_data,
                                           manifest_file).start()

        return redirect('/annotation_project_table')

    @app.route('/export_freehand_annotation_single', methods=("GET", "POST"))
    def export_freehand_annotation_single():
        if request.method == 'GET':

            manifest_file = request.args.get('manifest_file', type=str)
            slide_id = request.args.get('slide_id', type=str)
            manifest_txt = [item for item in open(manifest_file).readlines() if item[:len(slide_id)] == slide_id]
            if len(manifest_txt) == 0:
                return "input ERROR!!"
            export_file = annotation_project_controller.export_freehand_annotation_data(manifest_file, manifest_txt)
            with open(export_file, 'rb') as f:
                data = f.readlines()
            os.remove(export_file)
            return Response(data, headers={
                'Content-Type': 'application/zip',
                'Content-Disposition': 'attachment; filename=%s;' % (
                        manifest_file.rsplit("/", 1)[1][:-4] + '_freehand_annotation.zip')
            })

        if request.method == 'POST':
            manifest_file = request.form.get("manifest_file")
            slide_id = request.form.getlist('slide_id[]')
            print(slide_id)
            print(manifest_file)
            manifest_txt = [item for item in open(manifest_file).readlines() if item[:len(slide_id[0])] in slide_id]
            if len(manifest_txt) == 0:
                return "input ERROR!!"
            print(manifest_txt)
            export_file = "static/export/" + time.ctime() + \
                          " " + manifest_file.rsplit("/", 1)[1][:-4] + " freehand annotation.zip"
            thread_controller.BackgroundThread(annotation_project_controller.export_freehand_annotation_data,
                                               manifest_file, manifest_txt, export_file).start()
            return export_file

    @app.route('/export_freehand_annotation_data')
    def export_freehand_annotation_data():
        manifest_file = request.args.get('manifest_file', type=str)
        result = annotation_project_controller.export_freehand_annotation_list(manifest_file)
        return jsonify({'data': result, 'totals': len(result)})

    @app.route('/export_freehand_annotation_page')
    def export_freehand_annotation_page():
        manifest_file = request.args.get('manifest_file', type=str)
        return render_template("export_table.html", manifest_name=manifest_file,
                               annotation_style="freehand", column_addition=json.dumps({}))

    @app.route('/export_nuclei_annotation')
    def export_nuclei_annotation():
        manifest_file = request.args.get('manifest_file', type=str)

        thread_controller.BackgroundThread(annotation_project_controller.export_nuclei_annotation_data,
                                           manifest_file).start()

        return redirect('/annotation_project_table')

    @app.route('/export_nuclei_annotation_single', methods=("GET", "POST"))
    def export_nuclei_annotation_single():
        if request.method == 'GET':
            manifest_file = request.args.get('manifest_file', type=str)
            slide_id = request.args.get('slide_id', type=str)
            manifest_txt = [item for item in open(manifest_file).readlines() if item[:len(slide_id)] == slide_id]
            if len(manifest_txt) == 0:
                return "input ERROR!!"
            print(manifest_txt)
            export_file = annotation_project_controller.export_nuclei_annotation_data(manifest_file, manifest_txt)
            with open(export_file, 'rb') as f:
                data = f.readlines()
            os.remove(export_file)
            return Response(data, headers={
                'Content-Type': 'application/zip',
                'Content-Disposition': 'attachment; filename=%s;'
                                       % (manifest_file.rsplit("/", 1)[1][:-4] + '_nuclei_annotation.zip')
            })
        if request.method == 'POST':
            manifest_file = request.form.get("manifest_file")
            slide_id = request.form.getlist('slide_id[]')
            print(slide_id)
            print(manifest_file)
            manifest_txt = [item for item in open(manifest_file).readlines() if item[:len(slide_id[0])] in slide_id]
            if len(manifest_txt) == 0:
                return "input ERROR!!"
            print(manifest_txt)
            export_file = "static/export/" + time.ctime() + \
                          " " + manifest_file.rsplit("/", 1)[1][:-4] + " nuclei annotation.zip"
            thread_controller.BackgroundThread(annotation_project_controller.export_nuclei_annotation_data,
                                               manifest_file, manifest_txt, export_file).start()
            return export_file

    @app.route('/export_nuclei_annotation_data')
    def export_nuclei_annotation_data():
        manifest_file = request.args.get('manifest_file', type=str)
        result = annotation_project_controller.export_nuclei_annotation_list(manifest_file)
        return jsonify({'data': result, 'totals': len(result)})

    @app.route('/export_nuclei_annotation_page')
    def export_nuclei_annotation_page():
        manifest_file = request.args.get('manifest_file', type=str)
        return render_template("export_table.html", manifest_name=manifest_file,
                               annotation_style="nuclei", column_addition=json.dumps({}))

    @app.route('/export_region_annotation')
    def export_region_annotation():
        manifest_file = request.args.get('manifest_file', type=str)
        region_size = request.args.get('region_size', type=str)

        thread_controller.BackgroundThread(annotation_project_controller.export_region_annotation_data,
                                           manifest_file, region_size).start()

        return redirect('/annotation_project_table')

    @app.route('/export_region_annotation_single', methods=("GET", "POST"))
    def export_region_annotation_single():
        if request.method == 'GET':
            manifest_file = request.args.get('manifest_file', type=str)
            slide_id = request.args.get('slide_id', type=str)
            region_size = request.args.get('region_size', type=str)
            manifest_txt = [item for item in open(manifest_file).readlines() if item[:len(slide_id)] == slide_id]
            print(slide_id)
            print(manifest_file)
            if len(manifest_txt) == 0:
                return "input ERROR!!"
            print(manifest_txt)
            export_file = annotation_project_controller \
                .export_region_annotation_data(manifest_file, region_size, manifest_txt)
            with open(export_file, 'rb') as f:
                data = f.readlines()
            os.remove(export_file)
            return Response(data, headers={
                'Content-Type': 'application/zip',
                'Content-Disposition': 'attachment; filename=%s;'
                                       % (manifest_file.rsplit("/", 1)[1][:-4] + '_nuclei_annotation.zip')
            })
        if request.method == 'POST':
            manifest_file = request.form.get("manifest_file")
            region_size = request.form.get("region_size")
            slide_id = request.form.getlist('slide_id[]')
            print(slide_id)
            print(manifest_file)
            manifest_txt = [item for item in open(manifest_file).readlines() if item[:len(slide_id[0])] in slide_id]
            if len(manifest_txt) == 0:
                return "input ERROR!!"
            print(manifest_txt)
            export_file = "static/export/" + time.ctime() + \
                          " " + manifest_file.rsplit("/", 1)[1][:-4] + " region " + str(region_size) + ".zip"
            thread_controller.BackgroundThread(annotation_project_controller.export_region_annotation_data,
                                               manifest_file, region_size, manifest_txt, export_file).start()
            return export_file

    @app.route('/export_region_annotation_data')
    def export_region_annotation_data():
        manifest_file = request.args.get('manifest_file', type=str)
        result = annotation_project_controller.export_region_annotation_list(manifest_file)
        return jsonify({'data': result, 'totals': len(result)})

    @app.route('/export_region_annotation_page')
    def export_region_annotation_page():
        manifest_file = request.args.get('manifest_file', type=str)
        return render_template("export_table.html", manifest_name=manifest_file,
                               annotation_style="region", column_addition=json.dumps({}))
