import mysql.connector
import configparser
import os
import uuid


class Manifest:
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

    def insert(self, slide_uuid=None, svs_file=None, smaller_image=None, background_mask=None):
        db = self.db_connect()
        cursor = db.cursor()
        if slide_uuid is None:
            slide_uuid = str(uuid.uuid4())
        sql = "INSERT INTO MANIFEST( UUID, SVS_file, Smaller_image, Background_mask) VALUES (%s, %s, %s, %s)"
        val = (slide_uuid, svs_file, smaller_image, background_mask)
        cursor.execute(sql, val)
        cursor.close()
        db.commit()
        db.close()

    def get_projects(self):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM MANIFEST")
        result = cursor.fetchall()
        db.close()
        return result

    def get_project_by_id(self, slide_id):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM MANIFEST WHERE (ID = %s)", (slide_id,))
        result = cursor.fetchall()[0]
        cursor.close()
        db.close()
        return result

    def get_project_by_uuid(self, slide_uuid):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM MANIFEST WHERE (UUID = %s)", (slide_uuid,))
        result = cursor.fetchall()[0]
        cursor.close()
        db.close()
        return result

    def get_project_by_svs_file(self, svs_file):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM MANIFEST WHERE (SVS_file = %s)", (svs_file,))
        result = cursor.fetchall()[0]
        cursor.close()
        db.close()
        return result

    def get_project_by_similar_svs_file(self, svs_file):
        db = self.db_connect()
        cursor = db.cursor()
        svs_file = '%' + svs_file + '%'
        cursor.execute("SELECT * FROM MANIFEST WHERE (SVS_file like %s)", (svs_file,))
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    def update_svs_file_by_id(self, slide_id, svs_file):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("UPDATE MANIFEST SET SVS_file= %s WHERE (ID = %s)", (svs_file, slide_id))
        cursor.close()
        db.commit()
        db.close()

    def update_smaller_image_by_id(self, slide_id, smaller_image):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("UPDATE MANIFEST SET Smaller_image = %s WHERE (ID = %s)", (smaller_image, slide_id))
        cursor.close()
        db.commit()
        db.close()

    def update_background_mask_by_id(self, slide_id, background_mask):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("UPDATE MANIFEST SET Background_mask = %s WHERE (ID = %s)", (background_mask, slide_id))
        cursor.close()
        db.commit()
        db.close()

    def delete_project_by_id(self, slide_id):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("DELETE FROM MANIFEST WHERE (ID = %s)", (slide_id,))
        cursor.close()
        db.commit()
        db.close()

    def delete_all_projects(self):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("TRUNCATE TABLE MANIFEST")
        cursor.close()
        db.commit()
        db.close()

    def continue_id(self):
        db = self.db_connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM MANIFEST")
        result = cursor.fetchall()

        slide_id = 0

        for wsi in result:
            slide_id = slide_id + 1
            if wsi[0] != slide_id:
                cursor.execute("UPDATE MANIFEST SET ID = %s WHERE (ID = %s)", (slide_id, wsi[0]))

        cursor.close()
        db.commit()
        db.close()
