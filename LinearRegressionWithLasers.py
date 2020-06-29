#coding: utf-8
from BDUtils import BaseDeDados
from datetime import datetime
import pandas as pd
import numpy as np
import random
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from CorridaUtils import obtemDistanciaDaPista, obtemCaracteristicasDaCorrida

def obtemExtremosDistancias(nomes_mercados):
   #for punm in nomes_mercados:
      #dist = obtemDistanciaDaPista( punm )
      #if( dist is not None ): print("Termo=", punm, " distancia", str(dist) )
   dist_maxima = max([ obtemDistanciaDaPista(nm) for nm in nomes_mercados  if obtemDistanciaDaPista(nm) is not None] )
   dist_minima = min([ obtemDistanciaDaPista(nm) for nm in nomes_mercados  if obtemDistanciaDaPista(nm) is not None] )
   return dist_maxima, dist_minima

# Só para manter o backup
def coletaInformacoesSobreCorridas():
   nomes_mercados = banco.obtemNomesDosMercados()
   for nm in nomes_mercados:
      lista = obtemCaracteristicasDaCorrida(nm)
   dist_maxima, dist_minima = obtemExtremosDistancias(nomes_mercados)
   print("Distância Máxima:", dist_maxima, ", distância mínima:", dist_minima)

def fazApostaBack(odd_back, stack_back, wl_back, comissao = 0.065):
   if( stack_back < 2 ): return None # Sem condicao
   if( wl_back == -1 ): return 0.0 # Cavalo eliminado, aposta devolvida
   if( wl_back == 0 ): 
      pl_back = (-1*stack_back) 
   elif( wl_back == 1 ): 
      pl_back = stack_back*(odd_back)-stack_back
   if( pl_back > 0 ): 
      pl_back = pl_back*(1-comissao)
   return pl_back
   
def fazApostaLay(odd_lay, stack_lay, wl_lay, comissao = 0.065):
   if( stack_lay < 2 ): return 0 # Sem condicao
   if( wl_lay == -1 ): return 0.0 # Cavalo eliminado, aposta devolvida
   if( wl_lay == 0 ): 
      pl_lay = (+1*stack_lay)
   elif( wl_lay == 1 ): 
      pl_lay = (-1*(stack_lay*(odd_lay-1)))
   if( pl_lay > 0 ): 
      pl_lay = pl_lay*(1-comissao)
   return pl_lay

class Estrategia():
   def __init__(self, nome, min_back, min_lay, max_cavalo):
      self.nome = nome
      self.min_back = min_back
      self.min_lay = min_lay
      self.max_cavalo = max_cavalo
      self.saldo = 1000
      self.total_back = 0
      self.total_lay = 0
   def __str__(self):
      return "nome=" + str(self.nome)+ ", ret_unit=" + str(round(self.ret_unit,6)) + ", saldo=" + str(round(self.saldo,2)) + ", min_back=" + str(self.min_back) + ", min_lay=" + str(self.min_lay) + ", max_cavalo=" + str(self.max_cavalo) + ", qtd_back=" + str(self.total_back) + ", qtd_lay=" + str(self.total_lay)

def fazProspeccaoEstrategias(min_minutos_back = 1, max_minutos_back = 60, min_minutos_lay = 1, max_minutos_lay = 60, max_cavalos = 3): # Demora cerca de 42 horas na configuração padrão
   banco = BaseDeDados()
   banco.conectaBaseDados('bf_gb_win_47k.db')
   estrategias = []
   contador_id = 0
   for minutos1 in range(min_minutos_back,max_minutos_back+1):
      for minutos2 in range(min_minutos_lay,max_minutos_lay+1):
         for tantos_cavalos in range(max_cavalos):
            est = Estrategia(nome=contador_id, min_back=minutos1, min_lay=minutos2, max_cavalo=tantos_cavalos)
            estrategias.append(est)
            contador_id += 1
   print("Estratégias=", len(estrategias))
   
   menor_valor = min(min_minutos_back, min_minutos_lay)
   maior_valor = max(max_minutos_back, max_minutos_lay)
   #valores_minuto = range(menor_valor, maior_valor+1) 
   valores_minuto = [26,]
   for minuto in valores_minuto:
      print("Minuto=", minuto, ", são=", datetime.now().time())
      retorno = banco.obtemRetornoDaCorrida(minuto)
      if( retorno is not None ):
         dic_winLose = retorno # dic_winLose[0] ou dic_winLose[1]. O -1 deixa para lá
         estrats_back = [e for e in estrategias if e.min_back == minuto] # Estratégias que fariam Back nesse minuto
         for eb in estrats_back:
            comissao = 0.065
            for wl_back in dic_winLose.keys():
               pl_back = None
               soma_apostada = dic_winLose[wl_back][0]
               qtd_apostada = dic_winLose[wl_back][1]
               soma_stack = dic_winLose[wl_back][2]
               #stack_back = 20*round(soma_stack,2) # Stack proporcional, para lay?
               stack_back = 1
               if( wl_back == -1 ): 
                  pl_back = 0.0 # Cavalo eliminado, aposta devolvida
               elif( wl_back == 0 ): 
                  pl_back = (-1*stack_back*qtd_apostada ) 
               elif( wl_back == 1 ): 
                  pl_back = stack_back*(soma_apostada-qtd_apostada)
               if( pl_back > 0 ): 
                  pl_back = pl_back*(1-comissao)
               if(pl_back is not None):
                  eb.total_back += qtd_apostada
                  eb.saldo += pl_back
                  el.ret_unit = el.saldo/(el.total_back+el.total_lay)
         estrats_lay = [e for e in estrategias if e.min_lay == minuto] # Estratégias que fariam Lay nesse minuto
         for el in estrats_lay:
            comissao = 0.065
            for wl_lay in dic_winLose.keys():
               pl_lay = None
               soma_apostada = dic_winLose[wl_lay][0]
               qtd_apostada = dic_winLose[wl_lay][1]
               soma_stack = dic_winLose[wl_lay][2]
               stack_lay = 1*round(soma_stack,2) # Stack proporcional, já somado
               if( wl_lay == -1 ): pl_lay = 0.0 # Cavalo eliminado, aposta devolvida
               elif( wl_lay == 0 ): 
                  pl_lay = +1*stack_lay
               elif( wl_lay == 1 ): 
                  pl_lay = (-1*(qtd_apostada)) # Se for stack proporcional. S*(o-1)=1, pois S=1/(o-1)
               if( pl_lay > 0 ): 
                  pl_lay = pl_lay*(1-comissao)
               if(pl_lay is not None):
                  el.total_lay += qtd_apostada
                  el.saldo += pl_lay
                  el.ret_unit = el.saldo/(el.total_back+el.total_lay)
               print("Lay=", wl_lay, dic_winLose[wl_lay], pl_lay, el.saldo, el.total_lay, el.ret_unit)
   
   newlist = sorted(estrategias, key=lambda x: x.ret_unit, reverse=True) # Ordeno a lista de acordo com o saldo
   with open('estrategias.txt', 'w') as f:
      for item_es in newlist: 
         f.write("%s\n" % str(item_es))
    
   

   x = 1/0
   
   data_inicial, data_final, total_corridas = banco.obtemSumarioDasCorridas()
   corridas = banco.obtemCorridas(qtd_corridas=total_corridas, ordem="ASC") # ASC - Antigas primeiro, DESC - Recentes primeiro
   #corridas = ['1.123344088',]
   for corrida in corridas:
      print("Corrida=", corrida, ", são=", datetime.now().time() )
      minutosCorrida = banco.obtemMinutosDaCorrida(corrida) # Quais minutos tem eventos registrado de odds
      #if(len(minutosCorrida) != 0): todos_minutos = range(max(minutosCorrida),min(minutosCorrida)-1,-1) 
      #else: todos_minutos = []
      melhores_odds = None # Reference before assinigment
      for em in estrategias:
         minuto = em.min_back
         retorno = banco.obtemOddsPorMinuto(minuto) # Todas as odds consolidadas
         if( retorno is not None ):
            lista_ordenada = retorno # Obtenho lista ordenada das odds dos cavalos participantes
            melhores_odds = list(lista_ordenada.items())
            #print("Odds=", len(melhores_odds), "cavalo=", em.max_cavalo)
            if( len(melhores_odds) > em.max_cavalo  ): # Não tem cavalo suficiente para essa estratégia
               for y in range(em.max_cavalo+1):
                  nome_melhor = melhores_odds[y][0]
                  odds_cavalo_back = melhores_odds[y][1]
                  d = 0 # Deslocamento
                  while( odds_cavalo_back == -1.01 and d < len(melhores_odds) ):
                     nome_melhor = melhores_odds[y+d][0]
                     odds_cavalo_back = melhores_odds[y+d][1]
                     d += 1
                     #print("Alternativo", nome_melhor, odds_cavalo_back)
                  #stack_back = 20*round(1/(odds_cavalo_back-1),2) # Stack proporcional, para lay?
                  stack_back = 20
                  pl = fazApostaBack(odd_back=odds_cavalo_back, stack_back=stack_back, wl_back=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)                  
                  if(pl is not None): 
                     em.total_back += 1
                     em.saldo += pl
                  #print("Aposta Back retornou=", pl, ", ", str(em), ", minuto=", minuto, ", odds=", odds_cavalo, ", W/L=", banco.obtemWinLoseAtual(nome_melhor) )
            
         minuto = em.min_lay   
         retorno = banco.obtemOddsPorMinuto(minuto) # Todas as odds consolidadas
         if( retorno is not None ):
            lista_ordenada = retorno # Obtenho lista ordenada das odds dos cavalos participantes
            melhores_odds = list(lista_ordenada.items())
            if( len(melhores_odds) > em.max_cavalo  ): # Não tem cavalo suficiente para essa estratégia
               for y in range(em.max_cavalo+1):
                  nome_melhor = melhores_odds[y][0]
                  odds_cavalo_lay = melhores_odds[y][1]
                  d = 0 # Deslocamento
                  while( odds_cavalo_lay == -1.01 and d < len(melhores_odds) ):
                     nome_melhor = melhores_odds[y+d][0]
                     odds_cavalo_lay = melhores_odds[y+d][1]
                     d += 1
                     #print("Alternativo", nome_melhor, odds_cavalo_lay)
                  stack_lay = 20*round(1/(odds_cavalo_lay-1),2) # Stack proporcional
                  pl = fazApostaLay(odd_lay=odds_cavalo_lay, stack_lay=stack_lay, wl_lay=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)
                  if(pl is not None): 
                     em.total_lay += 1
                     em.saldo += pl  
                  #print("Aposta Lay retornou=", pl, ", ", str(em), ", minuto=", minuto, ", odds=", odds_cavalo, ", W/L=", banco.obtemWinLoseAtual(nome_melhor) )                  
   newlist = sorted(estrategias, key=lambda x: x.saldo, reverse=True) # Ordeno a lista de acordo com o saldo
   for item_es in newlist: 
      print("Esse:", str(item_es) )

def salvaRegistro(dados_corrida, nomes_colunas, campo, nome_campo):
   if( campo is None ):
      campo = 0.0 # Valor padrão #return dados_corrida, nomes_colunas # Sem nada para fazer
   dados_corrida.append(campo)
   if(len(dados_corrida) > len(nomes_colunas) ): 
      nomes_colunas.append(nome_campo) # Nome do campo
   return dados_corrida, nomes_colunas

def avaliaLay(minutos_lay, qtd_cavalos, banco, pl_total, total_stack):
   odds_cavalo_lay = None
   nome_melhor = None

   retorno = banco.obtemOddsPorMinuto(minutos_lay)
   if( retorno is not None ): # Tem realmente algo naqueles minutos
     lista_ordenada = retorno # Obtenho lista ordenada das odds dos cavalos participantes
     melhores_odds = list(lista_ordenada.items())
     #qtd_cavalos_corrida = len(melhores_odds)
     if( len(melhores_odds) > qtd_cavalos  ): # Não tem cavalo suficiente para essa estratégia
       for y in range(qtd_cavalos):
          nome_melhor = melhores_odds[y][0]
          odds_cavalo_lay = melhores_odds[y][1]
          d = 0 # Deslocamento
          while( odds_cavalo_lay == -1.01 and d < len(melhores_odds) ):
             nome_melhor = melhores_odds[y+d][0]
             odds_cavalo_lay = melhores_odds[y+d][1]
             d += 1
          stack_lay = 20*round(1/(odds_cavalo_lay-1),2) # Stack proporcional
          pl = fazApostaLay(odd_lay=odds_cavalo_lay, stack_lay=stack_lay, wl_lay=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)
          if(pl is not None): 
             if( pl_total is None ): 
                pl_total = pl # Primeira vez
                if( pl != 0 ): total_stack = stack_lay # Soma Stack apenas quando não devolve aposta
             else: 
                pl_total += pl # Concatena
                if( pl != 0 ): total_stack += stack_lay
          print("Aposta Lay retornou=", pl, ", minuto=", minutos_lay, ", odds=", odds_cavalo_lay, ", W/L=", banco.obtemWinLoseAtual(nome_melhor), ", stack=", stack_lay) #, "q_c=", qtd_cavalos_corrida )
   else:
      return None, None, None, None
   return pl_total, total_stack, odds_cavalo_lay, nome_melhor
   
def obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes):
   frac_odds_1h = None # Um padrão
   #Vendo como estava o mercado nos minutos Lay
   retorno1h = banco.obtemOddsPorMinuto(minuto_antes) # Mercado 1 hora atrás
   if( retorno1h is not None ):
      lista_ordenada1h = retorno1h
      melhores_odds1h = list(lista_ordenada1h.items())
   if( (retorno1h is None) or (nome_melhor is None) or (odds_cavalo_lay is None) ):
      return None
      
   for y in range(qtd_cavalos): # TODO: lidar com mais de um resultado ao mesmo tempo
      res_pesq = [melhores_odds1h[i][1] for i in range(len(melhores_odds1h)) if melhores_odds1h[i][0]==nome_melhor]
      if( len(res_pesq) >= 1 ): odds_cavalo_lay_1h = res_pesq[0] # Como estavam as odds 1 hora atrás
      else: odds_cavalo_lay_1h = 0.0 # Não teve nada
      frac_odds_1h = odds_cavalo_lay_1h / odds_cavalo_lay # Como evoluiu as odds             
      d = 0 # Deslocamento
      while( odds_cavalo_lay == -1.01 and d < len(melhores_odds) ):
         nome_melhor = melhores_odds[y+d][0]
         odds_cavalo_lay = melhores_odds[y+d][1]
         res_pesq = [melhores_odds1h[i][1] for i in range(len(melhores_odds1h)) if melhores_odds1h[i][0]==nome_melhor]
         if( len(res_pesq) >= 1 ): odds_cavalo_lay_1h = res_pesq[0] # Como estavam as odds 1 hora atrás
         else: odds_cavalo_lay_1h = 0.0 # Não teve nada
         frac_odds_1h = odds_cavalo_lay_1h / odds_cavalo_lay # Como evoluiu as odds  
         d += 1
   return frac_odds_1h
   
def obtemDadosTreinoDaEstrategia(minutos_back, minutos_lay, qtd_cavalos, frac_treino):
   banco = BaseDeDados()
   banco.conectaBaseDados('bf_gb_win_47k.db')
   data_inicial, data_final, total_corridas = banco.obtemSumarioDasCorridas()
   nomes_mercados = banco.obtemNomesDosMercados()
   dist_maxima, dist_minima = obtemExtremosDistancias(nomes_mercados) # Extremos de distâncias (se precisar de normatizar)
   qtd_corridas_treino = int(frac_treino * total_corridas) # Uso uma parte para treino. O resto é para validação
   #qtd_corridas_treino = 2 # Teste
   print("QTD=", qtd_corridas_treino, total_corridas )
   corridas = banco.obtemCorridas(qtd_corridas=qtd_corridas_treino, ordem="ASC") # ASC - Antigas primeiro, DESC - Recentes primeiro
   lista_treino = [] # Será uma lista de lista
   nomes_colunas = [] # Usa uma vez só
   for corrida in corridas:
      dados_corrida = [] # Linha sobre a corrida em si
      pl_total = None # Contabiliza o Back e o Lay como um só
      total_stack = None # Soma o Stack, para fazer retorno unitário
      pl_unitario = None # Retorno por unidade (item a ser maximizado)
      odds_cavalo_back = None
      print("Corrida=", corrida, ", são=", datetime.now().time() )
      minutosCorrida = banco.obtemMinutosDaCorrida(corrida) # Quais minutos tem eventos registrado de odds
      if(len(minutosCorrida) != 0): todos_minutos = range(max(minutosCorrida),min(minutosCorrida)-1,-1) 
      else: todos_minutos = []
      
      #Vendo como estava o mercado nos minutos Back
      retorno = banco.obtemOddsPorMinuto(minutos_back)
      if( retorno is not None ): # Tem realmente algo naqueles minutos
        lista_ordenada = retorno # Obtenho lista ordenada das odds dos cavalos participantes
        melhores_odds = list(lista_ordenada.items())
        if( len(melhores_odds) > qtd_cavalos  ): # Não tem cavalo suficiente para essa estratégia
          for y in range(qtd_cavalos):
             nome_melhor = melhores_odds[y][0]
             odds_cavalo_back = melhores_odds[y][1]
             d = 0 # Deslocamento
             while( odds_cavalo_back == -1.01 and d < len(melhores_odds) ):
                nome_melhor = melhores_odds[y+d][0]
                odds_cavalo_back = melhores_odds[y+d][1]
                d += 1
                #print("Alternativo", nome_melhor, odds_cavalo_lay)
             stack_back = 20*round(1/(odds_cavalo_back-1),2) # Stack proporcional
             pl = fazApostaBack(odd_back=odds_cavalo_back, stack_back=odds_cavalo_back, wl_back=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)                  
             if(pl is not None): 
                if( pl_total is None ): 
                   pl_total = pl # Primeira vez
                   if( pl != 0 ): total_stack = stack_back # Soma Stack apenas quando não devolve aposta
                else: 
                   pl_total += pl # Concatena
                   if( pl != 0 ): total_stack += stack_back
             #print("Aposta Back retornou=", pl, ", minuto=", minutos_back, ", odds=", odds_cavalo_back, ", W/L=", banco.obtemWinLoseAtual(nome_melhor) )
        
      lista_participantes, lista_bsp, lista_wl = banco.obtemParticipantesDeCorrida(corrida)
      qtd_cavalos_corrida = len(lista_participantes)
      pl_total, total_stack, odds_cavalo_lay, nome_melhor = avaliaLay(minutos_lay=minutos_lay, qtd_cavalos=qtd_cavalos, banco=banco, pl_total=pl_total, total_stack=total_stack)
      frac_odds_1h = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=60)
      frac_odds_45m = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=45)
      frac_odds_35m = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=35)
      frac_odds_30m = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=30)
      frac_odds_31m = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=31) # 5 minutos antes da aposta
      frac_odds_36m = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=36) # 10 minutos antes da aposta
      frac_odds_41m = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=41) # 15 minutos antes da aposta
      frac_odds_46m = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=46) # 20 minutos antes da aposta
      frac_odds_51m = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=51) # 25 minutos antes da aposta
      frac_odds_56m = obtemOddsLay1Hora(nome_melhor, odds_cavalo_lay, qtd_cavalos, banco, minuto_antes=56) # 30 minutos antes da aposta
      
      # Fim da corrida
      if(pl_total is not None): # Dados serão válidos para treino
         nome_mercado = banco.obtemNomeMercadoDaCorrida(corrida)
         handicap, novice, hurdle, maiden, stakes, claiming, amateur, trotting, national_hunt_flat, steeplechase, hunt, nursery, listed, conditions, group1, group2, group3, selling, apprentice, tres_anos_ou_mais, tres_anos, quatro_anos_ou_mais, quatro_anos, cinco_anos_ou_mais, cinco_anos, charity, mare = obtemCaracteristicasDaCorrida(nome_mercado)
         distancia = obtemDistanciaDaPista(nome_mercado)
         if( distancia is None ): distancia = 0 # Sem distância fica como 0?
         valores_afs_lay = banco.obtemAdjustmentFactorProximo(minutos_lay, qtd_cavalos_corrida)
         print("AFs=", valores_afs_lay)
         af_favorito = valores_afs_lay[ list(valores_afs_lay.keys())[0] ]
         if(total_stack is None): pl_unitario = 0.0 # Aposta devolvida
         else: pl_unitario = 1.0*pl_total/total_stack # Retorno unitário da corrida
         
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, odds_cavalo_back, 'odds_back')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, odds_cavalo_lay, 'odds_lay') 
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_1h, 'f_odd_lay_1h')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_45m, 'f_odd_lay_45m')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_35m, 'f_odd_lay_35m')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_30m, 'f_odd_lay_30m')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_31m, 'f_odd_lay_31m')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_36m, 'f_odd_lay_36m')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_41m, 'f_odd_lay_41m')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_46m, 'f_odd_lay_46m')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_51m, 'f_odd_lay_51m')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, frac_odds_56m, 'f_odd_lay_56m')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, distancia, 'dist') # Distância
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, qtd_cavalos_corrida, 'qtd_cav')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, af_favorito, 'af')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, handicap, 'handicap')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, novice, 'novice')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, hurdle, 'hurdle')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, maiden, 'maiden')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, stakes, 'stakes')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, claiming, 'claiming')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, amateur, 'amateur')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, trotting, 'trotting')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, national_hunt_flat, 'national_hunt_flat')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, steeplechase, 'steeplechase')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, hunt, 'hunt')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, nursery, 'nursery')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, listed, 'listed')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, conditions, 'conditions')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, group1, 'group1')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, group2, 'group2')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, group3, 'group3')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, selling, 'selling')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, apprentice, 'apprentice')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, tres_anos_ou_mais, 'tres_anos_ou_mais')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, tres_anos, 'tres_anos')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, quatro_anos_ou_mais, 'quatro_anos_ou_mais')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, quatro_anos, 'quatro_anos')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, cinco_anos_ou_mais, 'cinco_anos_ou_mais')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, cinco_anos, 'cinco_anos')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, charity, 'charity')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, mare, 'mare')
         dados_corrida, nomes_colunas = salvaRegistro(dados_corrida, nomes_colunas, pl_unitario, 'pl')

         print("Linha_corrida=", dados_corrida, ", colunas=", nomes_colunas, ", tam=", len(lista_treino), ", col=", len(nomes_colunas) )
         lista_treino.append(dados_corrida) # Lista de lista
   df = pd.DataFrame(lista_treino, columns = nomes_colunas)
   print("Dados coletados")
   return df

def calculaRegressaoLinear(df, campos_ignorar=[], percentil_ignora=0):
   SomaLogs=[] 
   qtd_colunas_x = len(df.columns)-1 # Tem apenas um Y
   qtd_registros = len(df)
   prop_treino = 0.9999 # Quanto fica para treino. O resto será teste
   qtd_treino = int(qtd_registros*prop_treino)
   qtd_teste = qtd_registros-qtd_treino
   colunas = [col for col in df.columns if col not in campos_ignorar]

   #Fitra o df baseado nas colunas
   df=df[colunas]
   
   #df['dist'] = df['dist'].fillna(0) # Se tiver algum valor Nan 
   #print([np.where(np.isnan(X))]) # Mostra índices que tem Nan
   for i in range(100):
      #Embaralha o dataframe, apartir de um estado predefindo
      df=df.sample(frac=1.0, random_state=i)
      df_teste, df_treino = df[:qtd_teste], df[qtd_teste:]
      
      #Filta o dataframe por intervalo de alguns campos que podem melhorar a regressão
      #min_odd_lay = df.odds_lay.quantile(percentil_ignora)
      #max_odd_lay = df.odds_lay.quantile(1-percentil_ignora)
      #df_treino=df_treino[(df_treino.odds_lay<=max_odd_lay)&(df_treino.odds_lay>=min_odd_lay)]
      #df_teste=df_teste[(df_teste.odds_lay<=max_odd_lay)&(df_teste.odds_lay>=min_odd_lay)]
      #if('odd_lay' in campos_ignorar): del df_treino['odds_lay'] # Uso apenas para filtrar
      #if('odd_lay' in campos_ignorar): del df_teste['odds_lay'] # Uso apenas para filtrar
      
      #Os Xs são todas as colunas exceto a PL que será o Y
      X_treino, Y_treino = df_treino.loc[:,(df_treino.columns!='pl')], df_treino.pl
      X_teste, Y_teste = df_teste.loc[:,(df_teste.columns!='pl')], df_teste.pl
      
      # Treina a regressão com os dados de treinamento
      reg=LinearRegression().fit(X_treino, Y_treino)
      #print('\n Coeficientes #'+str(i)+':')
      #for idx_c in range(len(reg.coef_)): print("Coef do campo", df.columns[idx_c], ":", reg.coef_[idx_c] )
      
      # Verifica a lucratividade nos dados de teste
      SomaLogs.append( [sum(np.log(10+y*y_pred) for y_pred,y in zip(reg.predict(X_teste),Y_teste) if y_pred>0 ) ] )
      #print('Mean squared error: %.2f' % mean_squared_error(Y, Y_reg))
   #X=df.iloc[:, :-1].values # Todos menos o último #print("X=", X)
   #Y=df.iloc[:,-1].values # Apenas o último #print("Y=", Y)
   #X = np.nan_to_num(X) # Para trocar Nan por 0 e Infinity por número
   #print("Todas as somas:", SomaLogs)
   for idx_c in range(len(reg.coef_)): print("Coef do campo", df_teste.columns[idx_c], ":", reg.coef_[idx_c] )
   #print("Soma dos logs sem o valor", campos_ignorar,":", round(np.nanmean(SomaLogs),2)  ) #nanmean ignora valores Nan
   return SomaLogs

def randomWalkerParametros(df):
   config_testadas = [[],] # Para evitar fazer a mesma coisa repetidamente
   colunas_total = [col for col in df.columns if col != 'pl'] # Antes de tudo
   max_configs = 2**len(colunas_total) # O máximo de configurações (Power Set)
   melhor_valor = None # Melhor valor de crescimento exponencial da banca
   melhor_config = [] # Colunas que geram o melhor valor
   colunas_ignorar = []
   chegou_fim = False
   while not chegou_fim:
      if( len(config_testadas) == max_configs-1 ): chegou_fim = True # Encerra se atingiu o máximo
      config_nova = []
      while (config_nova in config_testadas):
         config_nova = [random.randint(0,1) for c in range(len(colunas_total)) ]
      config_testadas.append(config_nova)
      colunas_ignorar = [colunas_total[idx_con] for idx_con in range(len(config_nova)) if config_nova[idx_con]==0]
      sl = calculaRegressaoLinear(df, campos_ignorar=colunas_ignorar )
      m_val = round(np.nanmean(sl),2)
      print("Soma dos logs sem o valor", colunas_ignorar,":", round(np.nanmean(sl),2)  ) #nanmean ignora valores Nan
      if( melhor_valor is None or m_val > melhor_valor ): 
         melhor_valor = m_val
         melhor_config = colunas_ignorar
      print("Melhor valor:", melhor_valor, ", ", melhor_config, ", qtd_hist=", len(config_testadas) )   

def criterioDeKelly(df, campos_ignorar=[], comissao = 0.065):
   media_pls = []
   qtd_colunas_x = len(df.columns)-1 # Tem apenas um Y
   qtd_registros = len(df)
   prop_treino = 0.666 # Quanto fica para treino. O resto será teste
   qtd_treino = int(qtd_registros*prop_treino)
   qtd_teste = qtd_registros-qtd_treino
   colunas = [col for col in df.columns if col not in campos_ignorar]

   #Fitra o df baseado nas colunas
   df_f=df[colunas]

   for i in range(100):
      #Embaralha o dataframe, apartir de um estado predefindo
      df_s=df_f.sample(frac=1.0, random_state=i)
      df_teste, df_treino = df_s[:qtd_teste], df_s[qtd_teste:]
      
      #Os Xs são todas as colunas exceto a PL que será o Y
      X_treino, Y_treino = df_treino.loc[:,(df_treino.columns!='pl')], df_treino.pl
      X_teste, Y_teste = df_teste.loc[:,(df_teste.columns!='pl')], df_teste.pl
      
      # Treina a regressão com os dados de treinamento
      reg=LinearRegression().fit(X_treino, Y_treino)
      
      # Logo depois do reg=
      media_pls.append( sum(y_pred for y_pred,y in zip(reg.predict(X_teste),Y_teste) if y_pred>0) )
   
   # Depois do laço
   m_pl = sum(m for m in media_pls)/len(media_pls)
   print("Media PL=", m_pl)
   kelly = (df.odds_lay.mean()*(1-comissao)-1)/m_pl # Confirmar a fórmula
   return kelly

if __name__ == '__main__':   
   #fazProspeccaoEstrategias(min_minutos_back = 999, max_minutos_back = 999, min_minutos_lay = 26, max_minutos_lay = 26, max_cavalos = 1) # Demora cerca de 7 minutos na configuração padrão
   
   df = obtemDadosTreinoDaEstrategia(minutos_back = 9999, minutos_lay=26, qtd_cavalos=1, frac_treino=1.0) # Estratégia vencedora, por enquanto
   df.to_csv('out_dev_full_47.csv', index=False) # Salvando para fuçar depois
   
   #df = pd.read_csv('out_dev_full_47.csv') # Lendo para fazer a regressão
   #sem_esses = ['odds_lay', 'handicap', 'novice', 'hurdle', 'maiden', 'stakes', 'amateur', 'trotting', 'listed', 'national_hunt_flat', 'steeplechase', 'hunt', 'conditions', 'group1', 'group2', 'group3', 'selling', 'apprentice', 'tres_anos', 'quatro_anos_ou_mais', 'cinco_anos_ou_mais'] # Esse gerou 1.98 no antigo
   #sem_esses = ['charity', 'cinco_anos_ou_mais', 'tres_anos_ou_mais', 'quatro_anos_ou_mais', 'hunt', 'selling', 'national_hunt_flat', 'steeplechase', 'hurdle', 'stakes', 'handicap', 'amateur', 'group1', 'novice', 'maiden', 'listed', 'group3', 'nursery', 'conditions', 'claiming', 'apprentice', 'group2', 'mare', ]
   #sem_esses = ['odds_lay', 'dist', 'maiden', 'stakes', 'amateur', 'trotting', 'national_hunt_flat', 'hunt,nursery', 'listed', 'group2', 'selling', 'apprentice', 'tres_anos_ou_mais', 'tres_anos', 'quatro_anos_ou_mais', 'quatro_anos', 'cinco_anos', 'mare']
   #frac_banca = criterioDeKelly(df, campos_ignorar=sem_esses )
   #print("Hello, my Kelly!", frac_banca)
   #sl = calculaRegressaoLinear(df, campos_ignorar=sem_esses, percentil_ignora=0 )
   #print("Soma dos logs sem o valor", sem_esses,":", round(np.nanmean(sl),2)  ) #nanmean ignora valores Nan
   #randomWalkerParametros(df)
   print("Fim do processamento!")