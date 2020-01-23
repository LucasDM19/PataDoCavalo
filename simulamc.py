import random, string
from math import log10 as log
import operator
import copy

class MeioAmbiente():
   def __init__(self, tipoAgente, qtd_agentes=1000):
      #print("No terceiro dia, surge!")
      self._agentes = [tipoAgente() for agente in range(qtd_agentes)]
      self._afogados = []   # Quem perder todo o patrimonio
      self._geracoes = 0   # Contabiliza as eras
      self._corridas = 0   # Contabiliza as corridas
      
   def recebeAtualizacao(self, odd, minuto, winLose, bsp={}, race_id=0):
      [agente.decide(odd, minuto, winLose, bsp, race_id) for agente in self._agentes]
      [self._afogados.append(agente) for agente in self._agentes if agente.estouVivo() == False]   # Quem se afogou sai
      self._agentes =  [agente for agente in self._agentes if agente.estouVivo() == True]    # Sobreviventes
      #melhor_patrimonio = max([agente.patrimonio for agente in self._agentes])
      melhor_retorno = max([agente.lucro_medio for agente in self._agentes])
      #melhorAgente = "<>".join( [str(agente) for agente in self._agentes if agente.patrimonio == melhor_patrimonio] )
      melhorAgente = "<>".join( [str(agente) for agente in self._agentes if agente.lucro_medio == melhor_retorno] )
      #if( self._geracoes % 500 == 0 ): print("Geracao#", self._geracoes, " Vivos:", len(self._agentes), ", afogados=", len(self._afogados), ", Champs=", melhorAgente )
      self._geracoes += 1
      
   def notificaNovaCorrida(self, race_id=0):
      [agente.novaCorrida() for agente in self._agentes]
      melhor_retorno = max([agente.lucro_medio for agente in self._agentes])
      melhorAgente = "<>".join( [str(agente) for agente in self._agentes if agente.lucro_medio == melhor_retorno] )
      print("Corrida#", self._corridas, ",ID=",race_id, " Vivos:", len(self._agentes), ", afogados=", len(self._afogados), ", Champs=", melhorAgente )
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
   def iniciaMindset(self):
      super().iniciaMindset() # Inicio o basico do apostador
      self.minutosX1 = 120 
      self.minutosX2 = 105 
      self.minutosX3 = 90 
      self.minutosX4 = 75 
      self.minutosX5 = 60 
      self.minutosX6 = 45 
      self.minutosX7 = 30
      self.minutosX8 = 15 
      self.min_cai = -0.45 # Caindo mais do que isso, faz aposta
      self.min_sobe = 0.85 # Subindo mais do que isso, faz aposta
      
   def novaCorrida(self):
      self.jaApostei = False
      self.valores_odds_X1 = {} # Cada odd no momento X1
      self.valores_odds_X2 = {}
      self.valores_odds_X3 = {}
      self.valores_odds_X4 = {}
      self.valores_odds_X5 = {}
      self.valores_odds_X6 = {}
      self.valores_odds_X7 = {}
      self.valores_odds_X8 = {}
      self.todos_trend = ["X2","X3","X4","X5","X6","X7","X8",]
      self.trend = { x : {} for x in self.todos_trend } # Calcula tendencia
      
   def calculaTrend(self, valores_odds_a, valores_odds_b, lista_corrida, cp=False):
      #print(valores_odds_a, valores_odds_b)
      trend = {}
      for lco in lista_corrida:
         if(lco not in valores_odds_a or lco not in valores_odds_b): trend[lco] = 0.0 # Sem comparacao, sem variacao
         else: 
            trend[lco] = log( valores_odds_a[lco]/valores_odds_b[lco] )
            if(cp==True): print("lco=", lco, "a=", valores_odds_a[lco], "b=",valores_odds_b[lco], "Trend=", round(trend[lco],4) )
      return trend
   
   # Back e lay simples
   def fazApostaBackLay(self, odd_back, stack_back, wl_back, odd_lay, stack_lay, wl_lay, comissao = 0.065 ):
      pl_back = fazApostaBack(self, odd_back, stack_back, wl_back)
      pl_lay = fazApostaLay(self, odd_lay, stack_lay, wl_lay)
      pl = pl_back + pl_lay
      print("Pl back=", pl_back, " e PL lay=", pl_lay)
      return pl
      
   # Faz apenas Back
   def fazApostaBack(self, odd_back, stack_back, wl_back, comissao = 0.065):
      if( wl_back == 0 ): 
         pl_back = (-1*stack_back) 
      else: 
         pl_back = stack_back*(odd_back)-stack_back
      if( pl_back > 0 ): 
         pl_back = pl_back*(1-comissao)
      self.somaStack += stack_back
      print("Aposta back ", stack_back ," na odd ", odd_back , " teve PL=", round(pl_back,2) )
      return pl_back
      
   # Faz apenas Lay
   def fazApostaLay(self, odd_lay, stack_lay, wl_lay, comissao = 0.065):
      if( wl_lay == 0 ): 
         pl_lay = (+1*stack_lay)
      else: 
         pl_lay = (-1*(stack_lay*(odd_lay-1)))
      if( pl_lay > 0 ): 
         pl_lay = pl_lay*(1-comissao)
      self.somaStack += stack_lay
      return pl_lay
      
   def decide(self, lista_corridas, minuto, winLose, lista_bsp, race_id=0 ):
      comissao = 0.065
      #print("Dado: Odd=", lista_corridas, ", minuto=", minuto, ", W/L=", winLose, ", race=", race_id)
      lista_corridas_ordenado = dict( sorted( lista_corridas.items(), key=operator.itemgetter(1),reverse=False ) ) # Mostra igual no site. Odds menores primeiro.
      if( minuto == self.minutosX1 ): 
         #print("Hora do X1")
         self.valores_odds_X1 = copy.deepcopy(lista_corridas_ordenado)
      if( minuto == self.minutosX2 ): 
         #print("Hora do X2")
         self.valores_odds_X2 = copy.deepcopy(lista_corridas_ordenado)
         self.trend["X2"] = self.calculaTrend(valores_odds_a=self.valores_odds_X2, valores_odds_b=self.valores_odds_X1, lista_corrida=lista_corridas_ordenado, cp=False)
      if( minuto == self.minutosX3 ): 
         #print("Hora do X3")
         self.valores_odds_X3 = copy.deepcopy(lista_corridas_ordenado)
         self.trend["X3"] = self.calculaTrend(valores_odds_a=self.valores_odds_X3, valores_odds_b=self.valores_odds_X2, lista_corrida=lista_corridas_ordenado, cp=False)
      if( minuto == self.minutosX4 ): 
         #print("Hora do X4")
         self.valores_odds_X4 = copy.deepcopy(lista_corridas_ordenado)
         self.trend["X4"] = self.calculaTrend(valores_odds_a=self.valores_odds_X4, valores_odds_b=self.valores_odds_X3, lista_corrida=lista_corridas_ordenado, cp=False)
      if( minuto == self.minutosX5 ): 
         #print("Hora do X5")
         self.valores_odds_X5 = copy.deepcopy(lista_corridas_ordenado)
         self.trend["X5"] = self.calculaTrend(valores_odds_a=self.valores_odds_X5, valores_odds_b=self.valores_odds_X4, lista_corrida=lista_corridas_ordenado, cp=False)
      if( minuto == self.minutosX6 ): 
         #print("Hora do X6")
         self.valores_odds_X6 = copy.deepcopy(lista_corridas_ordenado)
         self.trend["X6"] = self.calculaTrend(valores_odds_a=self.valores_odds_X6, valores_odds_b=self.valores_odds_X5, lista_corrida=lista_corridas_ordenado, cp=False)
      if( minuto == self.minutosX7 ): 
         #print("Hora do X7")
         self.valores_odds_X7 = copy.deepcopy(lista_corridas_ordenado)
         self.trend["X7"] = self.calculaTrend(valores_odds_a=self.valores_odds_X7, valores_odds_b=self.valores_odds_X6, lista_corrida=lista_corridas_ordenado, cp=False)
      if( minuto == self.minutosX8 ): 
         #print("Hora do X8")
         self.valores_odds_X8 = copy.deepcopy(lista_corridas_ordenado)
         self.trend["X8"] = self.calculaTrend(valores_odds_a=self.valores_odds_X8, valores_odds_b=self.valores_odds_X7, lista_corrida=lista_corridas_ordenado, cp=False)
         #print("Vals=", self.trend["X2"], self.trend["X3"], self.trend["X4"], self.trend["X5"], self.trend["X6"], self.trend["X7"], self.trend["X8"])
         media_trend = {}
         for vlox in self.valores_odds_X1: media_trend[vlox] = sum( [self.trend[x][vlox] for x in self.todos_trend  ] ) / (len(self.todos_trend)) # Tiro media de cada trend
         #for m in media_trend: print("Media Trend de ", m,"=", round(media_trend[m],4) ) # Exibo cada media
         #print([self.trend[x][vlox] for x in self.todos_trend for vlox in self.valores_odds_X1  ])
         if( len([media_trend[n] for n in media_trend]) == 0 ): return False # Sem aposta
         nome_maior_trend = [m for m in media_trend if media_trend[m] == max([media_trend[n] for n in media_trend]) ][0]
         nome_menor_trend = [m for m in media_trend if media_trend[m] == min([media_trend[n] for n in media_trend]) ][0]
         #print("Maior=", nome_maior_trend, " e menor=", nome_menor_trend )
         
         self.estrategia = "BackMaior" # Testando
         if( self.jaApostei == False ):
            if( self.estrategia == "BackMaior" ):
               stack_back = 20.0
               odd_back = lista_corridas_ordenado[nome_maior_trend]
               wl_back = winLose[nome_maior_trend]
               pl_back = self.fazApostaBack(odd_back, stack_back, wl_back)
               self.patrimonio += pl_back
               self.idade += 1   # Envelhece
               self.jaApostei = True
               
         #x = 18/0 
      if( minuto == 123456 ):
         if( len(self.valores_odds_X1) == 0 ): return False # Nao tem como fazer a estrategia sem dados anteriores
         maior_var = 0.0
         nome_maior_var = ""
         menor_var = 0.0
         nome_menor_var = ""
         self.valores_odds_X2 = lista_corridas_ordenado
         for lco in lista_corridas_ordenado:
            #print("lco=", lista_corridas_ordenado, " e X1=", self.valores_odds_X1, ", race=", race_id)
            if( lco in self.valores_odds_X1 ): # Se tem cavalo novo, nao importa para o var
               var = 1.0*(lista_corridas_ordenado[lco] - self.valores_odds_X1[lco] ) / (self.valores_odds_X1[lco])
               if( var > maior_var ):
                  maior_var = var
                  nome_maior_var = lco
               if( menor_var > var ):
                  menor_var = var
                  nome_menor_var = lco
            #print("Nome=", lco, ",o=", lista_corridas_ordenado[lco], ", W/L=", winLose[lco], ", estava=", self.valores_odds_X1[lco], ", V=", round(var,3)  )
         if( self.jaApostei == False and self.min_cai >= menor_var ): # Para variacao negativa
         #if( self.jaApostei == False and self.min_sobe <= maior_var ): # Para variacao positiva
         #if( self.jaApostei == False and self.min_sobe <= maior_var and self.min_cai >= menor_var ): # Para variacao positiva e negativa
            #print("Race=", race_id, "Maior var=", round(maior_var,3), " do=", nome_maior_var, " e menor var=", round(menor_var,3), " do=", nome_menor_var )
            #odd_back = lista_corridas_ordenado[nome_maior_var]
            #wl_back = winLose[nome_maior_var]
            odd_lay = lista_corridas_ordenado[nome_menor_var]
            wl_lay = winLose[nome_menor_var]
            stack_lay = 20.0
            #self.stack_back = round(stack_lay/(odd-1),2)
            self.stack_back = stack_lay # Stack fixo
            #if( wl_back == 0 ): pl_back = (-1*self.stack_back) 
            #else: pl_back = self.stack_back*(odd_back)-self.stack_back
            #if( pl_back > 0 ): pl_back = pl_back*(1-comissao)
            pl_back = 0
            #Parte Lay
            if( wl_lay == 0 ): pl_lay = (+1*stack_lay)
            else: pl_lay = (-1*(stack_lay*(odd_lay-1)))
            if( pl_lay > 0 ): pl_lay = pl_lay*(1-comissao)
            #print("BSP=", lista_bsp)
            
            self.somaStack += 0*self.stack_back + stack_lay
            self.patrimonio += pl_back + pl_lay
            #print("Pat=", self.patrimonio, " aos=", minuto, " com=", self.idade)
            self.idade += 1   # Envelhece
            self.jaApostei = True
      if( self.somaStack != 0 ): self.lucro_medio = 1.0*(self.patrimonio-1000.0)/self.somaStack
      return False
               
   def __str__ (self):
      return "Nome="+self.nome + ", Retorno=" + str(round(self.lucro_medio,3)) + ", idade=" + str(self.idade)
      
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