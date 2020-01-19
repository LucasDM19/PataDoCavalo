import sqlite3
from datetime import datetime, timedelta
from simulamc import MeioAmbiente, AgenteApostadorCavalo

lista_corridas = {} # Cada corrida tem uma lista de cavalos
lista_bsp = {} # Para saber qual eh o BSP correspondente
stack_lay = 20.0 # valor base - responsabilidade lay
comissao = 0.065 # 0.0650 - BetFair
minutos_antecedencia = 60   # Quanto tempo antes da corrida iniciar
soma_pl = 0.0 # O total que pingaria na conta
soma_stack = 0.0 # Quanto foi apostado no total
total_partidas = 0 # Quantas corridas tiveram
apostei = False # Ativa apenas quando chegaria a hora

conn = sqlite3.connect('bf_gb_win_full.db')
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
mundo = MeioAmbiente(qtd_agentes=50)   # Crio mundo
benchmark = AgenteApostadorCavalo()
#benchmark.defineAtributos(nome="BENCH", odd_back_min=1.5, odd_back_max=2.8, minutos_lay=0, minutos_back=90  )   # O que tem hoje
#benchmark.defineAtributos(nome="HCX5CHGNCB", odd_back_min=6.69, odd_back_max=1.45, minutos_back=482, minutos_lay=73  )  # Faz apenas lay faltando meia hora
#mundo._agentes.append( benchmark )
while True: 
   row = c.fetchone()
   if row == None: break  # Acabou o sqlite
            
   race_id, market_time, inplay_timestamp, market_name, market_venue, runner_id, nome_cavalo, win_lose, bsp, odd, data = row
   if( race_id not in lista_corridas ): 
      lista_corridas[race_id] = {}
      lista_bsp[race_id] = {}
      apostei = False
      mundo.notificaNovaCorrida()   # Se preparem para apostar
   uma_hora_antes = datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') - timedelta(hours=0, minutes=minutos_antecedencia) # Horario para avaliar odds
   delta = datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') - datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
   qtd_min = ((delta.seconds) // 60)
   #print('Minutos=', ((delta.seconds) // 60), 'd1=', market_time, 'd2=', data )
   if( datetime.strptime(data, '%Y-%m-%d %H:%M:%S') > datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') ) : # Corrida em andamento
      delta = (datetime.strptime(data, '%Y-%m-%d %H:%M:%S') - datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') )
      qtd_min = -1 * ((delta.seconds) // 60)
   lista_corridas[race_id][nome_cavalo] = odd #Atualiza as odds dessa corrida
   lista_bsp[race_id][nome_cavalo] = bsp # Sabendo o BSP do cavalo
   favorito = min( lista_corridas[race_id], key=lista_corridas[race_id].get ) # Nome do cavalo com menor odd
   odd_favorito = lista_corridas[race_id][favorito]
   bsp_favorito = lista_bsp[race_id][favorito]
   stack_back = round(stack_lay/(odd_favorito-1),2)
   if( win_lose == 0 ): pl = (-1*stack_back) + stack_lay/(bsp_favorito-1)
   if( win_lose == 1 ): pl = stack_back/(odd_favorito-1) + (-1*stack_lay)
   if( pl > 0 ): pl = pl*(1-comissao)   # Desconta comissao
   sbl = stack_back + stack_lay
   mundo.recebeAtualizacao(odd=odd_favorito, minuto=qtd_min, winLose=win_lose)
   
print("Mundo=", mundo) 
#lucro_medio = round( (100.0*soma_pl/soma_stack) ,4)
#print( "Total de partidas=", total_partidas, ", lucro total=", soma_pl, ", stake total=", soma_stack, ", lucro medio=", lucro_medio )