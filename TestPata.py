"""
   Uma classe de testes gerais
"""

from unittest import TestCase
import unittest
#from Hush import *

# class BasicTest(TestCase):
   # def setUp(self):
      # self.API_URL = ''
      
   # def test_IsAPIURLUP(self):
      # import urllib.request
      # try:
         # retorno = urllib.request.urlopen("https://api.betfair.com/exchange/betting/rest/v1.0/").getcode()
         # self.assertEqual( retorno.code, 200 )
      # except urllib.error.HTTPError:
         # print("ruim")
   # def testLogon(self): #SyntaxError: import * only allowed at module level
      # from RestAPI import *
      # from Hush import *
      # u, s, a = usuarioAPI, senhaAPI, APIKey
      # api = BetfairAPI(usuario=u, senha=s, api_key=a)
      # print("Session Token=",api.sessionToken)

def cenario1():
   win_lose = 0
   odds60 = 2.72
   bsp = 2.01
   stake_lay = 20
   return win_lose, odds60, bsp, stake_lay
   
def cenario2():
   win_lose = 0
   odds60 = 2.12
   bsp = 2.66
   stake_lay = 20
   return win_lose, odds60, bsp, stake_lay
      
class RonaldoStakeTest(TestCase):
   def test_Ronaldo_stake1(self):
      win_lose, odds60, bsp, stake_lay = cenario1()
      stake_back = round(stake_lay/(odds60-1),2)
      self.assertEqual( stake_back, 11.63 )
   def test_Ronaldo_lucro_back1(self):
      win_lose, odds60, bsp, stake_lay = cenario1()
      stake_back = round(stake_lay/(odds60-1),2)   
      if( win_lose==1 ) : x = odds60 
      else: x = 0
      lucro_back = (x-1)*stake_back
      self.assertEqual( lucro_back, -11.63 )
   def test_Ronaldo_lucro_lay1(self):
      win_lose, odds60, bsp, stake_lay = cenario1()
      stake_back = round(stake_lay/(odds60-1),2)   
      if( win_lose==1 ) : x = 0
      else: x = 1/(1-1/(bsp))-1 
      lucro_lay = round(x*stake_lay,2)
      self.assertEqual( lucro_lay, 19.80 )
   def test_Ronaldo_lucro_back_lay1(self):
      win_lose, odds60, bsp, stake_lay = cenario1()
      stake_back = round(stake_lay/(odds60-1),2) 
      if( win_lose==1 ) : 
         b = odds60
         l = 0
      else:
         b = 0
         l = 1/(1-1/(bsp))-1
      lucro_back = (b-1)*stake_back
      lucro_lay = round(l*stake_lay,2)
      lucro_total = lucro_back + lucro_lay
      self.assertEqual( lucro_total, 8.17 )

class RonaldoStakeTest2():
   def test_Ronaldo_stake2(self):
      win_lose, odds60, bsp, stake_lay = cenario2()
      stake_back = round(stake_lay/(odds60-1),2)
      self.assertEqual( stake_back, 18.18 )
   def test_Ronaldo_lucro_back2(self):
      win_lose, odds60, bsp, stake_lay = cenario2()
      stake_back = round(stake_lay/(odds60-1),2)   
      if( win_lose==1 ) : x = odds60 
      else: x = 0
      lucro_back = (x-1)*stake_back
      self.assertEqual( lucro_back, -18.18 )
   def test_Ronaldo_lucro_lay2(self):
      win_lose, odds60, bsp, stake_lay = cenario2()
      stake_back = round(stake_lay/(odds60-1),2)   
      if( win_lose==1 ) : x = 0
      else: x = 1/(1-1/(bsp))-1 
      lucro_lay = round(x*stake_lay,2)
      self.assertEqual( lucro_lay, 12.06 )
   def test_Ronaldo_lucro_back_lay2(self):
      win_lose, odds60, bsp, stake_lay = cenario2()
      stake_back = round(stake_lay/(odds60-1),2) 
      if( win_lose==1 ) : 
         b = odds60
         l = 0
      else:
         b = 0
         l = 1/(1-1/(bsp))-1
      lucro_back = (b-1)*stake_back
      lucro_lay = round(l*stake_lay,2)
      lucro_total = lucro_back + lucro_lay
      self.assertEqual( lucro_total, -6.12 )

class LucasStakeTest2():
   def test_Lucas_stake2(self):
      win_lose, odds60, bsp, stake_lay = cenario2()
      stack_back = round(stake_lay/(odds60-1),2)
      self.assertEqual( stack_back, 18.18 )
   def test_Lucas_lucro_back2(self):
      win_lose, odds60, bsp, stake_lay = cenario2()
      stack_back = round(stake_lay/(odds60-1),2)
      if( win_lose == 0 ): b = (-1*stack_back)
      if( win_lose == 1 ): b = stack_back/(odds60-1)
      lucro_back = b
      self.assertEqual( lucro_back, -18.18 )
   def test_Lucas_lucro_lay2(self):
      win_lose, odds60, bsp, stake_lay = cenario2()
      stake_back = round(stake_lay/(odds60-1),2)
      if( win_lose == 0 ): l = stake_lay/(bsp-1)
      if( win_lose == 1 ): l = (-1*stake_lay)
      lucro_lay = round(l,2)
      self.assertEqual( lucro_lay, 12.06 )
   def test_Lucas_lucro_back_lay2(self):
      win_lose, odds60, bsp, stake_lay = cenario2()
      stake_back = round(stake_lay/(odds60-1),2)
      if( win_lose == 0 ): pl = (-1*stake_back) + stake_lay/(bsp-1)
      if( win_lose == 1 ): pl = stake_back/(odds60-1) + (-1*stake_lay)
      lucro_total = round(pl,2)
      self.assertEqual( lucro_total, -6.12 )
      
class LucasStakeTest1(TestCase):
   def test_Lucas_stake1(self):
      win_lose, odds60, bsp, stake_lay = cenario1()
      stack_back = round(stake_lay/(odds60-1),2)
      self.assertEqual( stack_back, 11.63 )
   def test_Lucas_lucro_back1(self):
      win_lose, odds60, bsp, stake_lay = cenario1()
      stack_back = round(stake_lay/(odds60-1),2)
      if( win_lose == 0 ): b = (-1*stack_back)
      if( win_lose == 1 ): b = stack_back/(odds60-1)
      lucro_back = b
      self.assertEqual( lucro_back, -11.63 )
   def test_Lucas_lucro_lay1(self):
      win_lose, odds60, bsp, stake_lay = cenario1()
      stake_back = round(stake_lay/(odds60-1),2)
      if( win_lose == 0 ): l = stake_lay/(bsp-1)
      if( win_lose == 1 ): l = (-1*stake_lay)
      lucro_lay = round(l,2)
      self.assertEqual( lucro_lay, 19.80 )
   def test_Lucas_lucro_back_lay1(self):
      win_lose, odds60, bsp, stake_lay = cenario1()
      stake_back = round(stake_lay/(odds60-1),2)
      if( win_lose == 0 ): pl = (-1*stake_back) + stake_lay/(bsp-1)
      if( win_lose == 1 ): pl = stake_back/(odds60-1) + (-1*stake_lay)
      lucro_total = round(pl,2)
      self.assertEqual( lucro_total, 8.17 )
      
if __name__ == "__main__":
   unittest.main()

# Consigo pelo menos fazer um login?
