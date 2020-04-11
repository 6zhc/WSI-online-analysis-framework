from flask import render_template, redirect, request
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

    @app.route('/export_nuclei_annotation')
    def export_nuclei_annotation():
        manifest_file = request.args.get('manifest_file', type=str)

        thread_controller.BackgroundThread(annotation_project_controller.export_nuclei_annotation_data,
                                           manifest_file).start()

        return redirect('/annotation_project_table')
