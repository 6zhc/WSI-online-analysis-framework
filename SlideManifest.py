class SlideManifest:
    def __init__(self, root_path):
        manifest_path = root_path
        wsis = open(manifest_path).readlines()
        self.manifest = [wsi.split('\t') for wsi in wsis]

    def get_id(self, line):
        return self.manifest[line][0]

    def get_filename(self, line):
        return self.manifest[line][1]

    def get_md5(self, line):
        return self.manifest[line][2]

    def get_size(self, line):
        return self.manifest[line][3]

    def get_state(self, line):
        return self.manifest[line][4]

    def get_total_size(self):
        return len(self.manifest)
