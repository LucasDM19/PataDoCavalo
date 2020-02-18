#coding: utf-8
import neat # pip install neat-python
import os
import pickle
import math
import visualize # arquivo vizualize.py

gen = 0

# Classe que utiliza rede neural
def relu(input):
   if input > 0:
      return input
   else:
      return 0

# Calcula indice de Sharpe
def calc_sharpe(lista_retornos):
   soma = sum(lista_retornos)
   qtd_itens = len(lista_retornos)
   media = 1.0*soma/qtd_itens
   desvios = [ (r - media)**2 for r in lista_retornos]
   desvpad = ( sum(desvios)/len(desvios) )**0.5
   sh = media/desvpad
   return sh
      
import random, string
from math import log # Log base natural mesmo
from statistics import mean, stdev
from decimal import Decimal
class AgenteNEAT:
   def __init__(self):
      self.iniciaMindset()
      
   def iniciaMindset(self):
      self.nome = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))   # Uma cadeia de letras e numeros de tamanho 10
      self.patrimonio = 1000.0   # Mil doletas
      self.somaStack = 0.0 # Capital de giro
      self.lucro_medio = 0.0 # Retorno do investimento
      self.idade = 0 # Um bebezito
      self.cres_exp = 0.0 # Crescimento exponencial da banca
      self.pat_ant = self.patrimonio # Ve como estava de grana antes
      self.jaApostei = False
      self.relogio = 1 # Contabiliza ciclos
      self.idx_aposta = 0.0 # Quanto ele aposta
      self.pl_hist = [] # Histórico dos retornos - sharpe
      self.sharpe = 0.0 # Índice de Sharpe (Média/Desv_Pad dos retornos)
   
   def novaCorrida(self):
      self.jaApostei = False
      self.relogio += 1 # Contabiliza que essa corrida chegou para ele
      if( self.relogio != 0 ): self.idx_aposta = 1.0*self.idade/self.relogio
   
   def estouVivo(self):
      if( self.patrimonio <= 0 ): return False
      return True
   
   #def atualizaRetornos(self):
      #if( self.somaStack != 0 ): self.lucro_medio = 1.0*(self.patrimonio-1000.0)/self.somaStack
      #if( self.relogio != 0 ): self.idx_aposta = 1.0*self.idade/self.relogio
      
   # Faz apenas Back
   def fazApostaBack(self, odd_back, stack_back, wl_back, fracao_aposta=1.0, comissao = 0.065):
      #stack_back *= fracao_aposta # Aposto uma determinada fracao do Stack
      if( stack_back < 2 ): return None # Sem condicao
      if( wl_back == 0 ): 
         pl_back = (-1*stack_back) 
      elif( wl_back == 1 ): 
         pl_back = stack_back*(odd_back)-stack_back
      else: return None # WL invalido nao conta
      if( pl_back > 0 ): 
         pl_back = pl_back*(1-comissao)
      self.somaStack += stack_back
      self.cres_exp += log(1+ fracao_aposta*relu(pl_back) ) # Soma crescimento exponencial da banca
      self.patrimonio += pl_back
      self.idade += 1
      if( self.relogio != 0 ): self.idx_aposta = 1.0*self.idade/self.relogio
      if( self.somaStack != 0 ): self.lucro_medio = 1.0*(self.patrimonio-1000.0)/self.somaStack
      #self.pl_hist.append( Decimal(pl_back) )
      #if( len(self.pl_hist) > 1 ): self.sharpe = float( mean(self.pl_hist)/stdev(self.pl_hist) )
      #if( len(self.pl_hist) > 1 ): self.sharpe = calc_sharpe(self.pl_hist)
      #print("Aposta back ", round(stack_back,2) ," na odd ", odd_back , " teve PL=", round(pl_back,2), " e WL=", wl_back, ", frac=", round(fracao_aposta,2) )   
      #input("Teve aposta.")      
      #if( self.somaStack != 0 ): print("Pat depois=", self.lucro_medio, " $=", self.patrimonio, " SS=", self.somaStack )
      return pl_back
      
   # Faz apenas Lay
   def fazApostaLay(self, odd_lay, stack_lay, wl_lay, fracao_aposta=1.0, comissao = 0.065):
      #stack_lay *= fracao_aposta # Aposto uma determinada fracao do Stack
      if( stack_lay < 2 ): return 0 # Sem condicao
      if( wl_lay == 0 ): 
         pl_lay = (+1*stack_lay)
      elif( wl_back == 1 ): 
         pl_lay = (-1*(stack_lay*(odd_lay-1)))
      else: return 0 # WL invalido nao conta
      if( pl_lay > 0 ): 
         pl_lay = pl_lay*(1-comissao)
      self.somaStack += stack_lay
      #print("Aposta lay ", stack_lay ," na odd ", odd_lay , " teve PL=", round(pl_lay,2), " e WL=", wl_lay, ", frac=", fracao_aposta )
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

import sqlite3
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

from datetime import datetime, timedelta
import operator
class AmbienteDaCorrida:
   """
   Representa as restrições, regras e conversões dos dados para simular uma quase API da BetFair
   """
   def __init__(self):
      self.lista_corridas = {} # Cada corrida tem uma lista de cavalos
      self.lista_bsp = {} # Para saber qual eh o BSP correspondente
      self.lista_wl = {} # Para saber quem foi Win e quem foi Lose
      
   def atualizaDados(self, row):
      bd = BaseDeDados()
      bd.nomeBD = 'bf_gb_win_full.db'
      if( row is None ): return None
      self.race_id, market_time, inplay_timestamp, market_name, market_venue, runner_id, nome_cavalo, win_lose, bsp, odd, data = row
      if( self.race_id not in self.lista_corridas ): 
         self.lista_corridas[self.race_id], self.lista_bsp[self.race_id], self.lista_wl[self.race_id] = bd.obtemParticipantesDeCorrida(self.race_id)
      delta = datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') - datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
      qtd_min = ((delta.seconds) // 60)
      if( datetime.strptime(data, '%Y-%m-%d %H:%M:%S') > datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') ) : # Corrida em andamento
         delta = (datetime.strptime(data, '%Y-%m-%d %H:%M:%S') - datetime.strptime(market_time, '%Y-%m-%dT%H:%M:%S.000Z') )
         qtd_min = -1 * ((delta.seconds) // 60)
      self.lista_corridas[self.race_id][nome_cavalo] = odd #Atualiza as odds dessa corrida
      self.lista_bsp[self.race_id][nome_cavalo] = bsp # Sabendo o BSP do cavalo
      self.lista_wl[self.race_id][nome_cavalo] = win_lose # Sabendo o Win/Lose do cavalo
      #favorito = min( lista_corridas[race_id], key=lista_corridas[race_id].get ) # Nome do cavalo com menor odd
      #odd_favorito = lista_corridas[race_id][favorito]
      #bsp_favorito = lista_bsp[race_id][favorito]
      #wl_favorito = lista_wl[race_id][favorito]
      lista_corridas_ordenado = dict( sorted( self.lista_corridas[self.race_id].items(), key=operator.itemgetter(1),reverse=False ) ) # Mostra igual no site. Odds menores primeiro.
      self.melhores_odds = list(lista_corridas_ordenado.items())[0:3] # Top 3 odds
      
      if( len(self.melhores_odds) < 3 ) : return None #print("Deu merda!")
      if( qtd_min > 60 or qtd_min < 1 ): return None # Apenas uma hora antes
      #if( corridaJaFoi == True ): return None # Aposta apenas uma vez por corrida
      
      idx_qtd_min = 1.0*qtd_min/60 # Entre 0 e 1
      prob1 = 1.0/self.melhores_odds[0][1]
      prob2 = 1.0/self.melhores_odds[1][1]
      prob3 = 1.0/self.melhores_odds[2][1]
      return idx_qtd_min, prob1, prob2, prob3
   
def eval_genomes(genomes, config):
   """
   executa a simulação da população atual de 
   agentes e define seus fitness com base no progresso financeiro
   que eles atingem durante as corridas.
   """
   global gen
   gen += 1
   
   # Começa criando listas que determinam o genoma em si, 
   # a rede neural associada com o genoma e 
   # o objeto de agente apostador que usa essa rede para jogar
   nets = [] # Redes
   agentes = [] # Agentes apostadores
   ge = [] # Genomas
   for genome_id, genome in genomes:
      genome.fitness = 0  # Começa com nível de fitness de 0
      net = neat.nn.FeedForwardNetwork.create(genome, config)
      nets.append(net)
      agente = AgenteNEAT()
      agentes.append(agente)
      ge.append(genome)
      
   banco = BaseDeDados()
   banco.conectaBaseDados('bf_gb_win_full.db')
   corrida = AmbienteDaCorrida()
      
   score = 0 # Será que precisa?
   run = True # Para o "jogo financeiro"
   while run and len(agentes) > 0: # Enquanto o jogo não acaba e enquanto tem apostadores
      #clock.tick(30) Contabilizo corridas?
      
      for x, agente in enumerate(agentes):
         #ge[x].fitness -= 0.1 # Punição para estimular a aposta
         if( agente.estouVivo() == False or agente.patrimonio < 10 or agente.idx_aposta < 0.5 or math.isnan(round(agente.patrimonio,2)) or agente.lucro_medio < 0 ): # Morreu ou quase falido
            #print("MURRIO!", agente.nome )
            ge[x].fitness -= 5000 # Por ter morrido
            nets.pop(agentes.index(agente)) # Remove rede
            ge.pop(agentes.index(agente)) # Remove genoma
            agentes.pop(agentes.index(agente)) # Remove agente
      
      corridas = banco.obtemCorridasAleatorias(1) # Apenas uma corrida por enquanto
      [a.novaCorrida() for a in agentes] # Agora pode apostar
      nova_corrida = corridas[0] # Retorna apenas um id de corrida
      banco.efetuaConsultaCorrida(nova_corrida) # Faço a Query
      row = ""
      while row is not None:
         row = banco.proximoRegistroCorrida() # Proxima Odd
         retorno = corrida.atualizaDados(row)
         if( retorno is not None ):
            idx_qtd_min, prob1, prob2, prob3 = retorno
            
            for x, agente in enumerate(agentes):
               output = nets[agentes.index(agente)].activate((idx_qtd_min, prob1, prob2, prob3 ))
               for y, saida in enumerate(output): # Para cada neuronio de saida
                  if( saida > 0):
                     frac_apos = saida
                     stack_back = agente.patrimonio * frac_apos / len(output) # Fração para apostar
                     nome_melhor = corrida.melhores_odds[y][0]
                     odds_cavalo = corrida.melhores_odds[y][1]
                     pl_back = agente.fazApostaBack(odd_back=odds_cavalo, stack_back=stack_back, wl_back=corrida.lista_wl[corrida.race_id][nome_melhor], fracao_aposta=frac_apos )
                     if( pl_back is not None ): 
                        #agente.atualizaRetornos()
                        ge[x].fitness += pl_back # O importante é ficar positivo
      
      for x, agente in enumerate(agentes):
         if( agente.relogio > 10000 ):
            with open('winner10_'+agente.nome+'.pkl', 'wb') as output:
               pickle.dump(ge[x], output, 1)

      
      # Mostra o estado de todos os agentes   
      for x, agente in enumerate(agentes):
         print("Geração", gen, "Agente=", agente.nome, ", $=", round(agente.patrimonio,2), ", fit=", round(ge[x].fitness,4), ", idx=", round(agente.idx_aposta,4), ", apostas=", agente.idade, ", corridas=", agente.relogio, ", exp=", round(agente.cres_exp,2), ", ret=", round(agente.lucro_medio,4) )
      #x = 1/0
   
   
def run(config_file):
   """
   roda o algoritmo NEAT para treinar uma rede neural para apostar em corridas de cavalo.
   :param config_file: localização do arquivo de configuração
   :return: None
   """
   config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation,
            config_file)
            
   # Cria a população, que é o objeto de máximo nível para um run NEAT.
   p = neat.Population(config)
   
   # Adiciona um reporter stdout para mostrar o progresso no terminal.
   p.add_reporter(neat.StdOutReporter(show_species_detail=False)) # Se True mostra aquela tabela por especie
   stats = neat.StatisticsReporter()
   p.add_reporter(stats)
   #ckpoint = neat.Checkpointer(generation_interval=5, filename_prefix='neat-checkpoint-') #generation_interval=100, time_interval_seconds=300, filename_prefix='neat-checkpoint-'
   #p.add_reporter(ckpoint)
   
   # Executa até 50 gerações.
   winner = p.run(eval_genomes, 1)
   
   # Exibe as estatísticas finais
   print('\nMelhor genoma:\n{!s}'.format(winner))
   
   with open('vencedor.pkl', 'wb') as output:
      pickle.dump(winner, output, 1) # Salva o vencedor
      
   node_names = {-1:'Input1', -2: 'Input2', -3:'Input3', -4:'Input4', 0:'Output1', 1:'Output2'}
   visualize.draw_net(config, winner, True, node_names=node_names)
   visualize.plot_stats(stats, ylog=False, view=True)
   visualize.plot_species(stats, view=True)

if __name__ == '__main__':
   local_dir = os.path.dirname(__file__)
   config_path = os.path.join(local_dir, 'config-feedforward.txt')
   run(config_path)