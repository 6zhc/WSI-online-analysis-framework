import mysql.connector
import configparser
import os


class PredictMask:
    def __init__(self):
        config_file = os.getcwd() + '/config.ini'
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        db = self.db_connect()
        db.close()

    def db_connect(self):
        return mysql.connector.connect(
            host=self.config['db']['host'],
            user=self.config['db']['user'],
            passwd=self.config['db']['passwd'],
            database=self.config['db']['database']
        )

    def insert(self, slide_uuid, slide_id, job_type=None, finished=0, total=None, predict_mask=None):
        db = self.db_connect()
        cursor = db.cursor()
        sql = "INSERT INTO PREDICT_MASK( UUID, SlideID, Job_type, Finished, Total, Predict_mask)" \
              " VALUES (%s, %s, %s, %s, %s, %s)"
        val = (slide_uuid, slide_id, job_type, finished, total, predict_mask)
        cursor.execute(sql, val)
        temp = cursor.lastrowid
        cursor.close()
        db.commit()
        db.close()
        return temp

    def get_predict_masks(self):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM PREDICT_MASK ORDER BY ID DESC")
        result = cursor.fetchall()
        db.close()
        return result

    def get_predict_masks_by_id(self, job_id):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM PREDICT_MASK WHERE (ID = %s)", (job_id,))
        result = cursor.fetchall()[0]
        cursor.close()
        db.close()
        return result

    def get_predict_masks_by_uuid(self, slide_uuid):
        db = self.db_connect()
        cursor = db.cursor()
        print((slide_uuid,))
        cursor.execute("SELECT * FROM PREDICT_MASK WHERE (UUID = %s)", (slide_uuid,))
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    def get_predict_masks_by_uuid_and_job_type(self, slide_uuid, job_type):
        db = self.db_connect()
        cursor = db.cursor()
        print((slide_uuid,))
        cursor.execute("SELECT * FROM PREDICT_MASK WHERE (UUID = %s and Job_type = %s)", (slide_uuid, job_type))
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    def update_finished_by_id(self, job_id, finished):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("UPDATE PREDICT_MASK SET Finished= %s WHERE (ID = %s)", (finished, job_id))
        cursor.close()
        db.commit()
        db.close()

    def update_total_by_id(self, job_id, total):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("UPDATE PREDICT_MASK SET Total= %s WHERE (ID = %s)", (total, job_id))
        cursor.close()
        db.commit()
        db.close()

    def update_predict_mask_by_id(self, job_id, predict_mask):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("UPDATE PREDICT_MASK SET Predict_mask = %s WHERE (ID = %s)", (predict_mask, job_id))
        cursor.close()
        db.commit()
        db.close()

    def delete_predict_mask_by_id(self, job_id):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("DELETE FROM PREDICT_MASK WHERE (ID = %s)", (job_id,))
        cursor.close()
        db.commit()
        db.close()

    def delete_all_predict(self):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("TRUNCATE TABLE PREDICT_MASK")
        cursor.close()
        db.commit()
        db.close()

