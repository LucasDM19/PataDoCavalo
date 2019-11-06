import sqlite3
from datetime import datetime, timedelta

lista_corridas = {} # Cada corrida tem uma lista de cavalos
lista_bsp = {} # Para saber qual eh o BSP correspondente
stack_lay = 20.0 # valor base - responsabilidade lay
soma_pl = 0.0 # O total que pingaria na conta
total_partidas = 0 # Quantas corridas tiveram
apostei = False # Ativa apenas quando chegaria a hora

conn = sqlite3.connect('C:\\Users\\152456\\Downloads\\bf_gb_win.db')
c = conn.cursor()
c.execute(""" SELECT 
     races.RaceId, races.MarketTime, races.InplayTimestamp, races.MarketName, races.MarketVenue,
     runners.RunnerId, runners.RunnerName, runners.WinLose, runners.BSP,
     odds.LastTradedPrice, odds.PublishedTime
   FROM runners, races, odds
   WHERE runners.RaceId = races.RaceId
     AND odds.RaceId = races.RaceId
     AND odds.RunnerId = runners.RunnerId
     AND runners.BSP <> -1
   ORDER BY races.RaceId, odds.PublishedTime ASC """)         
while True: 
   row = c.fetchone()
   if row == None: break  # Acabou o sqlite
            
   race_id, market_time, inplay_timestamp, market_name, market_venue, runner_id, nome_cavalo, win_lose, bsp, odd, data = row
   if( race_id not in lista_corridas ): 
      lista_corridas[race_id] = {}
      lista_bsp[race_id] = {}
      apostei = False
   uma_hora_antes = datetime.strptime(inplay_timestamp, '%Y-%m-%d %H:%M:%S') - timedelta(hours=1, minutes=0) # Horario para avaliar odds
   if( datetime.strptime(data, '%Y-%m-%d %H:%M:%S') <= uma_hora_antes ): # Ainda tem mais de uma hora
      lista_corridas[race_id][nome_cavalo] = odd #Atualiza as odds dessa corrida
      lista_bsp[race_id][nome_cavalo] = bsp # Sabendo o BSP do cavalo
      favorito = min( lista_corridas[race_id], key=lista_corridas[race_id].get ) # Nome do cavalo com menor odd
      odd_favorito = lista_corridas[race_id][favorito]
      bsp_favorito = lista_bsp[race_id][favorito]
      stack_back = round(stack_lay/(odd_favorito-1),2)
      if( win_lose == "0" ): pl = (-1*stack_back) + stack_lay/(bsp_favorito-1)
      if( win_lose == "1" ): pl = stack_back/(odd_favorito-1) + (-1*stack_lay)
      #print(row)
   else: # Ja apostou
      if(not apostei):
         apostei = True
         soma_pl += pl
         total_partidas += 1
         print(race_id, ", PL=", pl, ", Total PL=", soma_pl, " partidas=", total_partidas, ", odd=", odd_favorito, ", BSP=", bsp_favorito )
         #if( race_id in ["1.159620525", "1.157891258", "1.159688325", "1.153171146", "1.155132765", "1.153722792", "1.158983876" ] ):
            #print("aqui:", lista_corridas[race_id], "favorito:", favorito, ", BSP=", bsp_favorito, bsp, ", raceId=", race_id, ", PL=", pl, ", Total PL=", soma_pl, " partidas=", total_partidas, "stack back", stack_back, ", W/L=", win_lose)
      #print("Perdeu!", datetime.strptime(data, '%Y-%m-%d %H:%M:%S'), ", ", uma_hora_antes)
      
   #print(row)
   