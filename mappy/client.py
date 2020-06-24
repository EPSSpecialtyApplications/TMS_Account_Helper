import pyodbc
from mappy.tables import InsertTable


class Driver(object):

	def __init__(self, cnxn_str):
		self.cnxn_str = cnxn_str
		self.cnxn = pyodbc.connect(cnxn_str, autocommit=True)


	def _results_to_dict(self, data, cursor):
		cols = [col[0] for col in cursor.description]
		if type(data) is pyodbc.Row: return dict(zip(cols, data))
		data_dict = []
		for row in data:
			data_dict.append(dict(zip(cols, row)))
		return data_dict

	def execute(self, sql, *args, to_dict=False, fetchone=False):
		cursor = self.cnxn.cursor()

		if fetchone:
			data = cursor.execute(sql, *args).fetchone()
		else:
			data = cursor.execute(sql, *args).fetchall()

		if to_dict:
			return self._results_to_dict(data, cursor)
		return data

	def write(self, sql, *args):
		cursor = self.cnxn.cursor()
		cursor.execute(sql, *args)
		last_id = cursor.execute('SELECT @@IDENTITY').fetchone()
		return last_id[0]

class Client(object):

	def __init__(self, cnxn_str):

		if not cnxn_str:
			raise ValueError("Connection string must not be blank or None")

		self.driver = Driver(cnxn_str)
		self.__set_db_name()


	def __set_db_name(self):
		self.db_name = self.driver.execute("SELECT DB_NAME();");

	def query(self, sql, *args, fetchone=False):
		return self.driver.execute(sql, *args, to_dict=True, fetchone=fetchone)

	def execute_sql(self, sql, *args):
		return self.driver.write(sql, *args)


	def get_table(self, tablename, mode='insert'):
		"""returns an insert table"""

		# Address case where table doesnt exist
		return InsertTable(self.driver, tablename)







