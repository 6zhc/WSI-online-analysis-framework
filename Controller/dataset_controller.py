from Model import manifest
from Model import predictMask
from Controller import manifest_controller
from Controller import thread


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
    thread.BackgroundThread(manifest_controller.get_table, 0).start()



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
    predict_mask_db = predictMask.PredictMask()
    predict_mask_csv = open(database_file_folder + '/predict_mask.txt', 'w')
    predict_mask_csv.write("id\tfilename\tmd5\tsize\tstate\n")
    for wsi in predict_mask_db.get_predict_masks():
        for temp in wsi:
            predict_mask_csv.write(str(temp) + '\t')
        predict_mask_csv.write("\n")


def clear_database():
    manifest_db = manifest.Manifest()
    manifest_db.delete_all_projects()
    predict_mask_db = predictMask.PredictMask()
    predict_mask_db.delete_all_predict()
