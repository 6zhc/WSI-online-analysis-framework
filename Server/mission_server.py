from flask import render_template, request
from flask import jsonify
from flask_login import login_required

from Controller import mission_controller


def add_mission_server(app):
    @app.route('/mission_table')
    @login_required
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

    @app.route('/mission_table_data')
    @login_required
    def mission_table_data():
        page_no = request.args.get('page_no', default=1, type=int)
        item_per_page = request.args.get('item_per_page', default=15, type=int)
        slide_uuid = request.args.get('slide_uuid', default="", type=str)
        return jsonify(
            mission_controller.get_table(slide_uuid)[page_no * item_per_page - item_per_page:page_no * item_per_page])

    @app.route('/remove_mission')
    @login_required
    def remove_mission():
        job_id = request.args.get('slide_id', type=int)
        mission_controller.remove_mission_by_id(job_id)
        return jsonify({"info": "Removed Successfully !", "time": "-1"})
