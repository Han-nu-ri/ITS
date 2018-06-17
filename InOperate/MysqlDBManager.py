import pymysql

class MySqlDBManager:
	def __init__(self):
		# self.connection = pymysql.connect(host = 'localhost', user = 'root', password = 'root', db = 'coin_info')
		# self.cursor = self.connection.cursor()
		print("DB init")

	def select(self, query):
		self.connection = pymysql.connect(host = 'localhost', user = 'root', password = 'root', db = 'coin_info')
		self.cursor = self.connection.cursor()
		self.cursor.execute(query)
		rows = self.cursor.fetchall()

		self.cursor.close()
		self.connection.close()

		return rows
	
	def insert(self, query):
		self.connection = pymysql.connect(host = 'localhost', user = 'root', password = 'root', db = 'coin_info')
		self.cursor = self.connection.cursor()
		self.cursor.execute(query)
		self.connection.commit()

		self.cursor.close()
		self.connection.close()
