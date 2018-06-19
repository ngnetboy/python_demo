#coding=utf-8

import csv, logging


class CSV():

    @staticmethod
    def _write(path, rows, header=None):
        try:
            with open(path, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=header)

                writer.writeheader()
                writer.writerows(rows)
        except Exception as e:
            logging.error(str(e))
            return -1
    @staticmethod
    def _read(path):
        try:
            with open(path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                '''
                for item in reader:
                    print(item["name"], item["age"])
                '''
                return reader
        except Exception as e:
            logging.error(str(e))
            return None

    @staticmethod
    def _append(path, rows, header=None):
        try:
            
            with open(path, 'a') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=header)

                writer.writerows(rows)
        except Exception as e:
            logging.error(str(e))
            return -1

if __name__ == "__main__":
    header = ["name", "age"]
    data = [
        {"name":"netboy", "age":18},
        {"name":"goodboy", "age":20}
    ]
    
    #CSV._write("csv_test.csv", data, header)
    #CSV._read("csv_test.csv")
    CSV._append("csv_test.csv", data, header)


