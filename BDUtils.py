import sqlite3
import operator
class BaseDeDados:
   """
   Representa o fluxo de odds se movimentando
   """
   def __init__(self):
      self.cursorBD = ''
   
   def conectaBaseDados(self, nomeBanco):
      self.nomeBD = nomeBanco
      conn = sqlite3.connect(self.nomeBD)
      self.cursorBD = conn.cursor()
      
   def efetuaConsultaCorrida(self, race_id):
      if( self.cursorBD is None ): return 1/0
      self.cursorBD.execute(""" SELECT 
        races.RaceId, races.MarketTime, races.InplayTimestamp, races.MarketName, races.MarketVenue,
        runners.RunnerId, runners.RunnerName, runners.WinLose, runners.BSP,
        odds.LastTradedPrice, odds.PublishedTime
      FROM runners, races, odds
      WHERE runners.RaceId = races.RaceId
        AND odds.RaceId = races.RaceId
        AND odds.RunnerId = runners.RunnerId
        AND races.RaceId = ?
        and (races.RaceId <> "1.159938420" AND races.RaceId <> "1.160357774" AND races.RaceId <> "1.160357775" AND races.RaceId <> "1.160934216" AND races.RaceId <> "1.162266316" AND races.RaceId <> "1.165629272")
        AND runners.BSP <> -1
        AND runners.WinLose <> -1
      ORDER BY races.RaceId, odds.PublishedTime ASC """, (race_id,) )
      self.fimRegistro = False
      
   def proximoRegistroCorrida(self):
      if( self.cursorBD is None ): return 1/0
      row = self.cursorBD.fetchone()
      if row == None:
         self.fimRegistro = True
      return row
      
   def chegouFimRegistroCorrida(self):
      return self.fimRegistro
   
   def obtemCorridas(self, qtd_corridas, ordem="ASC"):
      if( self.nomeBD is None ): return 1/0
      lista_corridas = []
      conn = sqlite3.connect(self.nomeBD)
      c_corrida = conn.cursor()
      if( ordem != "ASC" and ordem != "DESC" ): return 1/0
      if( ordem == "ASC" ):
         c_corrida.execute(""" SELECT * FROM races ORDER BY MarketTime ASC LIMIT ?; """, (qtd_corridas,) )
      if( ordem == "DESC" ):
         c_corrida.execute(""" SELECT * FROM races ORDER BY MarketTime DESC LIMIT ?; """, (qtd_corridas,) )
      while True: 
         row = c_corrida.fetchone()
         if row == None: break  # Acabou o sqlite
         race_id, market_time, inplay_timestamp, market_name, market_venue = row
         lista_corridas.append(race_id)
      return lista_corridas
      
   def obtemNomeMercadoDaCorrida(self, race_id):
      if( self.nomeBD is None ): return 1/0
      nome_mercado = ''
      conn = sqlite3.connect(self.nomeBD)
      c_corrida = conn.cursor()
      c_corrida.execute(""" SELECT * FROM races WHERE RaceId=?; """, (race_id,) )
      while True: 
         row = c_corrida.fetchone()
         if row == None: break  # Acabou o sqlite
         race_id, market_time, inplay_timestamp, market_name, market_venue = row
         nome_mercado = market_name
      return nome_mercado
      
   def obtemCorridasAleatorias(self, qtd_corridas):   
      if( self.nomeBD is None ): return 1/0
      lista_corridas = []
      conn = sqlite3.connect(self.nomeBD)
      c_corrida = conn.cursor()
      c_corrida.execute(""" SELECT * FROM races ORDER BY RANDOM() LIMIT ?; """, (qtd_corridas,) )
      #print("Inicio do processamento")  
      while True: 
         row = c_corrida.fetchone()
         if row == None: break  # Acabou o sqlite
         race_id, market_time, inplay_timestamp, market_name, market_venue = row
         #print("Col=", row)
         lista_corridas.append(race_id)
      return lista_corridas
   
   def obtemParticipantesDeCorrida(self, race_id):
      lista_participantes = {}
      lista_bsp = {}
      lista_wl = {}
      if( self.nomeBD is None ): return 1/0
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute(""" SELECT * FROM runners WHERE runners.RaceId = ? """, (race_id,) )       
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         runner_id, race_id2, runner_name, WinLose, BSP = row
         lista_participantes[runner_name] = -1.01 # Odd inicial
         lista_bsp[runner_name] = BSP
         lista_wl[runner_name] = WinLose
      return lista_participantes, lista_bsp, lista_wl
      
   def obtemNomesDosMercados(self):
      lista_mercados = []
      if( self.nomeBD is None ): return 1/0
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute(""" SELECT MarketName, COUNT(*) AS Total
                     FROM races 
                     GROUP BY MarketName
                     ORDER BY Total DESC """ )       
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         market_name, total_market = row
         lista_mercados.append( market_name )
      return lista_mercados
      
   def obtemLocaisDosMercados(self):
      lista_mercados = []
      if( self.nomeBD is None ): return 1/0
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute(""" SELECT MarketVenue, COUNT(*) AS Total
                     FROM races 
                     GROUP BY MarketVenue
                     ORDER BY Total DESC """ )       
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         market_venue, total_market = row
         lista_mercados.append( market_venue )
      return lista_mercados
   
   def obtemSumarioDasCorridas(self):
      if( self.nomeBD is None ): return 1/0
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute("""SELECT min(races.MarketTime) as data_inicial, MAX(races.MarketTime) as data_final, COUNT(*) as total_corridas 
      FROM races ORDER BY total_corridas DESC, data_inicial ASC""")
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         data_inicial, data_final, total_corridas = row
      return data_inicial, data_final, total_corridas
   
   def obtemCorridasDoCavalo(self, idCavalo):
      lista_corridas = []
      if( self.nomeBD is None ): return 1/0
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute("""SELECT runners.RunnerId, runners.RunnerName, races.MarketTime, races.RaceId
                     FROM runners, races
                    WHERE runners.RaceId = races.RaceId
                      AND runners.RunnerId = ?
                      AND runners.BSP <> -1 
                      AND runners.WinLose <> -1  
                    ORDER BY runners.RunnerId, races.MarketTime""", (idCavalo,) )
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         runner_id, runner_name, market_time, race_id = row
         lista_corridas.append( race_id )
      return lista_corridas
   
   def obtemMinutosDaCorrida(self, race_id):
      lista_minutos = []
      if( self.nomeBD is None ): return 1/0
      self.idCorrida_minutos = race_id # Lembra qual foi a corrida dos minutos
      self.lista_corridas = {} # Cada corrida tem uma lista de cavalos
      self.lista_bsp = {} # Para saber qual eh o BSP correspondente
      self.lista_wl = {} # Para saber quem foi Win e quem foi Lose
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute(""" SELECT  races.RaceId, 
      odds_position.MinutesUntillRace as Dif_Min
      FROM runners, races, odds_position
      WHERE runners.RaceId = races.RaceId
        AND odds_position.RaceId = races.RaceId
        AND odds_position.RunnerId = runners.RunnerId
        AND races.RaceId = ?
        AND runners.BSP <> -1
        AND runners.WinLose <> -1
      GROUP BY races.RaceId, Dif_Min
      ORDER BY races.RaceId, odds_position.MinutesUntillRace DESC """, (race_id,) )
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         runner_id, dif_min = row
         lista_minutos.append( dif_min )
      return lista_minutos   
   
   def obtemExtremosDosMinutos(self): # Demora meia hora para executar. max=4544	e min=-229, na base atual
      minuto_maximo = None
      minuto_minimo = None
      if( self.nomeBD is None ): return 1/0
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute("""SELECT  
              max(Cast (( JulianDay(races.MarketTime) - JulianDay(odds.PublishedTime) ) * 24 * 60 As Integer )) as maximo
              ,min(Cast (( JulianDay(races.MarketTime) - JulianDay(odds.PublishedTime) ) * 24 * 60 As Integer )) as minimo
                  FROM runners, races, odds
                  WHERE runners.RaceId = races.RaceId
                    AND odds.RaceId = races.RaceId
                    AND odds.RunnerId = runners.RunnerId
                    AND runners.BSP <> -1
                    AND runners.WinLose <> -1""")
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         minuto_maximo, minuto_minimo = row
      return minuto_maximo, minuto_minimo 
   
   def obtemOddsPorMinuto(self, minuto, params=[] ):
      if( self.nomeBD is None ): return 1/0
      if( self.idCorrida_minutos is None ): return 1/0
      lista_corridas_ordenado = None
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute(""" SELECT  races.RaceId, races.MarketTime, races.InplayTimestamp, races.MarketName, races.MarketVenue,  
      odds_position.MinutesUntillRace as Dif_Min
      , runners.RunnerId, runners.RunnerName, runners.WinLose, runners.BSP,
      odds_position.CurrentPrice
      FROM runners, races, odds_position
      WHERE runners.RaceId = races.RaceId
        AND odds_position.RaceId = races.RaceId
        AND odds_position.RunnerId = runners.RunnerId
        AND races.RaceId = ?
        AND runners.BSP <> -1
        AND runners.WinLose <> -1
		AND Dif_Min=?
      ORDER BY races.RaceId, odds_position.MinutesUntillRace ASC """, (self.idCorrida_minutos, minuto) )
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         self.race_id, market_time, inplay_timestamp, market_name, market_venue, dif_min, runner_id, nome_cavalo, win_lose, bsp, odd = row
         if( self.race_id not in self.lista_corridas ): 
            self.lista_corridas[self.race_id], self.lista_bsp[self.race_id], self.lista_wl[self.race_id] = self.obtemParticipantesDeCorrida(self.race_id)
         self.lista_corridas[self.race_id][nome_cavalo] = odd #Atualiza as odds dessa corrida
         self.lista_bsp[self.race_id][nome_cavalo] = bsp # Sabendo o BSP do cavalo
         self.lista_wl[self.race_id][nome_cavalo] = win_lose # Sabendo o Win/Lose do cavalo
         lista_corridas_ordenado = dict( sorted( self.lista_corridas[self.race_id].items(), key=operator.itemgetter(1),reverse=False ) ) # Mostra igual no site. Odds menores primeiro.
         
      return lista_corridas_ordenado
   
   def obtemAdjustmentFactorProximo(self, minuto, qtd_cavalos):
      if( self.nomeBD is None ): return 1/0
      if( self.idCorrida_minutos is None ): return 1/0
      dict_adjustment_factors = {}
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute("""SELECT afs_position.RaceId, afs_position.RunnerId, afs_position.CurrentAF, afs_position.MinutesUntillRace,
                  runners.RunnerName
                  FROM afs_position, runners
                  WHERE runners.RaceId = afs_position.RaceId
                    AND runners.RunnerId = afs_position.RunnerId
                    AND runners.RaceId= ?
                    AND runners.BSP <> -1
                    AND runners.WinLose <> -1
                    AND MinutesUntillRace <= ?
                  ORDER BY ABS(MinutesUntillRace - ?)
                  LIMIT ? """, (self.idCorrida_minutos, minuto, minuto, qtd_cavalos ) )
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         self.race_id, runner_id, currentAF, minutes, nome_cavalo = row
         if( minutes > minuto ): 
            print(self.race_id, runner_id, currentAF, minutes, nome_cavalo)
            x = 1/0 # Não pode!
         dict_adjustment_factors[nome_cavalo] = currentAF
      if( dict_adjustment_factors == {} ):
         lista_participantes, lista_bsp, lista_wl = self.obtemParticipantesDeCorrida(self.idCorrida_minutos)
         nomes_cavalos = lista_participantes.keys()
         for cavalo in nomes_cavalos:
            dict_adjustment_factors[cavalo] = 0.0 # Porcentagem fica zerada
      return dict_adjustment_factors
   
   def obtemBSPAtual(self, nome_cavalo):
      return self.lista_bsp[self.race_id][nome_cavalo]
      
   def obtemWinLoseAtual(self, nome_cavalo):
      return self.lista_wl[self.race_id][nome_cavalo]
   
   def obtemRegistroPorMinuto(self, minuto): # Da rede neural
      self.lista_corridas = {} # Cada corrida tem uma lista de cavalos
      self.lista_bsp = {} # Para saber qual eh o BSP correspondente
      self.lista_wl = {} # Para saber quem foi Win e quem foi Lose
      if( self.nomeBD is None ): return 1/0
      if( self.idCorrida_minutos is None ): return 1/0
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute(""" SELECT  races.RaceId, races.MarketTime, races.InplayTimestamp, races.MarketName, races.MarketVenue,  
      Cast (( JulianDay(races.MarketTime) - JulianDay(odds.PublishedTime) ) * 24 * 60 As Integer ) as Dif_Min
      , runners.RunnerId, runners.RunnerName, runners.WinLose, runners.BSP,
      odds.LastTradedPrice, odds.PublishedTime
      FROM runners, races, odds
      WHERE runners.RaceId = races.RaceId
        AND odds.RaceId = races.RaceId
        AND odds.RunnerId = runners.RunnerId
        AND races.RaceId = ?
        AND runners.BSP <> -1
        AND runners.WinLose <> -1
		AND Dif_Min=?
      ORDER BY races.RaceId, odds.PublishedTime ASC """, (self.idCorrida_minutos, minuto) )
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         #runner_id, market_time, published_time, dif_min, odds runner_name, win_lose, bsp = row
         self.race_id, market_time, inplay_timestamp, market_name, market_venue, dif_min, runner_id, nome_cavalo, win_lose, bsp, odd, data = row
         if( self.race_id not in self.lista_corridas ): 
            self.lista_corridas[self.race_id], self.lista_bsp[self.race_id], self.lista_wl[self.race_id] = self.obtemParticipantesDeCorrida(self.race_id)
         self.lista_corridas[self.race_id][nome_cavalo] = odd #Atualiza as odds dessa corrida
         self.lista_bsp[self.race_id][nome_cavalo] = bsp # Sabendo o BSP do cavalo
         self.lista_wl[self.race_id][nome_cavalo] = win_lose # Sabendo o Win/Lose do cavalo
         lista_corridas_ordenado = dict( sorted( self.lista_corridas[self.race_id].items(), key=operator.itemgetter(1),reverse=False ) ) # Mostra igual no site. Odds menores primeiro.
         self.melhores_odds = list(lista_corridas_ordenado.items())[0:3] # Top 3 odds
         
         if( len(self.melhores_odds) < 3 ) : return None #print("Deu merda!")
         if( dif_min > 60 or dif_min < 1 ): return None # Apenas uma hora antes
         
         idx_qtd_min = 1.0*dif_min/60 # Entre 0 e 1
         prob1 = 1.0/self.melhores_odds[0][1]
         prob2 = 1.0/self.melhores_odds[1][1]
         prob3 = 1.0/self.melhores_odds[2][1]
      #print("Teste=", self.race_id, ", min=", dif_min, ", minuto=", minuto )
      return idx_qtd_min, prob1, prob2, prob3
   