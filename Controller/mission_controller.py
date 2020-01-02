from Model import predictMask
from Model import manifest


def get_table():
    predict_mask_db = predictMask.PredictMask()
    manifest_db = manifest.Manifest()
    jobs = predict_mask_db.get_predict_masks()
    data = []
    for job in jobs:
        temp = []
        temp.append(job[0])  # ID
        slide_id = manifest_db.get_project_by_uuid(job[1])[0]
        temp.append(slide_id)
        temp.append('<button type="button" onclick="btn_click(\'remove_job\',' +
                    str(job[0]) + ')">remove</button>')
        temp.append('<a href="/slide?slide_id=' + str(slide_id) + '"target="_blank">' + job[1] + '</a>')
        temp.append(str(job[2]))
        temp.append(bar(str(job[3] / job[4] * 100)))
        temp.append(str(job[3]) + '/' + str(job[4]))
        if job[5] is None:
            temp.append("Not Finished")
        else:
            temp.append('<a href="/slide?slide_id=' + str(slide_id) +
                        '&mask_url=' + job[5] + '"target="_blank">' + job[5] + '</a>'
                        # + '<button type="button" onclick="btn_click(\'make_bg_mask\','
                        # + str(wsi[0]) + ')"> Remake</button>'
                        )
        temp.append(str(job[7]))
        temp.append(str(job[6]))
        data.append(temp)
    return data


def bar(now):
    return '<div class="progress progress-striped">' \
           '<div class="progress-bar" role="progressbar" style="width: ' + now + '%;">' \
                                                                                 '</div></div>'
