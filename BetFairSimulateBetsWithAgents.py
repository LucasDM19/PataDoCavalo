import sqlite3
import copy
from datetime import datetime, timedelta
import time
import operator
from simulamc import MeioAmbiente, AgenteApostadorCavalo, AgenteEspeculadorCavalo

lista_corridas = {} # Cada corrida tem uma lista de cavalos
lista_bsp = {} # Para saber qual eh o BSP correspondente
lista_wl = {} # Para saber quem foi Win e quem foi Lose
tempo_anterior = -999 # Para deixar a fita temporal coerente
odd_anterior = {}
winLose_anterior = {}
bsp_anterior = {}
conn = sqlite3.connect('bf_gb_win_2009.db')
c = conn.cursor()
c.execute(""" SELECT 
     races.RaceId, races.MarketTime, races.InplayTimestamp, races.MarketName, races.MarketVenue,
     runners.RunnerId, runners.RunnerName, runners.WinLose, runners.BSP,
     odds.LastTradedPrice, odds.PublishedTime
   FROM runners, races, odds
   WHERE runners.RaceId = races.RaceId
     AND odds.RaceId = races.RaceId
     AND odds.RunnerId = runners.RunnerId
     and (races.RaceId <> "1.159938420" AND races.RaceId <> "1.160357774" AND races.RaceId <> "1.160357775" AND races.RaceId <> "1.160934216" AND races.RaceId <> "1.162266316" AND races.RaceId <> "1.165629272")
     AND runners.BSP <> -1
     AND runners.WinLose <> -1
   ORDER BY races.RaceId, odds.PublishedTime ASC """)      
print("Inicio do processamento")   
mundo = MeioAmbiente(qtd_agentes=50, tipoAgente=AgenteEspeculadorCavalo)   # Crio mundo
#benchmark = AgenteEspeculadorCavalo()
benchmark2 = AgenteEspeculadorCavalo()
#benchmark.defineAtributos(nome="0AWCKP31IA", min=0.0, max=0.29, mins=[88, 74, 60, 46, 32, 18, 4], temBack=True, temLay=True, tipoBack="Atual", tipoLay="BSP", tipoTrend="Maior" )  # Retorno de ~1,1%
benchmark2.defineAtributos(nome="FU8YXOUW0T", min=0.0, max=0.29, mins=[44, 39, 34, 29, 24, 19, 14, 9, 4], temBack=True, temLay=True, tipoBack="Atual", tipoLay="BSP", tipoTrend="Maior", stackBack = "Proporcional", stackLay = "Fixo" ) # Retorno de ~2,7%
#benchmark2.defineAtributos(nome="0AWCKP31IA", min=0.0, max=0.29, mins=[88, 74, 60, 46, 32, 18, 4], temBack=True, temLay=True, tipoBack="Atual", tipoLay="BSP", tipoTrend="Maior" )  # Tira teima
#mundo._agentes.append( benchmark )
mundo._agentes.append( benchmark2 ) 
while True: 
   row = c.fetchone()
   if row == None: break  # Acabou o sqlite
   start = time.process_time() # Liga relogio
   race_id, market_time, inplay_timestamp, market_name, market_venue, runner_id, nome_cavalo, win_lose, bsp, odd, data = row
   if( race_id not in lista_corridas ): 
      #print("Corrida nova!")
      lista_corridas[race_id] = {}
      lista_bsp[race_id] = {}
      lista_wl[race_id] = {}
      mundo.notificaNovaCorrida(race_id)   # Se preparem para apostar
   delta = datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') - datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
   qtd_min = ((delta.seconds) // 60)
   #print('Segundos=', ((delta.seconds) // 1), 'Minutos=', ((delta.seconds) // 60), 'd1=', market_time, 'd2=', data )
   if( datetime.strptime(data, '%Y-%m-%d %H:%M:%S') > datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') ) : # Corrida em andamento
      delta = (datetime.strptime(data, '%Y-%m-%d %H:%M:%S') - datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') )
      qtd_min = -1 * ((delta.seconds) // 60)
   lista_corridas[race_id][nome_cavalo] = odd #Atualiza as odds dessa corrida
   lista_bsp[race_id][nome_cavalo] = bsp # Sabendo o BSP do cavalo
   lista_wl[race_id][nome_cavalo] = win_lose # Sabendo o Win/Lose do cavalo
   favorito = min( lista_corridas[race_id], key=lista_corridas[race_id].get ) # Nome do cavalo com menor odd
   #print("Fav=", favorito)
   odd_favorito = lista_corridas[race_id][favorito]
   bsp_favorito = lista_bsp[race_id][favorito]
   wl_favorito = lista_wl[race_id][favorito]
   #lista_corridas_ordenado = dict( sorted( lista_corridas[race_id].items(), key=operator.itemgetter(1),reverse=False ) ) # Mostra igual no site. Odds menores primeiro.
   #print("silencio da fita:", [qm for qm in range(tempo_anterior-1,qtd_min,-1)])
   #if (len([qm for qm in range(tempo_anterior-1,qtd_min,-1)]) != 0 ): x = 1/0
   #print("Minutos de silencio, ant=", odd_anterior, ", atu=", lista_corridas[race_id])
   [mundo.recebeAtualizacao(odd=odd_anterior, minuto=qm, winLose=winLose_anterior, bsp=bsp_anterior, race_id=race_id) for qm in range(tempo_anterior-1,qtd_min,-1)  ]
   #print("Fita normal, ant=", odd_anterior, ", atu=", lista_corridas[race_id])
   mundo.recebeAtualizacao(odd=lista_corridas[race_id], minuto=qtd_min, winLose=lista_wl[race_id], bsp=lista_bsp[race_id], race_id=race_id)
   tempo_anterior = qtd_min
   odd_anterior = copy.deepcopy(lista_corridas[race_id])
   winLose_anterior = copy.deepcopy(lista_wl[race_id])
   bsp_anterior = copy.deepcopy(lista_bsp[race_id])
   #print("Demorou", time.process_time() - start)
   #if(time.process_time() - start > 0 ) : x = 1/0
   #print("Fim do ciclo - dados novos!")
   
mundo.exibeAgentes()