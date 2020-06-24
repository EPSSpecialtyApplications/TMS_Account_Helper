import pytest

from mappy.tables import *


class TestDataObject:

	@pytest.fixture(scope='module', autouse=True)
	def table_def(self):
		table_def = [
			{'name': 'AddressID', 'max_length': 4, 'precision': 10, 'scale': 0, 'is_nullable': False, 'data_type': 'int'},
			{'name': 'AddressLine1', 'max_length': 120, 'precision': 0, 'scale': 0, 'is_nullable': False, 'data_type': 'nvarchar'},
			{'name': 'AddressLine2', 'max_length': 120, 'precision': 0, 'scale': 0, 'is_nullable': True, 'data_type': 'nvarchar'},
			{'name': 'City', 'max_length': 60, 'precision': 0, 'scale': 0, 'is_nullable': False, 'data_type': 'nvarchar'},
			{'name': 'StateProvinceID', 'max_length': 4, 'precision': 10, 'scale': 0, 'is_nullable': False, 'data_type': 'int'},
			{'name': 'PostalCode', 'max_length': 30, 'precision': 0, 'scale': 0, 'is_nullable': False, 'data_type': 'nvarchar'},
			{'name': 'SpatialLocation', 'max_length': -1, 'precision': 0, 'scale': 0, 'is_nullable': True, 'data_type': 'geography'},
			{'name': 'rowguid', 'max_length': 16, 'precision': 0, 'scale': 0, 'is_nullable': False, 'data_type': 'uniqueidentifier'},
			{'name': 'ModifiedDate', 'max_length': 8, 'precision': 23, 'scale': 3, 'is_nullable': False, 'data_type': 'datetime'}
		]
		return table_def

	@pytest.fixture(scope='module', autouse=True)
	def data(self):
		data = {
			'AddressID': '',
			'AddressLine1': '1971 Napa Ct.',
			'AddressLine2': '',
			'City': 'Pittsburgh',
			'StateProvinceID': '19',
			'PostalCode': '15123',
			'SpatialLocation': '0xE6100000010CE0B4E50458DA47402F12A5F80C975EC0',
			'rowguid': 'febf8191-9804-44c8-877a-33fde94f0075',
			'ModifiedDate': '2008-12-17 00:00:00.000'
		}
		return data

	@pytest.fixture(scope='module', autouse=True)
	def tablename(self):
		return 'Address'


	def test_required_fields(self, table_def, data, tablename):
		d_o = DataObject(table_def, **data)
		actual = [
			'AddressID', 
			'AddressLine1', 
			'City', 
			'StateProvinceID', 
			'PostalCode',
			'rowguid', 
			'ModifiedDate'
		]
		assert d_o.required_attributes == actual

	def test_sql_insert(self, table_def, data, tablename):
		d_o = DataObject(table_def, tablename=tablename, **data)
		sql_insert = d_o.sql_insert
		actual = ("INSERT INTO Address (AddressID, AddressLine1, AddressLine2, City, StateProvinceID, PostalCode, SpatialLocation, rowguid, ModifiedDate)\n"
				  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")


		assert sql_insert == actual
		




















