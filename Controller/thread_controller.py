import threading


class BackgroundThread(threading.Thread):
    def __init__(self, function, var1=-1, var2=-1, var3=-1):
        threading.Thread.__init__(self)
        self.function = function
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3

    def run(self):
        if self.var1 == -1:
            self.function()
        elif self.var2 == -1:
            self.function(self.var1)
        elif self.var3 == -1:
            self.function(self.var1, self.var2)
        else:
            self.function(self.var1, self.var2, self.var3)
