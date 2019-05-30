from Mysql_Driver import MysqlQuery
HOST = "localhost"
DATABASE = "MQTT_DATA"
USERNAME_DB = "root"
PASSWORD_DB = "raspberry"

mysqlQuery = MysqlQuery(HOST, DATABASE, USERNAME_DB, PASSWORD_DB)
mysqlQuery.connectDatabase()
for i in range(2,9):
	mysqlQuery.createTable("device_" + str(i))
