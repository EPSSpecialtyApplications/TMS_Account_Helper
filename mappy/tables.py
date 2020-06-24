import pyodbc
from enum import Enum
from abc import ABC
from mappy.exceptions import DataValidationError
from mappy.sqltypes import *
import csv

class TransactionState(Enum):
	READY = 0
	STAGED = 1
	COMMITTED = 2


class Table(object):
	def __init__(self, driver, tablename):
		self.driver = driver
		self.tablename = tablename


class InsertTable(Table):
	def __init__(self, driver, tablename):
		super().__init__(driver, tablename)
		self.column_info = self.__qry_column_info()
		self.row_inserts = []
		self.state = TransactionState.READY
		self.insert_ids = []


	def __qry_column_info(self):
		qry_column_info = """
			  SELECT c.name,
			       c.max_length,
			       c.precision,
			       c.scale,
			       c.is_nullable,
			       t.name [data_type],
				   c.object_id,
				   c.column_id,
				   CASE WHEN ind.is_primary_key = 1 THEN 1 ELSE 0 END AS is_primary_key
			  FROM sys.columns c
			  JOIN sys.types   t
			    ON c.user_type_id = t.user_type_id
			  CROSS APPLY (SELECT MAX(CASE WHEN ind.is_primary_key = 1 THEN 1 ELSE 0 END) AS is_primary_key FROM sys.index_columns ic
						   LEFT JOIN sys.indexes ind on ind.object_id = ic.object_id AND ind.index_id = ic.index_id
						   WHERE c.object_id = ic.object_id AND c.column_id = ic.column_id) AS ind
			 WHERE c.object_id    = Object_id(?)
		"""
		self.description = self.driver.execute(qry_column_info, self.tablename, to_dict=True)
		column_info = {column['name']: column for column in self.description}
		return column_info

	def add(self, data_row=None, data_dict=None, warn=True, die_on_error=False, **kwargs):
		try:
			d_o = DataObject(self.description, tablename=self.tablename, **kwargs)
			self.row_inserts.append(d_o)
		except DataValidationError as e:
			print(e)
			if die_on_error:
				raise e
			if warn:
				print(e)

	def add_all_from_file(self, filename):
		pass

	def add_all(self, data=None, warn=True, die_on_error=False):
		if data is None:
			data = []
		
		for row in data:
			self.add(**row)


	def export_to_sql_file(self, file):
		with open(file, 'w') as sql_out:
			for row in self.row_inserts:
				insert = row.sql_insert.replace('?', '{}')
				print(insert.format(*row.values))
				sql_out.write(insert.format(*row.values) + '\n')

	def execute(self):

		if not self.row_inserts:
			print('No staged data!')
			return

		for data_object in self.row_inserts:
			insert_id = self.driver.write(data_object.sql_insert, *data_object.values)
			self.insert_ids.append(insert_id)
	
	def get_last_insert_id(self):
		if self.insert_ids:
			return int(self.insert_ids[-1])
		

	def print_info(self):
		headers = next(iter(self.column_info.items()))
		print_as_table(table_headers=self.description[0].keys(), data=self.description)


class DataObject(object):
	def __init__(self, definition, tablename=None, **data):
		self.tablename = tablename
		self._data = data
		self.definition = definition
		self.col_defs = {d['name']: d for d in self.definition}
		self.__validate(data)

	@property
	def data(self):
		return self._data

	@property
	def values(self):
		return [val for k, val in self.data.items() if self.col_defs.get(k) is not None]

	@property
	def keys(self):
		return [k for k, val in self.data.items() if self.col_defs.get(k) is not None]
	
	@property	
	def required_attributes(self):
		return [attr['name'] for attr in self.definition if not attr['is_nullable'] and not attr['is_primary_key']]

	@property
	def sql_insert(self):
		sql = 'INSERT INTO {} ('.format(self.tablename)
		sql += ('{}, ' * (len(self.keys) - 1) + '{})\n').format(*self.keys)
		sql += 'VALUES ('
		sql += ('?, ' * (len(self.keys) - 1) + '?)')
		return sql
	

	def __check_field_lengths(self, data):
		#print('checkin fields')
		#print_dict_as_table(self.col_defs)
		try:
			for col, val in self.data.items():
				typename = self.col_defs[col]['data_type']
		except KeyError:
			print('Key Error on:', col)
	def __check_required_fields(self, data):
		"""Raises an error if a non-nullable field is None or not present
		   in the object's data
		"""
		for field in self.required_attributes:
			try:
				if data[field] is None:
					raise DataValidationError("Attribute '{}' is required and is None".format(field))
			except KeyError:
				raise DataValidationError("Attribute '{}' is required and is not present".format(field))

	def __validate(self, data):
		self.__check_required_fields(data)
		self.__check_field_lengths(data)

	def __set_attributes(self, data):
		for k, v in data.items():
			setattr(self, k, v)

	

def print_dict_as_table(d, PADDING=2, FORMAT_CHAR='-'):
	headers = d.keys()
	data = d.values()
	print_as_table(table_headers=headers, data=data)

def print_as_table(table_headers=[], data=[], PADDING=2, FORMAT_CHAR='-'):
	column_lens = __get_max_col_widths(table_headers, data)
	TABLE_LEN = (sum((column_lens[header] + PADDING + 1) 
				for header in table_headers))

	row_format = "|{:^{width}}"
	# print line
	print(FORMAT_CHAR * (TABLE_LEN + 1))

	# Print column headers
	for header in table_headers:
		width = column_lens[header] + PADDING
		print(row_format.format(header, width=width), end='')
	print('|')
	print(FORMAT_CHAR * (TABLE_LEN + 1))

	# Print data
	for row in data:
		for tup, column_len in zip(row.values(), column_lens.values()):	
			width = column_len + PADDING
			print(row_format.format(tup, width=width), end='')
		print("|")
	
def __get_max_col_widths(table_headers, data):
	column_lens = {}
	for header in table_headers:
		max_data_len = max([len(str(item[header])) for item in data])
		column_lens[header] = max(max_data_len, len(header))

	for k, v in column_lens.items():
		print(k, v)

	return column_lens

