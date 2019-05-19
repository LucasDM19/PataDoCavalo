"""
   Uma classe de testes gerais
"""

from unittest import TestCase
import unittest
from Hush import *

class BasicTest(TestCase):
   def setUp(self):
      self.API_URL = ''
      
   def test_IsAPIURLUP(self):
      import urllib.request
      try:
         retorno = urllib.request.urlopen("https://api.betfair.com/exchange/betting/rest/v1.0/").getcode()
         self.assertEqual( retorno.code, 200 )
      except urllib.error.HTTPError:
         print("ruim")
         
if __name__ == "__main__":
   unittest.main

# Consigo pelo menos fazer um login?
