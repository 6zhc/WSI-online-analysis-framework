import sqlite3
import os


class SqliteConnector:
    def __init__(self, sqlite_path):
        if not os.path.exists(sqlite_path):
            self.db = sqlite3.connect(sqlite_path)
            self.create()
        else:
            self.db = sqlite3.connect(sqlite_path)

    def create(self):
        cursor = self.db.cursor()
        cursor.execute(
            "create table RegionCentre (id integer primary key,regionID integer UNIQUE,centreX integer, centreY integer)")
        cursor.execute(
            "create table NucleusGrade (id integer primary key,nucleusID integer UNIQUE,nucleusGrade integer)")
        cursor.close()

    def incert_RegionCentre(self, regionID: int, centreX: int, centreY: int):
        cursor = self.db.cursor()
        if regionID < 0:
            RegionID_exist = self.get_RegionID()
            if len(RegionID_exist) is 0:
                regionID = 1;
            else:
                regionID = max(RegionID_exist) + 1
        if len(self.get_RegionCentre_By_RegionID(regionID)):
            cursor.execute("update RegionCentre set centreX=?, centreY =? where regionID == ?",
                           tuple([centreX, centreY, regionID]))
        else:
            cursor.execute("insert into RegionCentre(regionID, centreX, centreY) values (?,?,?)",
                           tuple([regionID, centreX, centreY]))
        cursor.close()
        self.db.commit()

    def delete_RegionCentre(self, regionID: int):
        cursor = self.db.cursor()
        cursor.execute("delete from RegionCentre where regionID == ?",
                       tuple([regionID]))
        cursor.close()
        self.db.commit()

    def get_RegionID(self):
        cursor = self.db.cursor()
        cursor.execute("select regionID from RegionCentre")
        result = cursor.fetchall()
        cursor.close()
        RegionID = []
        for i in result:
            RegionID.append(i[0])
        return RegionID

    def get_RegionID_Centre(self):
        cursor = self.db.cursor()
        cursor.execute("select regionID, centreX, centreY from RegionCentre")
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_RegionCentre_By_RegionID(self, regionID: int):
        cursor = self.db.cursor()
        cursor.execute("select centreX,centreY from RegionCentre where regionID == ?", tuple([regionID]))
        result = cursor.fetchall()
        cursor.close()
        return result

    def incert_NucleusGrade(self, nucleusID: int, nucleusGrade: int):
        cursor = self.db.cursor()
        if not self.is_Exist_NucleusGrade(nucleusID):
            cursor.execute("insert into NucleusGrade(nucleusID, nucleusGrade) values (?,?)",
                           tuple([nucleusID, nucleusGrade]))
        else:
            cursor.execute("update NucleusGrade set nucleusGrade =? where nucleusID == ?",
                           tuple([nucleusGrade, nucleusID]))
        cursor.close()
        self.db.commit()

    def get_NucleusGrade(self, nucleusID: int):
        cursor = self.db.cursor()
        cursor.execute("select nucleusGrade from NucleusGrade where nucleusID == ?",
                       tuple([nucleusID]))
        result = cursor.fetchall()
        cursor.close()
        if len(result):
            return result[0][0]
        else:
            return 0

    def is_Exist_NucleusGrade(self, nucleusID: int):
        cursor = self.db.cursor()
        cursor.execute("select nucleusGrade from NucleusGrade where nucleusID == ?",
                       tuple([nucleusID]))
        result = cursor.fetchall()
        cursor.close()
        return len(result)

    def get_all_NucleusGrade(self):
        cursor = self.db.cursor()
        cursor.execute("select * from NucleusGrade")
        result = cursor.fetchall()
        cursor.close()
        return result
