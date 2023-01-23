import csv

class Logger:   
    def __init__(self):
        self.file = open('log.csv', 'w')
        self.writer = csv.writer(self.file)

    def write(self, linha):
        self.writer.writerow(linha)
    
    def close(self):
        self.file.close()