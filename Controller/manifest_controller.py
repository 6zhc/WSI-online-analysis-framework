from Model import manifest
from Controller import image_processing
import openslide
import os

data_root = 'static/data/'


def get_table(start_no=0, end_no=0):
    mani = manifest.Manifest()
    data = []
    wsis = mani.get_projects()
    if end_no <= 0:
        end_no = end_no + len(wsis)
    for wsi in wsis[start_no: end_no]:
        temp = []
        temp.append(wsi[0])  # ID
        temp.append('<button type="button" onclick="btn_click(\'remove_wsi\',' +
                    str(wsi[0]) + ')">remove</button>')
        temp.append(wsi[1])  # UUID

        svs_file_path = data_root + wsi[1] + '/' + wsi[2]
        try:  # image_size
            dimensions = openslide.OpenSlide(svs_file_path).dimensions
        except:
            if os.path.exists(svs_file_path):
                temp.append('<a "target="_blank">' + wsi[2] + '</a>')
                temp.append('Not SVS file')
                temp.append('Unsupported file')
                data.append(temp)
            else:
                temp.append('<a "target="_blank">' + wsi[2] + '</a>')
                temp.append('No SVS file')
                data.append(temp)
            continue

        temp.append('<a href="/slide?slide_id=' + str(wsi[0]) + '"target="_blank">' + wsi[2] + '</a>')

        icon_file_path = data_root + wsi[1] + '/' + 'icon.png'
        if not os.path.exists(icon_file_path):
            try:
                image_processing.generate_icon_image_from_svs_file(svs_file_path, icon_file_path)
            except:
                pass
        temp.append('<img src="' + icon_file_path + '"/>')

        temp.append(str(dimensions[0]).rjust(6, '_') + ' * ' + str(dimensions[1]).rjust(6, '_'))

        if wsi[4] is None or not os.path.exists(data_root + wsi[1] + '/' + wsi[4]):
            temp.append('<button type="button" onclick="btn_click(\'make_bg_mask\',' +
                        str(wsi[0]) + ')"> Make BG Mask</button>')
        else:
            temp.append('<a href="/slide?slide_id=' + str(wsi[0]) +
                        '&mask_url=' + wsi[4] + '"target="_blank">' + 'Background Mask ' + '</a>'
                        # + '<button type="button" onclick="btn_click(\'make_bg_mask\','
                        # + str(wsi[0]) + ')"> Remake</button>'
                        )
        temp.append("model_selection")
        temp.append('<a href="/mission_table?slide_uuid=' + str(wsi[1]) + '"target="_blank">' + 'Mission' + '</a>')

        data.append(temp)
    return data


def add_wsi(uuid, svs_file_name):
    mani = manifest.Manifest()
    mani.insert(slide_uuid=uuid, svs_file=svs_file_name)


def get_info_by_id(slide_id):
    mani = manifest.Manifest()
    return mani.get_project_by_id(slide_id)


def remove_wsi_by_id(slide_id):
    mani = manifest.Manifest()
    mani.delete_project_by_id(slide_id)


def get_total_number():
    mani = manifest.Manifest()
    return len(mani.get_projects())


def get_available_slide_id():
    mani = manifest.Manifest()
    data = []
    for wsi in mani.get_projects():
        temp = {"id": wsi[0], "text": wsi[0]}
        try:  # image_size
            svs_file_path = data_root + wsi[1] + '/' + wsi[2]
            openslide.OpenSlide(svs_file_path)
        except:
            continue
        data.append(temp)
    return data
