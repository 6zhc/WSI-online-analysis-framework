import os

analysis_data_root = "Data/analysis_data/"

analysis_csv = "5slide_tcga_re"
for folder in os.listdir(analysis_data_root):
    analysis_data_folder = analysis_data_root + folder + '/'
    for item in os.listdir(analysis_data_folder):
        # print(item[:len(analysis_csv)])
        if item[:len(analysis_csv)] == analysis_csv:
            os.remove(analysis_data_folder + item)
