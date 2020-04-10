from flask import render_template, redirect
from flask import jsonify

from Controller import thread_controller
from Controller import annotation_project_controller


def add_annotation_project_sever(app):
    @app.route('/annotation_project_table')
    def annotation_project_table():
        return render_template('annotation_project_table.html')

    @app.route('/annotation_project_table_data')
    def annotation_project_table_data():
        return jsonify(
            annotation_project_controller.get_table())

    @app.route('/refresh_annotation_slide')
    def refresh_annotation_slide():
        thread_controller.BackgroundThread(annotation_project_controller.refresh_npy).start()
        return redirect('/annotation_project_table')
