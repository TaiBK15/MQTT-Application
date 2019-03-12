import mysql.connector
from mysql.connector import Error


class MysqlQuery:

    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connect = None
        self.cursor = None

    def connectDatabase(self):
        try:
            self.connect = mysql.connector.connect(host=self.host,
                                        database=self.database,
                                        user=self.user,
                                        password=self.password)
            if self.connect.is_connected():
                self.cursor = self.connect.cursor()     
                print("Connected to MySQL database")
        except mysql.connector.Error as error:
            print("Failed to connect to database!")
            print(error)

            
    def queryCmd(self, sql_query):
        try:
            self.cursor.execute(sql_query)
            self.connect.commit()
            print("Query OK!")
        except mysql.connector.Error as error:
            print("Query failed!")
            print(error)

    def createTable(self, device_tab):
        try:
            sql_create_table = "CREATE TABLE " + device_tab + "(ID INT NOT NULL AUTO_INCREMENT,\
                                                            TIME TIMESTAMP NOT NULL,\
                                                            DATA VARCHAR(255) NOT NULL,\
                                                            PRIMARY KEY (ID));"
            self.cursor.execute(sql_create_table)
            print("create table " + device_tab +" successfully!")
        except mysql.connector.Error as error:
            print("Failed to create table!")
            print(error)


    def deleteTable(self, device_tab):
        try:
            sql_drop_tab_query = "DROP TABLE " + device_tab + ";"
            self.cursor.execute(sql_drop_tab_query)
            print("Delete table " + device_tab + " successfully!")
        except mysql.connector.Error as error:
            print("Failed to delete table!")
            print(error)


    def insertTable(self,device_tab, data):
        try:
            sql_insert_query = "INSERT INTO "+ device_tab + "(DATA) VALUES('" + data + "')"
            self.cursor.execute(sql_insert_query)
            self.connect.commit()
            print("Insert into database successfully!")
        except mysql.connector.Error as error:
            print("Failed to insert ino table!")
            print(error)

    def readAllTable(self, device_tab):
        try:
            sql_read_all_query = "SELECT * FROM "+ device_tab + ";"
            self.cursor.execute(sql_read_all_query)
            records = self.cursor.fetchall()
            for row in records:
                print(row)
        except mysql.connector.Error as error:
            print("Failed to read data!")
            print(error)

    def readRecentTable(self, device_tab, size_row):
        try:
            sql_read_recent_query = "SELECT * FROM "+ device_tab + " ORDER BY TIME DESC;"
            self.cursor.execute(sql_read_recent_query)
            records = self.cursor.fetchmany(size_row)
            for row in records:
                print(row)
        except mysql.connector.Error as error:
            print("Failed to read data!")
            print(error)

    def deleteDataTable(self, device_tab):
        try:
            sql_delete_query = "TRUNCATE " + device_tab + ";"
            self.cursor.execute(sql_delete_query)
            self.connect.commit()
            print("Delete database successfully!")
        except mysql.connector.Error as error:
            print("Failed to delete data!")
            print(error)

    def finishConnect(self):
        if(self.connect.is_connected()):
              self.cursor.close()
              self.connect.close()
              print("MySQL connection is closed\n")
