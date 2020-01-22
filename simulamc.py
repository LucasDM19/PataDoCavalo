import random, string

class MeioAmbiente():
   def __init__(self, tipoAgente, qtd_agentes=1000):
      #print("No terceiro dia, surge!")
      self._agentes = [tipoAgente() for agente in range(qtd_agentes)]
      self._afogados = []   # Quem perder todo o patrimonio
      self._geracoes = 0   # Contabiliza as eras
      self._corridas = 0   # Contabiliza as corridas
      
   def recebeAtualizacao(self, odd, minuto, winLose, race_id=0):
      [agente.decide(odd, minuto, winLose, race_id) for agente in self._agentes]
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
   
   def exibeAgentes(self):
      print("Agentes Vivos:")
      lista_agentes = [agente for agente in self._agentes if agente.estouVivo() == True]
      while( len(lista_agentes) != 0 ):
         melhor_retorno = max([agente.lucro_medio for agente in lista_agentes])
         melhorAgente = "<>".join( [str(agente) for agente in lista_agentes if agente.lucro_medio == melhor_retorno] )
         if( len([str(agente) for agente in lista_agentes if agente.lucro_medio == melhor_retorno]) != 1 ):
            for a in [str(agente) for agente in lista_agentes if agente.lucro_medio == melhor_retorno]:
               print(a)
         else:
            print(melhorAgente)
         lista_agentes = [agente for agente in lista_agentes if agente.lucro_medio != melhor_retorno]
      print("Agentes Afogados:")
      lista_agentes = [agente for agente in self._afogados if agente.estouVivo() == False]
      while( len(lista_agentes) != 0 ):
         melhor_retorno = max([agente.lucro_medio for agente in lista_agentes])
         melhorAgente = "<>".join( [str(agente) for agente in lista_agentes if agente.lucro_medio == melhor_retorno] )
         if( len([str(agente) for agente in lista_agentes if agente.lucro_medio == melhor_retorno]) != 1 ):
            for a in [str(agente) for agente in lista_agentes if agente.lucro_medio == melhor_retorno]:
               print(a)
         else:
            print(melhorAgente)
         lista_agentes = [agente for agente in lista_agentes if agente.lucro_medio != melhor_retorno]
         
   def __str__ (self):
      desc = "Era "+ str(self._geracoes)
      lista_agentes = [agente for agente in self._agentes if agente.estouVivo() == True]
      while( len(lista_agentes) != 0 ):
         melhor_retorno = max([agente.lucro_medio for agente in lista_agentes])
         melhorAgente = "<>".join( [str(agente) for agente in lista_agentes if agente.lucro_medio == melhor_retorno] )
         desc += melhorAgente + "#"
         lista_agentes = [agente for agente in lista_agentes if agente.lucro_medio != melhor_retorno]
      return desc

# Classe mais abstrata. Tudo o que envolve envolver apostas com stack e retornos
class AgenteApostador():
   def __init__(self):
      self.iniciaMindset()
      
   def iniciaMindset(self):
      self.nome = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))   # Uma cadeia de letras e numeros de tamanho 10
      self.patrimonio = 1000.0   # Mil doletas
      self.somaStack = 0.0 # Capital de giro
      self.lucro_medio = 0.0 # Retorno do investimento
      self.idade = 0 # Um bebezito
      
   def estouVivo(self):
      if( self.patrimonio <= 0 ): return False
      return True

# Agente para apostas que envolvem tendencias de odds. Nao apenas para o favorito.
class AgenteEspeculadorCavalo(AgenteApostador):
   pass
      
# Agente para apostas simples com base em faixas de odds e pontos temporais de back e de lay. Nao deu certo.
class AgenteApostadorCavalo(AgenteApostador):      
   def iniciaMindset(self):
      super().iniciaMindset() # Inicio o basico do apostador
      self.odd_back_min = random.uniform(2.0, 9.9)
      self.odd_back_max = random.uniform(0.0, 9.9)
      self.odd_lay_min = random.uniform(2.0, 9.9)
      self.odd_lay_max = random.uniform(0.0, 9.9)
      self.minutos_lay = random.randrange(0, 120)
      self.minutos_back = random.randrange(-9, 999)
      self.jaAposteiBack = False
      self.jaAposteiLay = False
   
   def defineAtributos(self, nome, odd_back_min=0.0, odd_back_max=999.9, odd_lay_min=0.0, odd_lay_max=999.9, minutos_lay=0, minutos_back=0  ):
      self.nome = nome
      self.odd_back_min = odd_back_min
      self.odd_back_max = odd_back_max
      self.odd_lay_min = odd_lay_min
      self.odd_lay_max = odd_lay_max
      self.minutos_lay = minutos_lay
      self.minutos_back = minutos_back
      
   def novaCorrida(self):
      self.jaAposteiBack = False
      self.jaAposteiLay = False
   
   def decide(self, odd, minuto, winLose, race_id):
      comissao = 0.065
      #print("Dado: Odd=", odd, ", minuto=", minuto, ", W/L=", winLose)
      if( (odd > self.odd_back_min) and (odd <= self.odd_back_max) and (minuto == self.minutos_back) and (self.jaAposteiBack == False) ) :   # Bora apostar back
         stack_lay = 20.0
         #self.stack_back = round(stack_lay/(odd-1),2)
         self.stack_back = stack_lay # Stack fixo
         if( winLose == 0 ): pl = (-1*self.stack_back)
         else: pl = self.stack_back*(odd)-self.stack_back
         if( pl > 0 ): pl = pl*(1-comissao)
         #print(self.nome, "Aposta back com odd=",odd, ", minuto=", minuto, ", W/L=",winLose, ", retorno=", pl, ", StackBack=", self.stack_back, ", corre=", race_id)
         self.somaStack += self.stack_back
         self.patrimonio += pl
         self.jaAposteiBack = True
         self.idade += 1   # Envelhece
         return True
      if( (odd > self.odd_lay_min) and (odd <= self.odd_lay_max) and (minuto <= self.minutos_lay) and (self.jaAposteiLay == False) ):   # Bora apostar lay
         stack_lay = 20.0
         #stack_back = round(stack_lay/(odd-1),2)
         if( winLose == 0 ): pl = +1*stack_lay
         else: pl = (-1*(stack_lay*(odd-1)))
         if( pl > 0 ): pl = pl*(1-comissao)
         #print(self.nome, "Aposta lay com odd=", odd, ", minuto=", minuto, ", W/L=",winLose, ", retorno=", round(pl,2), ", stack=", stack_lay)
         self.somaStack += stack_lay
         self.patrimonio += pl
         self.jaAposteiLay = True
         self.idade += 1   # Envelhece
         return True
      # Atualizando os valores - rendimento!
      if( self.somaStack != 0 ): self.lucro_medio = 1.0*(self.patrimonio-1000.0)/self.somaStack
      return False
      
   def __str__ (self):
      return "Nome="+self.nome+", OddBack min=" + str(round(self.odd_back_min,2)) + ", OddBack max=" + str(round(self.odd_back_max,2)) + ", Min. Back=" + str(round(self.minutos_back,2)) + ", OddLay min=" + str(round(self.odd_lay_min,2)) + ", OddLay max=" + str(round(self.odd_lay_max,2)) + ", Min. Lay=" + str(self.minutos_lay) + ", Retorno=" + str(round(self.lucro_medio,3)) + ", idade=" + str(self.idade)

if( __name__ == '__main__' ):
   print("Rodo pela linha de comando!")
   mundo = MeioAmbiente(qtd_agentes=5)
   [mundo.recebeAtualizacao(odd=2.1, minuto=10, winLose=1) for geracoes in range(50)]
   print(mundo)