import threading


class BackgroundThread(threading.Thread):
    def __init__(self, function, slide_id):
        threading.Thread.__init__(self)
        self.function = function
        self.slide_id = slide_id

    def run(self):
        self.function(self.slide_id)
