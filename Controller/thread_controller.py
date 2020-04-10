import threading


class BackgroundThread(threading.Thread):
    def __init__(self, function, slide_id=-1, job_type=-1):
        threading.Thread.__init__(self)
        self.function = function
        self.slide_id = slide_id
        self.job_type = job_type

    def run(self):
        if self.slide_id == -1 and self.job_type == -1:
            self.function()
        elif self.slide_id == -1:
            self.function(self.job_type)
        elif self.job_type == -1:
            self.function(self.slide_id)
        else:
            self.function(self.slide_id, self.job_type)
