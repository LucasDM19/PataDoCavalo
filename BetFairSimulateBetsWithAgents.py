import sqlite3
from datetime import datetime, timedelta
from simulamc import MeioAmbiente, AgenteApostadorCavalo

lista_corridas = {} # Cada corrida tem uma lista de cavalos
lista_bsp = {} # Para saber qual eh o BSP correspondente
lista_wl = {} # Para saber quem foi Win e quem foi Lose
stack_lay = 20.0 # valor base - responsabilidade lay
comissao = 0.065 # 0.0650 - BetFair

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
     AND runners.BSP <> -1
     AND runners.WinLose <> -1
   ORDER BY races.RaceId, odds.PublishedTime ASC """)      
print("Inicio do processamento")   
mundo = MeioAmbiente(qtd_agentes=50, tipoAgente=AgenteApostadorCavalo)   # Crio mundo
benchmark = AgenteApostadorCavalo()
#benchmark.defineAtributos(nome="BENCH", minutos_back=0, minutos_lay=60  )   # O que tem hoje
#benchmark.defineAtributos(nome="HCX5CHGNCB", odd_back_min=6.69, odd_back_max=1.45, minutos_back=482, minutos_lay=73  )  # Faz apenas lay faltando meia hora
#benchmark.defineAtributos(nome="RMNCQLBS2E", odd_back_min=4.16, odd_back_max=6.7, minutos_back=85, odd_lay_max=2.0, odd_lay_min=8.0, minutos_lay=850  )  # Era canto de sereia
mundo._agentes.append( benchmark )
while True: 
   row = c.fetchone()
   if row == None: break  # Acabou o sqlite      
   race_id, market_time, inplay_timestamp, market_name, market_venue, runner_id, nome_cavalo, win_lose, bsp, odd, data = row
   if( race_id not in lista_corridas ): 
      lista_corridas[race_id] = {}
      lista_bsp[race_id] = {}
      lista_wl[race_id] = {}
      mundo.notificaNovaCorrida()   # Se preparem para apostar
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
   mundo.recebeAtualizacao(odd=odd_favorito, minuto=qtd_min, winLose=wl_favorito, race_id=race_id)
   
mundo.exibeAgentes()