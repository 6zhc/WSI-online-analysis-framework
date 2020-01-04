from Model import mission
import os


def get_table(slide_uuid):
    mission_db = mission.Mission()
    if slide_uuid == "":
        jobs = mission_db.get_predict_masks()
    else:
        jobs = mission_db.get_predict_masks_by_uuid(slide_uuid)
    data = []
    for job in jobs:
        temp = []
        temp.append(job[0])  # ID
        # slide_id = manifest_db.get_project_by_uuid(job[2])[0]
        temp.append(str(job[1]))
        temp.append('<button type="button" onclick="btn_click(\'remove_mission\',' +
                    str(job[0]) + ')">remove</button>')
        temp.append('<a href="/slide?slide_id=' + str(job[1]) + '"target="_blank">' + str(job[2]) + '</a>')
        temp.append(str(job[3]))
        temp.append(bar(str(job[4] / job[5] * 100)))
        temp.append(str(job[4]) + '/' + str(job[5]))
        if job[6] is None:
            temp.append("Not Finished")
        else:
            temp.append('<a href="/slide?slide_id=' + str(job[1]) +
                        '&mask_url=' + job[6] + '"target="_blank">' + job[6] + '</a>'
                        # + '<button type="button" onclick="btn_click(\'make_bg_mask\','
                        # + str(wsi[0]) + ')"> Remake</button>'
                        )
        temp.append(str(job[8]))
        temp.append(str(job[7]))
        data.append(temp)
    return data


def bar(now):
    return '<div class="progress progress-striped">' \
           '<div class="progress-bar" role="progressbar" style="width: ' + now + '%;">' \
                                                                                 '</div></div>'


def remove_mission_by_id(job_id):
    mission_db = mission.Mission()
    mission_db.delete_predict_mask_by_id(job_id)


def get_total_number():
    mission_db = mission.Mission()
    return len(mission_db.get_predict_masks())


def get_available_model():
    result = []
    list = os.listdir("Model/")
    for file in list:
        if file[-4:] == ".pth":
            temp = {"id": file, "text": file}
            result.append(temp)
    return result
