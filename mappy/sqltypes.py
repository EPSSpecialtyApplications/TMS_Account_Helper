from abc import ABC

class SQLTypeFactory(object):
	pass


class DataType(object):
	"""Base class for all data types"""
	def __init__(self, value):
		self._value = value

	@property
	def value(self):
		return self._value

	def __parse_value(self):
		"""Implicity parses value from string if necessary"""
		pass

	def __validate_type(self):
		pass

	def __repr__(self):
		return self.__class__.__name__



class Int32(DataType):

	def __init__(self, value):
		super().__init__(value)
		self.__parse_value()
		self.__validate_type()

	
	def __parse_value(self):
		if type(self._value) is str:
			self._value = int(self.value)
		elif type(self._value) is int:
			pass
		else:
			raise TypeError('Int32 type was initialized with an illegal value: {}'.format(self.value))
	
	def __validate_type(self):
		if self._value.bit_length() >= 32:
			raise TypeError('Value exceeded the maximum value for a 32 bit int')


class NVarChar(DataType):
	def __init__(self, value, size):
		super().__init__(value)
		self._size = size
		self.__validate_type()

	@property
	def size(self):
		return self._size

	def __validate_type(self):
		if len(self.value) > self.size:
			raise TypeError('String length exceeded the set value of {}'.format(self.size))




_sql_type_map = {
	'int': Int32,
	'nvarchar': NVarChar,
	'uniqueidentifier': DataType,
	'geography': DataType,
	'datetime': DataType
}

	












