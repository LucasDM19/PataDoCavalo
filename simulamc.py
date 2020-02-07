import random, string
import operator
import copy
import neat # pip install neat-python

# Mundo que utiliza rede neural NEAT
class MeioAmbienteNeural():
   def __init__(self, config_file):
      self.config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
               neat.DefaultSpeciesSet, neat.DefaultStagnation,
               config_file)
   
   # Cria a populacao
   def criaPopulacao(self):
      self.p = neat.Population(self.config)
   
   # Cria um Reporter StdOut
   def criaReporterStdOut(self):
      self.p.add_reporter(neat.StdOutReporter(True))
      self.stats = neat.StatisticsReporter()
      self.p.add_reporter(self.stats)
      #self.p.add_reporter(neat.Checkpointer(5))

# Mundo basico para agentes com variacoes de atributos
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
      self.cres_exp = 0.0 # Crescimento exponencial da banca
      
   def estouVivo(self):
      if( self.patrimonio <= 0 ): return False
      return True
   
   def atualizaRetorno(self):
      if( self.somaStack != 0 ): self.lucro_medio = 1.0*(self.patrimonio-1000.0)/self.somaStack
      
   # Faz apenas Back
   def fazApostaBack(self, odd_back, stack_back, wl_back, fracao_aposta=1.0, comissao = 0.065):
      stack_back *= fracao_aposta # Aposto uma determinada fracao do Stack
      if( stack_back < 2 ): return 0 # Sem condicao
      if( wl_back == 0 ): 
         pl_back = (-1*stack_back) 
      elif( wl_back == 1 ): 
         pl_back = stack_back*(odd_back)-stack_back
      else: return 0 # WL invalido nao conta
      if( pl_back > 0 ): 
         pl_back = pl_back*(1-comissao)
      self.somaStack += stack_back
      #print("Aposta back ", stack_back ," na odd ", odd_back , " teve PL=", round(pl_back,2), " e WL=", wl_back, ", frac=", fracao_aposta )   
      #input("Teve aposta.")      
      #if( self.somaStack != 0 ): print("Pat depois=", self.lucro_medio, " $=", self.patrimonio, " SS=", self.somaStack )
      return pl_back
      
   # Faz apenas Lay
   def fazApostaLay(self, odd_lay, stack_lay, wl_lay, fracao_aposta=1.0, comissao = 0.065):
      stack_lay *= fracao_aposta # Aposto uma determinada fracao do Stack
      if( stack_lay < 2 ): return 0 # Sem condicao
      if( wl_lay == 0 ): 
         pl_lay = (+1*stack_lay)
      elif( wl_back == 1 ): 
         pl_lay = (-1*(stack_lay*(odd_lay-1)))
      else: return 0 # WL invalido nao conta
      if( pl_lay > 0 ): 
         pl_lay = pl_lay*(1-comissao)
      self.somaStack += stack_lay
      #print("Aposta lay ", stack_lay ," na odd ", odd_lay , " teve PL=", round(pl_lay,2), " e WL=", wl_lay )
      return pl_lay
   
   # Back e lay simples
   def fazApostaBackLay(self, odd_back, stack_back, wl_back, odd_lay, stack_lay, wl_lay, comissao = 0.065 ):
      if( stack_lay < 2 ): return 0 # Sem condicao
      if( stack_back < 2 ): return 0 # Sem condicao
      pl_back = self.fazApostaBack(odd_back, stack_back, wl_back)
      pl_lay = self.fazApostaLay(odd_lay, stack_lay, wl_lay)
      pl = pl_back + pl_lay
      #print("1/2 Aposta back ", stack_back ," na odd ", odd_back , " teve PL=", round(pl_back,2), " e WL=", wl_back )
      #print("2/2 Aposta lay ", stack_lay ," na odd ", odd_lay , " teve PL=", round(pl_lay,2), " e WL=", wl_lay )
      return pl

# Classe que utiliza rede neural
class AgenteNEAT(AgenteApostador):
   def iniciaMindset(self):
      super().iniciaMindset() # Inicio o basico do apostador
   #def fazApostaBack(self, odd_back, stack_back, wl_back, comissao = 0.065):
   #   super().fazApostaBack(odd_back, stack_back, wl_back, comissao = 0.065)

# Agente para apostas que envolvem tendencias de odds. Nao apenas para o favorito.
class AgenteEspeculadorCavalo(AgenteApostador):
   def iniciaMindset(self):
      super().iniciaMindset() # Inicio o basico do apostador
      stackBack = random.choice(["Fixo", "Proporcional"]) # Fixo ou Proporcional
      #ndvqdsdb = "Proporcional"
      stackLay = random.choice(["Fixo", "Proporcional"]) # Fixo ou Proporcional
      #ndvqdsdl = "Fixo"
      #self.defineAtributos(nome=self.nome, stkb=ndvqdsdb , stkl=ndvqdsdl )
      self.defineAtributos(nome=self.nome, stkb=stackBack , stkl=stackLay, min=0.00, max=9.290, temBack=True, temLay=False, tipoBack="Atual", tipoLay="Atual", tipoTrend="Maior" )
   
   def defineAtributos(self, nome, min=None, max=None, mins=None, temBack=None, temLay=None, tipoBack=None, tipoLay=None, tipoTrend=None, stkb=None, stkl=None ):
      self.nome=nome 
      if( min is None ): self.minimo_trend = random.uniform(0.0, 0.290)
      else: self.minimo_trend=min
      if( max is None ): self.maximo_trend = random.uniform(self.minimo_trend, 0.290)
      else: self.maximo_trend = max
      if( mins is None ): 
         qtd_intervalo = random.randrange(2, 50) # Quantas amostras serao obtidas para obter trend
         n_min = [ random.randrange(1, 150) for n in range(qtd_intervalo)] # Gera numeros aleatorios
         n_min_s_rep = list(set(n_min)) # Removo duplicatas
         n_min_s_rep.sort(reverse=True) # Ordem ascendente - feita sem retorno de nada
         self.minutos = n_min_s_rep #
         #self.minutos = [random.randrange(2, 150), 1] # Testando
         qtd_intervalo = len(self.minutos)
      else: 
         self.minutos=mins 
         qtd_intervalo = len(self.minutos)
      if( temBack is None ): self.temApostaBack = bool(random.getrandbits(1)) # True tem back
      else: self.temApostaBack = temBack
      if( temLay is None ): self.temApostaLay = bool(random.getrandbits(1)) # True tem lay
      else: self.temApostaLay = temLay
      if( tipoBack is None ): self.tipoOddBack = random.choice(["Atual", "BSP"]) # Atual ou BSP
      else: self.tipoOddBack = tipoBack
      if( tipoLay is None ):
         if( self.tipoOddBack == "BSP" ) : self.tipoOddLay = "Atual"
         else: self.tipoOddLay = random.choice(["Atual", "BSP"]) # Atual ou BSP
      else: self.tipoOddLay = tipoLay
      if( stkb is None ): self.tipoStackBack = random.choice(["Fixo", "Proporcional"]) # Fixo ou Proporcional
      self.tipoStackBack = stkb
      #print("SB=", self.tipoStackBack)
      if( stkl is None ): self.tipoStackLay = random.choice(["Fixo", "Proporcional"]) # Fixo ou Proporcional
      self.tipoStackLay = stkl
      if( tipoTrend is None ): self.tipoTrend = random.choice(["Maior", "Menor"]) # Maior ou Menor
      else: self.tipoTrend = tipoTrend
      
      self.estrategia = "" # Para categorizacao mesmo
      if( self.temApostaBack ): self.estrategia += "Back"
      if( self.tipoOddBack == "BSP" ): self.estrategia += "BSP"
      if( self.tipoStackBack == "Proporcional" ): self.estrategia += "Prop"
      if( self.temApostaLay ): self.estrategia += "Lay"
      if( self.tipoOddLay == "BSP" ): self.estrategia += "BSP"
      if( self.tipoStackLay == "Proporcional" ): self.estrategia += "Prop"
      if( self.tipoTrend == "Maior" ): self.estrategia += "+"
      if( self.tipoTrend == "Menor" ): self.estrategia += "-"
      #print("Do grego=", self.estrategia)
      self.todos_trend = ["X"+str(x) for x in range(2,qtd_intervalo+1)] #["X2","X3","X4","X5","X6","X7","X8",]
      self.todos_trend_x = ["X1",] +  self.todos_trend
      #print(self.todos_trend_x, self.todos_trend )
   
   def novaCorrida(self):
      self.jaApostei = False
      self.trend = { x : {} for x in self.todos_trend } # Calcula tendencia
      self.valores_odds = { x : {} for x in self.todos_trend_x } # Memoriza as odds
      
   def calculaTrend(self, valores_odds_a, valores_odds_b, lista_corrida, cp=False):
      #print(valores_odds_a, valores_odds_b)
      trend = {}
      for lco in lista_corrida:
         if(lco not in valores_odds_a or lco not in valores_odds_b): trend[lco] = 0.0 # Sem comparacao, sem variacao
         else: 
            trend[lco] = log( valores_odds_a[lco]/valores_odds_b[lco] )
            if(cp==True): print("lco=", lco, "a=", valores_odds_a[lco], "b=",valores_odds_b[lco], "Trend=", round(trend[lco],4) )
      return trend
      
   def decide(self, lista_corridas_ordenado, minuto, winLose, lista_bsp, race_id=0 ):
      comissao = 0.065
      #print("Dado: Odd=", lista_corridas_ordenado, ", minuto=", minuto, ", W/L=", winLose, ", race=", race_id)
      #lista_corridas_ordenado = dict( sorted( lista_corridas.items(), key=operator.itemgetter(1),reverse=False ) ) # Mostra igual no site. Odds menores primeiro.
      for idx_min in range(len(self.minutos)): # Para todas as faixas de acompanhamento
         if( minuto == self.minutos[idx_min] ):
            qual_x = self.todos_trend_x[idx_min]
            #print("Hora do ", qual_x)
            self.valores_odds[qual_x] = copy.deepcopy(lista_corridas_ordenado)
            #print("Valor do ", qual_x, "=", self.valores_odds[qual_x] )
            if( idx_min != 0 ): # Primeiro nao tem anterior
               qual_x_ant = self.todos_trend_x[idx_min-1]
               self.trend[qual_x] = self.calculaTrend(valores_odds_a=self.valores_odds[qual_x], valores_odds_b=self.valores_odds[qual_x_ant], lista_corrida=lista_corridas_ordenado, cp=False)
            if( idx_min == len(self.minutos)-1 ): # Ultimo tem a aposta em si
               #for vtc in self.todos_trend: print("Vals=", vtc, self.trend[vtc])
               #print("X1=", self.valores_odds["X1"])
               media_trend = {}
               #for x in self.todos_trend: print("Trend=",x, self.trend[x])
               for vlox in self.valores_odds["X1"]: media_trend[vlox] = sum( [self.trend[x][vlox] for x in self.todos_trend  ] ) / (len(self.todos_trend)) # Tiro media de cada trend
               #for m in media_trend: print("Media Trend de ", m,"=", round(media_trend[m],4) ) # Exibo cada media
               #print([self.trend[x][vlox] for x in self.todos_trend for vlox in self.valores_odds["X1"]  ])
               if( len([media_trend[n] for n in media_trend]) == 0 ): return False # Sem aposta
               maior_valor_trend = max([media_trend[n] for n in media_trend])
               menor_valor_trend = min([media_trend[n] for n in media_trend])
               nome_maior_trend = [m for m in media_trend if media_trend[m] == maior_valor_trend ][0]
               nome_menor_trend = [m for m in media_trend if media_trend[m] == menor_valor_trend ][0]
               #print("Maior=", nome_maior_trend, " e menor=", nome_menor_trend )
               
               if( self.jaApostei == False ):
                  if( self.tipoTrend == "Maior" ): 
                     nome_trend = nome_maior_trend
                     valor_trend = maior_valor_trend
                  if( self.tipoTrend == "Menor" ): 
                     nome_trend = nome_menor_trend
                     valor_trend = menor_valor_trend
                  if( self.maximo_trend >= abs(valor_trend) and self.minimo_trend <= abs(valor_trend)): # Tem um teto de trend
                     if( self.temApostaBack ): # Devo fazer back
                        if( self.tipoOddBack == "Atual" ): odd_back = lista_corridas_ordenado[nome_trend] 
                        if( self.tipoOddBack == "BSP" ): odd_back = lista_bsp[nome_trend] 
                        if( self.tipoStackBack == "Fixo" ): stack_back = 20.0
                        if( self.tipoStackBack == "Proporcional" ): stack_back = round(20.0/(odd_back-1),2)
                        wl_back = winLose[nome_trend]
                        if( self.temApostaLay == False ): # Somente Back, sem Lay
                           pl_back = self.fazApostaBack(odd_back, stack_back, wl_back)
                           self.patrimonio += pl_back
                     if( self.temApostaLay ): # Devo fazer lay
                        if( self.tipoOddLay == "Atual" ): odd_lay = lista_corridas_ordenado[nome_trend] 
                        if( self.tipoOddLay == "BSP" ): odd_lay = lista_bsp[nome_trend]
                        if( self.tipoStackLay == "Fixo" ): stack_lay = 20.0
                        if( self.tipoStackLay == "Proporcional" ): stack_lay = round(20.0/(odd_lay-1),2)
                        wl_lay = winLose[nome_trend]
                        if( self.temApostaBack == False ): # Somente LAy, sem Back
                           pl_lay = self.fazApostaLay(odd_lay, stack_lay, wl_lay)
                           self.patrimonio += pl_lay
                     if( self.temApostaBack and self.temApostaLay ): # Os dois ao mesmo tempo
                        pl_bl = self.fazApostaBackLay(odd_back, stack_back, wl_back, odd_lay, stack_lay, wl_lay)
                        self.patrimonio += pl_bl
                     #x = 18/0 
                     self.idade += 1   # Envelhece
                     self.jaApostei = True 
      if( self.somaStack != 0 ): self.lucro_medio = 1.0*(self.patrimonio-1000.0)/self.somaStack
      return False
               
   def __str__ (self):
      return "Nome="+self.nome + ", Estrategia="+self.estrategia + ", min=" + str(round(self.minimo_trend,3)) + ", max=" + str(round(self.maximo_trend,3)) + ", mins="+str(self.minutos)+ ", idade=" + str(self.idade) + ", Retorno=" + str(round(self.lucro_medio,3)) 
      
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