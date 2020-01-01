import mysql.connector
import configparser

config_file = 'config.ini'
config = configparser.ConfigParser()
config.read(config_file, encoding='utf-8')

try:
    db = mysql.connector.connect(
        host=config['db']['host'],
        user=config['db']['user'],
        passwd=config['db']['passwd'],
        database=config['db']['database']
    )
except:
    db = mysql.connector.connect(
        host=config['db']['host'],
        user=config['db']['user'],
        passwd=config['db']['passwd']
    )
    mycursor = db.cursor()
    mycursor.execute("CREATE DATABASE test")
    db.close()
    db = mysql.connector.connect(
        host=config['db']['host'],
        user=config['db']['user'],
        passwd=config['db']['passwd'],
        database=config['db']['database']
    )

cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS MANIFEST")
sql = """CREATE TABLE MANIFEST (
         ID INT PRIMARY KEY NOT NULL auto_increment,
         UUID  CHAR(36) NOT NULL UNIQUE,
         SVS_file  VARCHAR(255) DEFAULT NULL,
         Smaller_image VARCHAR(255) DEFAULT NULL,
         Background_mask VARCHAR(255) DEFAULT NULL)"""
cursor.execute(sql)

cursor.execute("DROP TABLE IF EXISTS PREDICT_MASK")
sql = """CREATE TABLE PREDICT_MASK (
         ID INT PRIMARY KEY NOT NULL auto_increment,
         UUID CHAR(36) NOT NULL,
         Job_type VARCHAR(255) DEFAULT 'undefined',
         Finished INT DEFAULT 0,
         Total INT DEFAULT 1,
         Predict_mask VARCHAR(255) DEFAULT NULL,
         Creat_time  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)"""
cursor.execute(sql)

# 关闭数据库连接
db.close()
