from Model import manifest
from Model import mission
from Controller import manifest_controller
from Controller import thread_controller


def import_manifest(manifest_path):
    manifest_db = manifest.Manifest()
    manifest_txt = open(manifest_path).readlines()
    for wsi in manifest_txt:
        info = wsi.split('\t')
        if info[0] == "id":
            continue
        try:
            manifest_db.insert(slide_uuid=info[0], svs_file=info[1])
        except Exception as e:
            print(e)
    thread_controller.BackgroundThread(manifest_controller.get_table, 0).start()


def export_manifest(manifest_path):
    manifest_db = manifest.Manifest()
    manifest_txt = open(manifest_path, 'w')
    manifest_txt.write("id\tfilename\tmd5\tsize\tstate\n")
    for wsi in manifest_db.get_projects():
        manifest_txt.write(wsi[1] + "\t" + wsi[2] + "\tunknown\tunknown\tunknown\n")


def export_database(database_file_folder):
    manifest_db = manifest.Manifest()
    manifest_csv = open(database_file_folder + '/manifest.txt', 'w')
    manifest_csv.write("id\tfilename\tmd5\tsize\tstate\n")
    for wsi in manifest_db.get_projects():
        for temp in wsi:
            manifest_csv.write(str(temp) + '\t')
        manifest_csv.write("\n")
    mission_db = mission.Mission()
    mission_csv = open(database_file_folder + '/predict_mask.txt', 'w')
    mission_csv.write("id\tfilename\tmd5\tsize\tstate\n")
    for wsi in mission_db.get_predict_masks():
        for temp in wsi:
            mission_csv.write(str(temp) + '\t')
        mission_csv.write("\n")


def clear_database():
    manifest_db = manifest.Manifest()
    manifest_db.delete_all_projects()
    mission_db = mission.Mission()
    mission_db.delete_all_predict()
