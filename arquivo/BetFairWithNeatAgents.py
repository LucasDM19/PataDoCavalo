#coding: utf-8
import neat # pip install neat-python
import os
import pickle
import math
import visualize # arquivo vizualize.py
from BDUtils import BaseDeDados

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
      self.max_patrimonio = self.patrimonio # Ve como estava de grana antes
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
      
   score = 0 # Será que precisa?
   run = True # Para o "jogo financeiro"
   while run and len(agentes) > 0: # Enquanto o jogo não acaba e enquanto tem apostadores
      
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
      minutosCorrida = banco.obtemMinutosDaCorrida(nova_corrida) # Quais minutos tem eventos registrado de odds
      
      for minuto in minutosCorrida:
         retorno = banco.obtemRegistroPorMinuto(minuto) # Todas as odds consolidadas
         if( retorno is not None ):
            idx_qtd_min, prob1, prob2, prob3 = retorno
            
            for x, agente in enumerate(agentes):
               output = nets[agentes.index(agente)].activate((idx_qtd_min, prob1, prob2, prob3 ))
               for y, saida in enumerate(output): # Para cada neuronio de saida
                  if( saida > 0):
                     frac_apos = saida
                     stack_back = agente.patrimonio * frac_apos / len(output) # Fração para apostar
                     nome_melhor = banco.melhores_odds[y][0]
                     odds_cavalo = banco.melhores_odds[y][1]
                     pl_back = agente.fazApostaBack(odd_back=odds_cavalo, stack_back=stack_back, wl_back=banco.lista_wl[banco.race_id][nome_melhor], fracao_aposta=frac_apos )
                     if( pl_back is not None ): 
                        #agente.atualizaRetornos()
                        #if( agente.patrimonio > agente.max_patrimonio ):
                           #ge[x].fitness += 1 # Bateu recorde, é bom
                           #agente.max_patrimonio = agente.patrimonio
                        ge[x].fitness = agente.relogio
      
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
   winner = p.run(eval_genomes, 1000)
   
   # Exibe as estatísticas finais
   print('\nMelhor genoma:\n{!s}'.format(winner))
   
   with open('vencedor.pkl', 'wb') as output:
      pickle.dump(winner, output, 1) # Salva o vencedor
      
   node_names = {-1:'Idx_Minutos', -2: 'Prob1', -3:'Prob2', -4:'Prob3', 0:'Frac_Back1', 1:'Frac_Back2', 2:'Frac_Back3' }
   visualize.draw_net(config, winner, True, node_names=node_names)
   visualize.plot_stats(stats, ylog=False, view=True)
   visualize.plot_species(stats, view=True)

if __name__ == '__main__':
   local_dir = os.path.dirname(__file__)
   config_path = os.path.join(local_dir, 'config-feedforward.txt')
   run(config_path)