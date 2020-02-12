import sqlite3
import copy
from datetime import datetime, timedelta
import time
import operator
from simulamc import MeioAmbiente, AgenteApostadorCavalo, AgenteEspeculadorCavalo, MeioAmbienteNeural, AgenteNEAT
import neat # pip install neat-python
import os
import pickle
from math import log # Log base natural mesmo

qtd_corridas_treino = 30000
qtd_corridas_validacao = 3535
qtd_geracoes = 9

def relu(input):
   if input > 0:
      return input
   else:
      return 0

def validaModelo(nome_picke, config_file, qtd_corridas):
   print("Bora validar!")
   file = open(nome_picke, 'rb')
   winner = pickle.load(file)
   file.close()
   
   #print('\nBest genome:\n{!s}'.format(winner))
   
   print("Fitness anterior=", winner.fitness)
   #print("Index=", winner.key)
   
   config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
               neat.DefaultSpeciesSet, neat.DefaultStagnation,
               config_file)
   
   # Reiniciando os itens
   net = neat.nn.FeedForwardNetwork.create(winner, config)
   agente = AgenteNEAT()
   
   # Agora simular
   corridas = obtemCorridasAleatorias(qtd_corridas = qtd_corridas_validacao)
   for corrida in corridas:
      processaOddsMundo(race_id=corrida, nets=[net,], agentes=[agente,], ge=[winner,] )
      [a.novaCorrida() for a in [agente,] ] # Agora pode apostar
      
   print("Fitness posterior=", winner.fitness)
   print("Apostas feitas=", agente.idade )
   print("Patrimonio final=", agente.patrimonio )

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
   corridaJaFoi = None
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
      if row == None: 
         #print("Idade=", agentes[0].idade, ", Patrimonio=", agentes[0].patrimonio )
         break  # Acabou o sqlite
      start = time.process_time() # Liga relogio
      race_id, market_time, inplay_timestamp, market_name, market_venue, runner_id, nome_cavalo, win_lose, bsp, odd, data = row
      if( race_id not in lista_corridas ): 
         #print("Corrida nova!")
         lista_corridas[race_id], lista_bsp[race_id], lista_wl[race_id]  = obtemParticipantesDeCorrida(race_id)
         corridaJaFoi = False
         #mundo.notificaNovaCorrida(race_id)   # Se preparem para apostar
      delta = datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') - datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
      qtd_min = ((delta.seconds) // 60)
      #print('Segundos=', ((delta.seconds) // 1), 'Minutos=', ((delta.seconds) // 60), 'd1=', market_time, 'd2=', data )
      #print("DBG=", race_id, market_time, inplay_timestamp, market_name, market_venue, runner_id, nome_cavalo, win_lose, bsp, odd, data)
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
      #print("X=", melhores_odds , " e todos=", list(lista_corridas_ordenado.items()) )
      #print(melhores_odds[0][0], melhores_odds[1][0], melhores_odds[2][0] ) # Nomes
      
      for x, agente in enumerate(agentes):
         ge[x].fitness -= 1 # Desconta sempre
         if( agente.estouVivo() == False ): # Morreu
            #print("MURRIO!")
            ge[x].fitness -= 5000 # Por ter morrido
            nets.pop(agentes.index(agente)) # Remove rede
            ge.pop(agentes.index(agente)) # Remove genoma
            agentes.pop(agentes.index(agente)) # Remove agente
         else:
            #ge[x].fitness += agente.lucro_medio # O que tem de retorno eh fitness
            #if( agente.lucro_medio == 0  ): ge[x].fitness -= 1 # Tem de ser ousado
            #agente.move()
            if( len(melhores_odds) < 3 ) : break #print("Deu merda!")
            if( qtd_min > 60 or qtd_min < 1 ): break # Apenas uma hora antes
            if( corridaJaFoi == True ): break # Aposta apenas uma vez por corrida
            if( agente.jaApostei == True ): break # Ja apostei
            corridaJaFoi = True
            #print("DBG=", race_id, market_time, inplay_timestamp, market_name, market_venue, runner_id, nome_cavalo, win_lose, bsp, odd, data, qtd_min, corridaJaFoi)
            idx_qtd_min = 1.0*qtd_min/60 # Entre 0 e 1
            prob1 = 1.0/melhores_odds[0][1]
            prob2 = 1.0/melhores_odds[1][1]
            prob3 = 1.0/melhores_odds[2][1]
            #print("Entrada=", idx_qtd_min, prob1, prob2, prob3 )
            output = nets[agentes.index(agente)].activate((idx_qtd_min, prob1, prob2, prob3 ))
            devoFazerBack = output[0] # Se ativado, faco aposta Back no favorito
            #frac_apos = output[1] # Fracao a ser apostada no Back no favorito
            frac_apos = 1.0
            #print("Saida=", output, agente.idade)
            if devoFazerBack > 0.5 and frac_apos > 0:
               nome_melhor = melhores_odds[0][0] # O com menor odd
               odds_cavalo1 = melhores_odds[0][1] # Cavalo com menor odd
               #stack_back = agente.patrimonio * frac_apos
               stack_back = 20
               pl_back = agente.fazApostaBack(odd_back=odds_cavalo1, stack_back=stack_back, wl_back=lista_wl[race_id][nome_melhor], fracao_aposta=frac_apos )
               if( pl_back is not None ):
                  #print("minutos=", qtd_min, " race=", race_id )
                  agente.patrimonio += pl_back
                  #ge[x].fitness += agente.patrimonio # Quanto mais, melhor
                  if( agente.pat_ant > agente.patrimonio ): ge[x].fitness -= 3 # Ruim, ruim
                  else: ge[x].fitness += 1 # Bom, bom
                  if( agente.lucro_medio < 0 ): ge[x].fitness -= 3 # Ruim, ruim
                  else: ge[x].fitness += 1 # Bom, bom
                  if( agente.relogio > 10 and agente.idx_aposta < 0.5) : ge[x].fitness -= 3
                  else: ge[x].fitness += 1 # Bom, bom
                  if( agente.idade == 0 ): ge[x].fitness -= 3 # Tem de apostar!
                  #print(", $$=", agente.patrimonio, " antes era=", agente.pat_ant, ", fit=", ge[x].fitness )
                  #input("Olha a grana.")
                  agente.cres_exp += log(1+ frac_apos*relu(pl_back) ) # Soma crescimento exponencial da banca
                  #ge[x].fitness += agente.cres_exp # Quanto mais, melhor
                  #ge[x].fitness += agente.patrimonio-1000 # Quanto mais, melhor
                  ge[x].fitness += pl_back # Retorninho
                  agente.idade += 1
                  agente.idx_aposta = 1.0*agente.idade/agente.relogio
                  agente.atualizaRetorno()
                  #ge[x].fitness = agente.cres_exp # O que cresce exponencialmente na banca eh fitness
                  #ge[x].fitness = agente.patrimonio
                  agente.jaApostei = True # Uma vez apenas
                  agente.pat_ant = agente.patrimonio # Para lembrar
      tempo_anterior = qtd_min
      odd_anterior = copy.deepcopy(lista_corridas[race_id])
      winLose_anterior = copy.deepcopy(lista_wl[race_id])
      bsp_anterior = copy.deepcopy(lista_bsp[race_id])

def obtemCorridasAleatorias(qtd_corridas):   
   lista_corridas = []
   conn = sqlite3.connect('bf_gb_win_full.db')
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
   corridas = obtemCorridasAleatorias(qtd_corridas = qtd_corridas_treino)
   for corrida in corridas:
      processaOddsMundo(race_id=corrida, nets=nets, agentes=agentes, ge=ge)
      [a.novaCorrida() for a in agentes] # Agora pode apostar
      
   # Mostra as minhas estatisticas, depois da corrida
   for x, agente in enumerate(agentes):
      print("Agente=", agente.nome, ", $=", round(agente.patrimonio,2), ", fit=", round(ge[x].fitness,4), ", idx=", round(agente.idx_aposta,4), ", apostas=", agente.idade, ", exp=", round(agente.cres_exp,2), ", ret=", round(agente.lucro_medio,2) )
   #input("Olha a tabela-->.")
      
def simula(config_file):
   #mundo = MeioAmbienteNeural(config_file)   # Crio mundo 
   #mundo.criaPopulacao()
   #mundo.criaReporterStdOut()
   config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
               neat.DefaultSpeciesSet, neat.DefaultStagnation,
               config_file)
   
   # Cria a populacao
   p = neat.Population(config)
   #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-9') # Se for o caso continua
   
   # Extraindo algum item que eu queira (tipo ID=36 nesse caso)
   #for x in p.population:
   #   print("P=", x, p.population[x].fitness )
   #parece_boa = p.population[29] # Meio que se mantem de boas
   #with open('candidato.pkl', 'wb') as output:
   #   pickle.dump(parece_boa, output, 1) # Salva o vencedor
   #x  = 1/0
   
   # Cria um Reporter StdOut
   p.add_reporter(neat.StdOutReporter(show_species_detail=False)) # Se True mostra aquela tabela por especie
   stats = neat.StatisticsReporter()
   p.add_reporter(stats)
   ckpoint = neat.Checkpointer(generation_interval=5, filename_prefix='neat-checkpoint-') #generation_interval=100, time_interval_seconds=300, filename_prefix='neat-checkpoint-'
   p.add_reporter(ckpoint) 
   
   # Executa 50 geracoes
   #winner = p.run(avalia_genomas, qtd_geracoes)

   #if resume == True: 
   #p = neat.Checkpointer.restore_checkpoint(restore_file) # Se for o caso continua
   #p = neat.Checkpointer.restore_checkpoint( 'neat-checkpoint-4' ) # Carregar o checkpoint
   winner = p.run( avalia_genomas , qtd_geracoes ) # Aqui tem de simular
   
   # Depois do treino, hora de salvar o campeao
   with open('vencedor.pkl', 'wb') as output:
      pickle.dump(winner, output, 1) # Salva o vencedor

if __name__ == '__main__':
   local_dir = os.path.dirname(__file__)
   config_path = os.path.join(local_dir, 'config-feedforward.txt')
   simula(config_path)
   validaModelo(nome_picke='vencedor.pkl', config_file=config_path, qtd_corridas=qtd_corridas_validacao)