import random

class MeioAmbiente():
   def __init__(self, qtd_agentes=10, geracoes=10000):
      #print("No terceiro dia, surge!")
      self._agentes = [AgenteApostadorCavalo() for agente in range(qtd_agentes)]
      
   def recebeAtualizacao(self, odd, minuto, winLose):
      [agente.decide(odd, minuto, winLose) for agente in self._agentes]
      
   def __str__ (self):
      return "#".join( [str(agente) for agente in self._agentes] )
      
class AgenteApostadorCavalo():
   def __init__(self):
      #print("Surge o pacato cidadao")
      self.iniciaMindset()
      
   def iniciaMindset(self):
      self.odd_min = random.uniform(0.0, 9.9)
      self.odd_max = random.uniform(0.0, 9.9)
      self.minutos_min = random.randrange(-9, 999)
      self.minutos_max = random.randrange(-9, 999)
      self.patrimonio = 1000.0   # Mil doletas
      self.idade = 0 # Um bebezito
      self.jaAposteiBack = False
      self.jaAposteiLay = False
      
   def estouVivo(self):
      if( self.patrimonio <= 0 ): return False
      return True
      
   def novaCorrida(self):
      self.jaAposteiBack = False
      self.jaAposteiLay = False
   
   def decide(self, odd, minuto, winLose):
      if( odd >= self.odd_min and minuto >= self.minutos_min ):   # Bora apostar back
         if( self.jaAposteiBack == True ): return False   # Sem aposta
         stack_lay = 20.0
         self.stack_back = round(stack_lay/(odd-1),2)
         if( winLose == 0 ): pl = (-1*self.stack_back)
         else: pl = self.stack_back/(odd-1)
         self.patrimonio += pl
         self.jaAposteiBack == True
         return True
      if( odd <= self.odd_max and minuto <= self.minutos_max ):
         if( self.jaAposteiLay == True ): return False   # Sem aposta
         stack_lay = 20.0
         #stack_back = round(stack_lay/(odd-1),2)
         if( winLose == 0 ): pl = stack_lay/(odd-1)
         else: pl = (-1*stack_lay)
         self.patrimonio += pl
         self.jaAposteiLay == True
         return True
      return False
      
   def __str__ (self):
      return "Odd min=" + str(self.odd_min) + ", Odd max=" + str(self.odd_max) + ", Min. min=" + str(self.minutos_min) + ", Min. max=" + str(self.minutos_max) + ", Patrimonio=" + str(self.patrimonio)

if( __name__ == '__main__' ):
   print("Rodo pela linha de comando!")
   mundo = MeioAmbiente(qtd_agentes=5)
   mundo.recebeAtualizacao(odd=2.1, minuto=10, winLose=0)
   print(mundo)