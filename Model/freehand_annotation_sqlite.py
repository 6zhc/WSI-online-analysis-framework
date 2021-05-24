import sqlite3
import os
import atexit


class SqliteConnector:
    def __init__(self, sqlite_path):
        self.sqlite_path = sqlite_path
        if not os.path.exists(sqlite_path):
            self.create()

    def create(self):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        cursor = db.cursor()
        cursor.execute(
            "create table Line (id integer primary key, X1 integer, Y1 integer, X2 integer, Y2 integer, " + \
            "Grade integer, Branch integer, TimeStamp timestamp default (datetime('now','localtime')))")
        cursor.close()
        db.close()

    def incert_line(self, X1: int, Y1: int, X2: int, Y2: int, Grade: int):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        if X1 == X2 and Y1 == Y2:
            db.close()
            return
        cursor = db.cursor()
        cursor.execute(
            "insert into Line(X1, Y1, X2, Y2, Grade, Branch) values (?,?,?,?,?," + str(self.get_max_branch() + 1) + ")",
            tuple([X1, Y1, X2, Y2, Grade]))
        cursor.close()
        db.commit()
        db.close()

    def incert_lines(self, data):
        branch_id = self.get_max_branch() + 1
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        print(self.sqlite_path)
        cursor = db.cursor()
        cursor.executemany(
            "insert into Line(X1, Y1, X2, Y2, Grade, Branch) values (?,?,?,?,?," + str(branch_id) + ")",
            data)

        cursor.close()
        db.commit()
        db.close()
        return branch_id

    # def delete_line(self, X :int, Y :int):
    #     cursor = self.db.cursor()
    #     cursor.execute("delete from Line where (X1 == ? and Y1 == ?) or (X2 == ? and Y2 == ?)",
    #                        tuple([X, Y, X, Y]))
    #     cursor.close()
    #     self.db.commit()

    def delete_points(self, X: int, Y: int):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        cursor = db.cursor()
        cursor.execute("delete from Line where (X1 >? and X1 <? and Y1 >? and Y1 < ?) or" + \
                       "(X2 >? and X2 <? and Y2 >? and Y2 < ?)",
                       tuple([X - 100, X + 100, Y - 100, Y + 100, X - 100, X + 100, Y - 100, Y + 100]))

        cursor.close()
        db.commit()
        db.close()

    def delete_lines(self, X: int, Y: int):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        cursor = db.cursor()
        cursor.execute("select * from Line where (X1 >? and X1 <? and Y1 >? and Y1 < ?) or" + \
                       "(X2 >? and X2 <? and Y2 >? and Y2 < ?)",
                       tuple([X - 100, X + 100, Y - 100, Y + 100, X - 100, X + 100, Y - 100, Y + 100]))
        result = cursor.fetchall()
        # print(result)
        for item in result:
            # print(item)
            cursor.execute("delete from Line where branch == ?",
                           tuple([item[6]]))

        cursor.close()
        db.commit()
        db.close()

    def find_lines(self, X: int, Y: int):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        cursor = db.cursor()
        cursor.execute("select * from Line where (X1 >? and X1 <? and Y1 >? and Y1 < ?) or" + \
                       "(X2 >? and X2 <? and Y2 >? and Y2 < ?)",
                       tuple([X - 20, X + 20, Y - 20, Y + 20, X - 20, X + 20, Y - 20, Y + 20]))
        result = cursor.fetchall()
        # print(result)
        branch_id = []
        for item in result:
            # print(item)
            if item[6] not in branch_id:
                branch_id.append(item[6])

        cursor.close()
        db.close()
        return branch_id

    def delete_all_lines(self):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        cursor = db.cursor()
        cursor.execute("delete from  Line")

        cursor.close()
        db.commit()
        db.close()

    def get_lines(self):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        cursor = db.cursor()
        cursor.execute("select * from Line")
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    def get_lines_in_area(self, X_MIN: int, Y_MIN: int, X_MAX: int, Y_MAX: int):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        cursor = db.cursor()
        cursor.execute("select *  from Line where (X1 >= ? and Y1 >= ? and X1 <= ? and Y1 <= ?) " +
                       "or (X2 >= ? and Y2 >= ? and X2 <= ? and Y2 <= ?)",
                       tuple([X_MIN, Y_MIN, X_MAX, Y_MAX, X_MIN, Y_MIN, X_MAX, Y_MAX]))
        result = cursor.fetchall()
        cursor.close()
        db.close()
        return result

    def get_max_branch(self):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        cursor = db.cursor()
        cursor.execute("select MAX(branch)  from Line")
        result = cursor.fetchall()[0][0]
        if result == None:
            result = 0
        cursor.close()
        db.close()
        return result

    def del_max_branch(self):
        db = sqlite3.connect(self.sqlite_path)
        atexit.register(db.close)
        cursor = db.cursor()
        cursor.execute("delete from Line where branch == ?",
                       tuple([self.get_max_branch()]))

        cursor.close()
        db.commit()
        db.close()
