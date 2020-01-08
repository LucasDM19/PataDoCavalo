import random

class MeioAmbiente():
   def __init__(self, qtd_agentes=1000):
      #print("No terceiro dia, surge!")
      self._agentes = [AgenteApostadorCavalo() for agente in range(qtd_agentes)]
      self._afogados = []   # Quem perder todo o patrimonio
      self._geracoes = 0   # Contabiliza as eras
      
   def recebeAtualizacao(self, odd, minuto, winLose):
      [agente.decide(odd, minuto, winLose) for agente in self._agentes]
      [self._afogados.append(agente) for agente in self._agentes if agente.estouVivo() == False]   # Quem se afogou sai
      self._agentes =  [agente for agente in self._agentes if agente.estouVivo() == True]    # Sobreviventes
      #melhor_patrimonio = max([agente.patrimonio for agente in self._agentes])
      melhor_retorno = max([agente.lucro_medio for agente in self._agentes])
      #melhorAgente = "<>".join( [str(agente) for agente in self._agentes if agente.patrimonio == melhor_patrimonio] )
      melhorAgente = "<>".join( [str(agente) for agente in self._agentes if agente.lucro_medio == melhor_retorno] )
      if( self._geracoes % 500 == 0 ):
         print("Geracao#", self._geracoes, " Vivos:", len(self._agentes), ", afogados=", len(self._afogados), ", Champs=", melhorAgente )
      self._geracoes += 1
      
   def notificaNovaCorrida(self):
      [agente.novaCorrida() for agente in self._agentes]
      
   def __str__ (self):
      return "#".join( [str(agente) for agente in self._agentes] )
      
class AgenteApostadorCavalo():
   def __init__(self):
      self.iniciaMindset()
      
   def iniciaMindset(self):
      self.odd_back_min = random.uniform(0.0, 9.9)
      self.odd_back_max = random.uniform(0.0, 9.9)
      self.minutos_lay = random.randrange(-9, 999)
      self.minutos_back = random.randrange(-9, 999)
      self.patrimonio = 1000.0   # Mil doletas
      self.somaStack = 0.0 # Capital de giro
      self.lucro_medio = 0.0 # Retorno do investimento
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
      if( odd >= self.odd_back_min and odd <= self.odd_back_max and minuto <= self.minutos_back ):   # Bora apostar back
         if( self.jaAposteiBack == True ): return False   # Sem aposta
         stack_lay = 20.0
         self.stack_back = round(stack_lay/(odd-1),2)
         if( winLose == 0 ): pl = (-1*self.stack_back)
         else: pl = self.stack_back/(odd-1)
         self.somaStack += self.stack_back
         self.patrimonio += pl
         self.jaAposteiBack == True
         self.idade += 1   # Envelhece
         return True
      if( minuto <= self.minutos_lay ):   # Bora apostar lay
         if( self.jaAposteiLay == True ): return False   # Sem aposta
         stack_lay = 20.0
         #stack_back = round(stack_lay/(odd-1),2)
         if( winLose == 0 ): pl = stack_lay/(odd-1)
         else: pl = (-1*stack_lay)
         self.somaStack += stack_lay
         self.patrimonio += pl
         self.jaAposteiLay == True
         self.idade += 1   # Envelhece
         return True
      # Atualizando os valores - rendimento!
      if( self.somaStack != 0 ): self.lucro_medio = 1.0*(self.patrimonio-1000.0)/self.somaStack
      return False
      
   def __str__ (self):
      return "Odd Back min=" + str(self.odd_back_min) + ", Odd Back max=" + str(self.odd_back_max) + ", Min. Back=" + str(self.minutos_back) + ", Min. Lay=" + str(self.minutos_lay) + ", Retorno=" + str(self.lucro_medio) + ", idade=" + str(self.idade)

if( __name__ == '__main__' ):
   print("Rodo pela linha de comando!")
   mundo = MeioAmbiente(qtd_agentes=5)
   [mundo.recebeAtualizacao(odd=2.1, minuto=10, winLose=1) for geracoes in range(50)]
   print(mundo)