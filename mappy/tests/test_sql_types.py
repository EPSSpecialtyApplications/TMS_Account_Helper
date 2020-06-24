import pytest

from mappy.sqltypes import *


class TestTypeValidation:

    def test_integer_string_parse(self):
    	val = '165'
    	int_type = Int32(val)
    	assert int_type.value == 165

    def test_integer(self):
    	val = 190
    	int_type = Int32(val)
    	assert int_type.value == val

    def test_integer_max_val(self):
    	val = 2147483647
    	int_type = Int32(val)
    	assert int_type.value == val

    def test_integer_overflow(self):
    	val = 2147483648
    	with pytest.raises(TypeError):
    		int_type = Int32(val)