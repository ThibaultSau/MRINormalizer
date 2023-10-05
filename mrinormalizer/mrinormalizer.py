import pandas

class MRIParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.load(self.file_path)

    def load(self, file_path):
        pass