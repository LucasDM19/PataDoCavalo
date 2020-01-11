import random, string

class MeioAmbiente():
   def __init__(self, qtd_agentes=1000):
      #print("No terceiro dia, surge!")
      self._agentes = [AgenteApostadorCavalo() for agente in range(qtd_agentes)]
      self._afogados = []   # Quem perder todo o patrimonio
      self._geracoes = 0   # Contabiliza as eras
      self._corridas = 0   # Contabiliza as corridas
      
   def recebeAtualizacao(self, odd, minuto, winLose):
      [agente.decide(odd, minuto, winLose) for agente in self._agentes]
      [self._afogados.append(agente) for agente in self._agentes if agente.estouVivo() == False]   # Quem se afogou sai
      self._agentes =  [agente for agente in self._agentes if agente.estouVivo() == True]    # Sobreviventes
      #melhor_patrimonio = max([agente.patrimonio for agente in self._agentes])
      melhor_retorno = max([agente.lucro_medio for agente in self._agentes])
      #melhorAgente = "<>".join( [str(agente) for agente in self._agentes if agente.patrimonio == melhor_patrimonio] )
      melhorAgente = "<>".join( [str(agente) for agente in self._agentes if agente.lucro_medio == melhor_retorno] )
      #if( self._geracoes % 500 == 0 ): print("Geracao#", self._geracoes, " Vivos:", len(self._agentes), ", afogados=", len(self._afogados), ", Champs=", melhorAgente )
      self._geracoes += 1
      
   def notificaNovaCorrida(self):
      [agente.novaCorrida() for agente in self._agentes]
      melhor_retorno = max([agente.lucro_medio for agente in self._agentes])
      melhorAgente = "<>".join( [str(agente) for agente in self._agentes if agente.lucro_medio == melhor_retorno] )
      print("Corrida#", self._corridas, " Vivos:", len(self._agentes), ", afogados=", len(self._afogados), ", Champs=", melhorAgente )
      self._corridas += 1
      
   def __str__ (self):
      return "#".join( [str(agente) for agente in self._agentes] )
      
class AgenteApostadorCavalo():
   def __init__(self):
      self.iniciaMindset()
      
   def iniciaMindset(self):
      self.nome = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))   # Uma cadeia de letras e numeros de tamanho 10
      self.odd_back_min = random.uniform(2.0, 9.9)
      self.odd_back_max = random.uniform(0.0, 9.9)
      self.minutos_lay = random.randrange(0, 120)
      self.minutos_back = random.randrange(-9, 999)
      self.patrimonio = 1000.0   # Mil doletas
      self.somaStack = 0.0 # Capital de giro
      self.lucro_medio = 0.0 # Retorno do investimento
      self.idade = 0 # Um bebezito
      self.jaAposteiBack = False
      self.jaAposteiLay = False
   
   def defineAtributos(self, nome, odd_back_min, odd_back_max, minutos_lay, minutos_back  ):
      self.nome = nome
      self.odd_back_min = odd_back_min
      self.odd_back_max = odd_back_max
      self.minutos_lay = minutos_lay
      self.minutos_back = minutos_back
      
   def estouVivo(self):
      if( self.patrimonio <= 0 ): return False
      return True
      
   def novaCorrida(self):
      self.jaAposteiBack = False
      self.jaAposteiLay = False
   
   def decide(self, odd, minuto, winLose):
      comissao = 0.065
      if( (odd >= self.odd_back_min) and (odd <= self.odd_back_max) and (minuto <= self.minutos_back) and (self.jaAposteiBack == False) ) :   # Bora apostar back
         stack_lay = 20.0
         self.stack_back = round(stack_lay/(odd-1),2)
         if( winLose == 0 ): pl = (-1*stack_lay)
         else: pl = self.stack_back*(odd)- self.stack_back
         if( pl > 0 ): pl = pl*(1-comissao)
         #print(self.nome, "Aposta back com odd=",odd, ", minuto=", minuto, ", W/L=",winLose, ", retorno=", pl, ", StackBack=", self.stack_back)
         self.somaStack += self.stack_back
         self.patrimonio += pl
         self.jaAposteiBack = True
         self.idade += 1   # Envelhece
         return True
      if( (minuto <= self.minutos_lay) and (self.jaAposteiLay == False) ):   # Bora apostar lay
         stack_lay = 20.0
         #stack_back = round(stack_lay/(odd-1),2)
         if( winLose == 0 ): pl = +1*stack_lay
         else: pl = (-1*(stack_lay/(odd-1)))
         if( pl > 0 ): pl = pl*(1-comissao)
         print(self.nome, "Aposta lay com odd=", odd, ", minuto=", minuto, ", W/L=",winLose, ", retorno=", pl, ", stack=", stack_lay)
         self.somaStack += stack_lay
         self.patrimonio += pl
         self.jaAposteiLay = True
         self.idade += 1   # Envelhece
         return True
      # Atualizando os valores - rendimento!
      if( self.somaStack != 0 ): self.lucro_medio = 1.0*(self.patrimonio-1000.0)/self.somaStack
      return False
      
   def __str__ (self):
      return "Nome="+self.nome+", Odd Back min=" + str(round(self.odd_back_min,2)) + ", Odd Back max=" + str(round(self.odd_back_max,2)) + ", Min. Back=" + str(round(self.minutos_back,2)) + ", Min. Lay=" + str(self.minutos_lay) + ", Retorno=" + str(round(self.lucro_medio,3)) + ", idade=" + str(self.idade)

if( __name__ == '__main__' ):
   print("Rodo pela linha de comando!")
   mundo = MeioAmbiente(qtd_agentes=5)
   [mundo.recebeAtualizacao(odd=2.1, minuto=10, winLose=1) for geracoes in range(50)]
   print(mundo)