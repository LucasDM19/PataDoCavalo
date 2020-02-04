import sqlite3
import copy
from datetime import datetime, timedelta
import time
import operator
from simulamc import MeioAmbiente, AgenteApostadorCavalo, AgenteEspeculadorCavalo, MeioAmbienteNeural, AgenteNEAT
import neat # pip install neat-python
import os

def obtemParticipantesDeCorrida(race_id):
   lista_participantes = {}
   lista_bsp = {}
   lista_wl = {}
   conn = sqlite3.connect('bf_gb_win_full.db')
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

def processaOddsMundo(race_id, nets, agentes, ge):
   lista_corridas = {} # Cada corrida tem uma lista de cavalos
   lista_bsp = {} # Para saber qual eh o BSP correspondente
   lista_wl = {} # Para saber quem foi Win e quem foi Lose
   tempo_anterior = -999 # Para deixar a fita temporal coerente
   odd_anterior = {}
   winLose_anterior = {}
   bsp_anterior = {}
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
        AND races.RaceId = ?
        and (races.RaceId <> "1.159938420" AND races.RaceId <> "1.160357774" AND races.RaceId <> "1.160357775" AND races.RaceId <> "1.160934216" AND races.RaceId <> "1.162266316" AND races.RaceId <> "1.165629272")
        AND runners.BSP <> -1
        AND runners.WinLose <> -1
      ORDER BY races.RaceId, odds.PublishedTime ASC """, (race_id,) )       
   while True: 
      row = c.fetchone()
      if row == None: break  # Acabou o sqlite
      start = time.process_time() # Liga relogio
      race_id, market_time, inplay_timestamp, market_name, market_venue, runner_id, nome_cavalo, win_lose, bsp, odd, data = row
      if( race_id not in lista_corridas ): 
         #print("Corrida nova!")
         lista_corridas[race_id], lista_bsp[race_id], lista_wl[race_id]  = obtemParticipantesDeCorrida(race_id)
         #mundo.notificaNovaCorrida(race_id)   # Se preparem para apostar
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
      lista_corridas_ordenado = dict( sorted( lista_corridas[race_id].items(), key=operator.itemgetter(1),reverse=False ) ) # Mostra igual no site. Odds menores primeiro.
      #print("silencio da fita:", [qm for qm in range(tempo_anterior-1,qtd_min,-1)])
      #if (len([qm for qm in range(tempo_anterior-1,qtd_min,-1)]) != 0 ): x = 1/0
      #print("Minutos de silencio, ant=", odd_anterior, ", atu=", lista_corridas[race_id])
      #[mundo.recebeAtualizacao(odd=odd_anterior, minuto=qm, winLose=winLose_anterior, bsp=bsp_anterior, race_id=race_id) for qm in range(tempo_anterior-1,qtd_min,-1)  ]
      #print("Fita normal, ant=", odd_anterior, ", atu=", lista_corridas[race_id])
      #mundo.recebeAtualizacao(odd=lista_corridas[race_id], minuto=qtd_min, winLose=lista_wl[race_id], bsp=lista_bsp[race_id], race_id=race_id)
      
      melhores_odds = list(lista_corridas_ordenado.items())[0:3] # Top 3 odds
      #print("X=", lista_corridas_ordenado  )
      #print(melhores_odds[0][0], melhores_odds[1][0], melhores_odds[2][0] ) # Nomes
      
      for x, agente in enumerate(agentes):
         if( agente.estouVivo() == False ): # Morreu
            #print("MURRIO!")
            ge[x].fitness -= 5 # Por ter morrido
            nets.pop(agentes.index(agente)) # Remove rede
            ge.pop(agentes.index(agente)) # Remove genoma
            agentes.pop(agentes.index(agente)) # Remove agente
         else:
            #ge[x].fitness += agente.lucro_medio # O que tem de retorno eh fitness
            #if( agente.lucro_medio == 0  ): ge[x].fitness -= 1 # Tem de ser ousado
            #agente.move()
            if( len(melhores_odds) < 3 ) : break #print("Deu merda!")
            if( qtd_min > 60 ): break # Apenas uma hora antes
            idx_qtd_min = 1.0*qtd_min/60 # Entre 0 e 1
            prob1 = 1.0/melhores_odds[0][1]
            prob2 = 1.0/melhores_odds[1][1]
            prob3 = 1.0/melhores_odds[2][1]
            #print("Entrada=", idx_qtd_min, prob1, prob2, prob3 )
            output = nets[agentes.index(agente)].activate((idx_qtd_min, prob1, prob2, prob3 ))
            
            #print("Saida=", output, agente.lucro_medio)
            if output[0] > 0.5:
               nome_melhor = melhores_odds[0][0] # O com menor odd
               pl_back = agente.fazApostaBack(odd_back=melhores_odds[0][1], stack_back=20.0, wl_back=lista_wl[race_id][nome_melhor] )
               agente.patrimonio += pl_back
               agente.atualizaRetorno()
               ge[x].fitness = agente.lucro_medio # O que tem de retorno eh fitness
      
      tempo_anterior = qtd_min
      odd_anterior = copy.deepcopy(lista_corridas[race_id])
      winLose_anterior = copy.deepcopy(lista_wl[race_id])
      bsp_anterior = copy.deepcopy(lista_bsp[race_id])
      #print("Demorou", time.process_time() - start)
      #if(time.process_time() - start > 0 ) : x = 1/0
      #print("Fim do ciclo - dados novos!")

def processaCorrida(qtd_corrdas, nets, agentes, ge):   
   conn = sqlite3.connect('bf_gb_win_full.db')
   c_corrida = conn.cursor()
   c_corrida.execute(""" SELECT * FROM races ORDER BY RANDOM() LIMIT ?; """, (qtd_corrdas,) )
   #print("Inicio do processamento")  
   while True: 
      row = c_corrida.fetchone()
      if row == None: break  # Acabou o sqlite
      race_id, market_time, inplay_timestamp, market_name, market_venue = row
      #print("Col=", row)
      processaOddsMundo(race_id, nets=nets, agentes=agentes, ge=ge)
   #mundo.exibeAgentes()

def avalia_genomas(genomes, config):
   nets = [] # Redes
   agentes = [] # Agentes apostadores
   ge = [] # Genomas
   for genome_id, genome in genomes:
      genome.fitness = 0  # O fitness comeca com 0
      net = neat.nn.FeedForwardNetwork.create(genome, config)
      nets.append(net)
      agente = AgenteNEAT()
      agentes.append(agente)
      ge.append(genome)
      
   # Agora os dados
   processaCorrida(qtd_corrdas = 5000, nets=nets, agentes=agentes, ge=ge)
      
def simula(config_file):
   #mundo = MeioAmbienteNeural(config_file)   # Crio mundo 
   #mundo.criaPopulacao()
   #mundo.criaReporterStdOut()
   config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
               neat.DefaultSpeciesSet, neat.DefaultStagnation,
               config_file)
   
   # Cria a populacao
   p = neat.Population(config)
   
   # Cria um Reporter StdOut
   p.add_reporter(neat.StdOutReporter(True))
   stats = neat.StatisticsReporter()
   p.add_reporter(stats)
   ckpoint = neat.Checkpointer(generation_interval=5, filename_prefix='neat-checkpoint-') #generation_interval=100, time_interval_seconds=300, filename_prefix='neat-checkpoint-'
   p.add_reporter(ckpoint) 
   
   # Executa 50 geracoes
   winner = p.run(avalia_genomas, 300)

if __name__ == '__main__':
   local_dir = os.path.dirname(__file__)
   config_path = os.path.join(local_dir, 'config-feedforward.txt')
   simula(config_path)