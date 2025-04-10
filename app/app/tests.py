"""
Sample Tests
"""

from django.test import SimpleTestCase

from app import calc

class CalcTests(SimpleTestCase):
    """Test calc module"""
    
    def test_add_numbers(self):
        """Testing adding numbers together."""
        res = calc.add(5, 4)
        self.assertEqual(res,9)
    
    def test_substract_numbers(self):
        """Testing substracting numbers"""
        res = calc.substract(10,15)
        self.assertEqual(res,5)