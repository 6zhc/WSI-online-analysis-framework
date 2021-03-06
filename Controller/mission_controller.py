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
        # print('static/data/analysis_data/' + str(job[2]) + '/mission' + str(job[0]) + '_result.png')
        if os.path.exists('static/data/analysis_data/' + str(job[2]) + '/mission' + str(job[0]) + '_result.png'):
            temp.append('<a href="/static/data/analysis_data/' + str(job[2]) + '/mission' + str(
                job[0]) + '_result.png"target="_blank">' + str(job[1]) + '</a>')
        else:
            temp.append(str(job[1]))
        temp.append('<button type="button" onclick="btn_click(\'remove_mission\',' +
                    str(job[0]) + ')">remove</button>')
        temp.append('<a href="/slide?slide_id=' + str(job[1]) + '"target="_blank">' + str(job[2]) + '</a>')
        temp.append(str(job[3]))
        temp.append(bar(str(job[4] / job[5] * 100)))
        temp.append(str(job[4]) + '/' + str(job[5]))
        if job[6] is None:
            temp.append("Not Finished")
        elif "mission" in job[6]:
            temp.append('<a href="/slide?slide_id=' + str(job[1]) +
                        '&mask_url=' + job[6] + '"target="_blank">' + job[6] + '</a>'
                        )
        else:
            temp.append('<a href="/slide?slide_id=' + str(job[1]) +
                        '&mask_url=' + 'mission' + str(job[0]) + '_' + str(job[3]) + '.png' +
                        '"target="_blank">' + job[6] + '</a>'
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
    file_list = os.listdir("models/")
    for file in file_list:
        if file[-4:] == ".pth":
            temp = {"id": file, "text": file}
            result.append(temp)
        if file[-8:] == ".pth.tar":
            temp = {"id": file, "text": file}
            result.append(temp)
    return result
