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
         lista_participantes[runner_name] = 1.01 # Odd inicial
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
      
   def obtemMinutosDaCorrida(self, race_id):
      lista_minutos = []
      if( self.nomeBD is None ): return 1/0
      self.idCorrida_minutos = race_id # Lembra qual foi a corrida dos minutos
      conn = sqlite3.connect(self.nomeBD)
      c = conn.cursor()
      c.execute(""" SELECT  races.RaceId, 
      Cast (( JulianDay(races.MarketTime) - JulianDay(odds.PublishedTime) ) * 24 * 60 As Integer ) as Dif_Min
      FROM runners, races, odds
      WHERE runners.RaceId = races.RaceId
        AND odds.RaceId = races.RaceId
        AND odds.RunnerId = runners.RunnerId
        AND races.RaceId = ?
        AND runners.BSP <> -1
        AND runners.WinLose <> -1
      GROUP BY races.RaceId, Dif_Min
      ORDER BY races.RaceId, odds.PublishedTime ASC """, (race_id,) )
      while True: 
         row = c.fetchone()
         if row == None: break  # Acabou o sqlite
         runner_id, dif_min = row
         lista_minutos.append( dif_min )
      return lista_minutos   
   
   def obtemRegistroPorMinuto(self, minuto):
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
   