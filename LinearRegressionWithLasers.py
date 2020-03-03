#coding: utf-8
from BDUtils import BaseDeDados
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def obtemDistanciaDaPista(nome_mercado):
   distancia_milhas = '' 
   #milha_metro = 1609.34 # Quantos metros tem uma milha
   milha_milha = 1.0 # Padrão será em milhas
   #furlong_metro = 201.168 # Quantos metros tem um furlong
   furlong_milha = 0.125 # Quantos furlongs tem uma milha
   #print("Nome=", nome_mercado)
   for punm in nome_mercado.split():
      try:
         qtd_miles = ''
         qtd_fur = ''
         if( 'm' in punm and 'f' in punm ):
            #print("Termo M e F=", punm)
            p1, p2 = punm.split('m')
            qtd_miles = int(p1)
            p3, p4 = p2.split('f')
            qtd_fur = int(p3)
            #print("tem miles", str(qtd_miles), " tem furlong", str(qtd_fur) )
            distancia_milhas = milha_milha*qtd_miles + furlong_milha*qtd_fur
         elif( 'm' in punm ):
            #print("Termo=", punm)
            p1, p2 = punm.split('m')
            qtd_miles = int(p1)
            #print("tem miles", str(qtd_miles) )
            if( distancia_milhas == '' ):
               distancia_milhas = milha_milha*qtd_miles
            else:
               distancia_milhas += milha_milha*qtd_miles
         elif( 'f' in punm ):   
            #print("Termo F=", punm)
            p3, p4 = punm.split('f')
            qtd_fur = int(p3)
            #print(" tem furlong", str(qtd_fur) )
            if( distancia_milhas == '' ):
               distancia_milhas = furlong_milha*qtd_fur
            else:
               distancia_milhas += furlong_milha*qtd_fur
         #else: print("Mist=", punm)
      except ValueError:
         pass
         #print(punm, " deu ruim")
   if( distancia_milhas == '' ): return None
   return distancia_milhas

def obtemExtremosDistancias(nomes_mercados):
   #for punm in nomes_mercados:
      #dist = obtemDistanciaDaPista( punm )
      #if( dist is not None ): print("Termo=", punm, " distancia", str(dist) )
   dist_maxima = max([ obtemDistanciaDaPista(nm) for nm in nomes_mercados  if obtemDistanciaDaPista(nm) is not None] )
   dist_minima = min([ obtemDistanciaDaPista(nm) for nm in nomes_mercados  if obtemDistanciaDaPista(nm) is not None] )
   return dist_maxima, dist_minima

def obtemCaracteristicasDaCorrida(nome_mercado):
   handicap = 0
   novice = 0
   hurdle = 0
   maiden = 0
   stakes = 0
   claiming = 0
   amateur = 0
   trotting = 0
   listed = 0
   national_hunt_flat = 0
   steeplechase = 0
   hunt = 0
   nursery = 0
   listed = 0
   conditions = 0
   group1 = 0
   group2 = 0
   group3 = 0
   selling = 0
   apprentice = 0
   tres_anos = 0
   tres_anos_ou_mais = 0
   quatro_anos_ou_mais = 0
   quatro_anos = 0
   cinco_anos_ou_mais = 0
   cinco_anos = 0
   charity = 0
   mare = 0
   if('Hcap' in nome_mercado ): handicap = 1 # Iguala o peso com base na vantagem
   if('Nov' in nome_mercado ): novice = 1 # 2 anos de idade que não ganharam mais de uma vez
   if('Hrd' in nome_mercado or 'Hurdle' in nome_mercado ): hurdle = 1 # Com aquelas barreiras para pular
   if('Mdn' in nome_mercado ): maiden = 1 # Nunca correu na vida
   if('Stks' in nome_mercado or 'Stakes' in nome_mercado ): stakes = 1 # Sem o handicap
   if('Claim' in nome_mercado ): claiming = 1 # Todos tem o mesmo preço (Claiming Price) inicial igual antes da corrida
   if('Amateur' in nome_mercado or 'Amat' in nome_mercado ): amateur = 1 # Amador?
   if('Trot' in nome_mercado ): trotting = 1 # Corrida com mini biga / charrete
   if('Listed' in nome_mercado ): listed = 1 # 	Just below group class
   if('NHF' in nome_mercado ): national_hunt_flat = 1 # No piso mesmo Flat racing / Bumper races
   if('Chs' in nome_mercado or 'Chase' in nome_mercado ): steeplechase = 1 # Pula mureta e fossa
   if('Hunt' in nome_mercado or 'Hnt' in nome_mercado ): hunt = 1 # Pula mureta e fossa
   if('Nursery' in nome_mercado or 'Juv' in nome_mercado ): nursery = 1 # Exclusiva para cavalos com dois anos de idade
   if('Listed' in nome_mercado or 'List' in nome_mercado ): listed = 1 # Abaixo do Grupo 3 de ranking
   if('Cond' in nome_mercado ): conditions = 1 # Tem peso de acordo com o sexo, idade e habilidade do cavalo
   if('Grp1' in nome_mercado or 'Grp 1' in nome_mercado ): group1 = 1
   if('Grp2' in nome_mercado or 'Grp 2' in nome_mercado ): group2 = 1
   if('Grp3' in nome_mercado or 'Grp 3' in nome_mercado ): group3 = 1
   if('Sell' in nome_mercado or 'Selling' in nome_mercado ): selling = 1 # Cavalo de baixa classe. O vencedor é vendido.
   if('App' in nome_mercado ): apprentice = 1 # Apenas para jóqueis aprendizes (novatos)
   if('3yo+' in nome_mercado ): tres_anos_ou_mais = 1 # Correm os cavalos com três anos ou mais
   if('3yo' in nome_mercado and '3yo+' not in nome_mercado ): tres_anos = 1 # Correm cavalos com três anos de idade
   if('4yo+' in nome_mercado ): quatro_anos_ou_mais = 1 # Correm os cavalos com quatro anos ou mais
   if('4yo' in nome_mercado and '4yo+' not in nome_mercado ): quatro_anos = 1 # Correm os cavalos com quatro anos de idade
   if('5yo+' in nome_mercado ): cinco_anos_ou_mais = 1 # Correm os cavalos com cinco anos ou mais
   if('5yo' in nome_mercado and '5yo+' not in nome_mercado ): cinco_anos = 1 # Correm os cavalos com cinco anos de idade
   if('Charity' in nome_mercado ): charity = 1 # Corrida para a Caridade
   if('Mare' in nome_mercado or 'Mares' in nome_mercado ): mare = 1 # Éguas acima de três anos de idade
   if( sum([handicap, novice, hurdle, maiden, stakes, claiming, amateur, trotting, listed, national_hunt_flat, steeplechase, hunt, nursery, listed, conditions, group1, group2, group3, selling, apprentice, tres_anos_ou_mais, tres_anos, quatro_anos_ou_mais, quatro_anos, cinco_anos_ou_mais, cinco_anos, charity, mare ]) == 0 ): print("Falta:", nome_mercado)
   return handicap, novice, hurdle, maiden, stakes, claiming, amateur, trotting, listed, national_hunt_flat, steeplechase, hunt, nursery, listed, conditions, group1, group2, group3, selling, apprentice, tres_anos_ou_mais, tres_anos, quatro_anos_ou_mais, quatro_anos, cinco_anos_ou_mais, cinco_anos, charity, mare

# Só para manter o backup
def coletaInformacoesSobreCorridas():
   nomes_mercados = banco.obtemNomesDosMercados()
   for nm in nomes_mercados:
      lista = obtemCaracteristicasDaCorrida(nm)
   dist_maxima, dist_minima = obtemExtremosDistancias(nomes_mercados)
   print("Distância Máxima:", dist_maxima, ", distância mínima:", dist_minima)

def fazApostaBack(odd_back, stack_back, wl_back, comissao = 0.065):
   if( stack_back < 2 ): return None # Sem condicao
   if( wl_back == 0 ): 
      pl_back = (-1*stack_back) 
   elif( wl_back == 1 ): 
      pl_back = stack_back*(odd_back)-stack_back
   else: return None # WL invalido nao conta
   if( pl_back > 0 ): 
      pl_back = pl_back*(1-comissao)
   return pl_back
   
def fazApostaLay(odd_lay, stack_lay, wl_lay, comissao = 0.065):
   if( stack_lay < 2 ): return 0 # Sem condicao
   if( wl_lay == 0 ): 
      pl_lay = (+1*stack_lay)
   elif( wl_lay == 1 ): 
      pl_lay = (-1*(stack_lay*(odd_lay-1)))
   else: return None # WL invalido nao conta
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
      return "nome=" + str(self.nome)+ ", saldo=" + str(round(self.saldo,2)) + ", min_back=" + str(self.min_back) + ", min_lay=" + str(self.min_lay) + ", max_cavalo=" + str(self.max_cavalo) + ", qtd_back=" + str(self.total_back) + ", qtd_lay=" + str(self.total_lay)

def fazProspeccaoEstrategias(min_minutos_back = 1, max_minutos_back = 60, min_minutos_lay = 1, max_minutos_lay = 60, max_cavalos = 3): # Demora cerca de 42 horas na configuração padrão
   banco = BaseDeDados()
   banco.conectaBaseDados('bf_gb_win_full.db')
   estrategias = []
   contador_id = 0
   for minutos1 in range(min_minutos_back,max_minutos_back+1):
      for minutos2 in range(min_minutos_lay,max_minutos_lay+1):
         for tantos_cavalos in range(max_cavalos):
            est = Estrategia(nome=contador_id, min_back=minutos1, min_lay=minutos2, max_cavalo=tantos_cavalos)
            estrategias.append(est)
            contador_id += 1
   print("Estratégias=", len(estrategias))
   data_inicial, data_final, total_corridas = banco.obtemSumarioDasCorridas()
   #total_corridas = 2
   corridas = banco.obtemCorridas(qtd_corridas=total_corridas, ordem="ASC") # ASC - Antigas primeiro, DESC - Recentes primeiro
   #corridas = ['1.123344088',]
   for corrida in corridas:
      print("Corrida=", corrida)
      minutosCorrida = banco.obtemMinutosDaCorrida(corrida) # Quais minutos tem eventos registrado de odds
      if(len(minutosCorrida) != 0): todos_minutos = range(max(minutosCorrida),min(minutosCorrida)-1,-1) 
      else: todos_minutos = []
      for minuto in todos_minutos:
         if( minuto in minutosCorrida ): # Tem atualização
            retorno = banco.obtemOddsPorMinuto(minuto) # Todas as odds consolidadas
         if( retorno is not None ):
            lista_ordenada = retorno # Obtenho lista ordenada das odds dos cavalos participantes
            melhores_odds = list(lista_ordenada.items())
            #if( minuto in minutosCorrida ): print("Minuto", minuto, " tem atualização", ", Odds=", melhores_odds)
            #else: print("Minuto=", minuto, ", Odds=", melhores_odds)
            #print("Minuto=", minuto, ", Odds=", melhores_odds)
            estrategias_com_minutos_back = [e for e in estrategias if e.min_back==minuto]
            for em in estrategias_com_minutos_back:
               #print("Odds=", len(melhores_odds), "cavalo=", em.max_cavalo)
               if( len(melhores_odds) > em.max_cavalo  ): # Não tem cavalo suficiente para essa estratégia
                  for y in range(em.max_cavalo+1):
                     nome_melhor = melhores_odds[y][0]
                     odds_cavalo = melhores_odds[y][1]
                     pl = fazApostaBack(odd_back=odds_cavalo, stack_back=20, wl_back=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)                  
                     if(pl is not None): 
                        em.total_back += 1
                        em.saldo += pl
                     #print("Aposta Back retornou=", pl, ", ", str(em), ", minuto=", minuto, ", odds=", odds_cavalo, ", W/L=", banco.obtemWinLoseAtual(nome_melhor) )
            estrategias_com_minutos_lay = [e for e in estrategias if e.min_lay==minuto]
            for em in estrategias_com_minutos_lay:
               if( len(melhores_odds) > em.max_cavalo  ): # Não tem cavalo suficiente para essa estratégia
                  for y in range(em.max_cavalo+1):
                     nome_melhor = melhores_odds[y][0]
                     odds_cavalo = melhores_odds[y][1]
                     #pl = fazApostaLay(odd_lay=banco.obtemBSPAtual(nome_melhor), stack_lay=20, wl_lay=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)
                     pl = fazApostaLay(odd_lay=odds_cavalo, stack_lay=20, wl_lay=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)
                     if(pl is not None): 
                        em.total_lay += 1
                        em.saldo += pl  
                     #print("Aposta Lay retornou=", pl, ", ", str(em), ", minuto=", minuto, ", odds=", odds_cavalo, ", W/L=", banco.obtemWinLoseAtual(nome_melhor) )                  
   newlist = sorted(estrategias, key=lambda x: x.saldo, reverse=True) # Ordeno a lista de acordo com o saldo
   for item_es in newlist: 
      print("Esse:", str(item_es) )

def obtemDadosTreinoDaEstrategia(minutos_back, minutos_lay, qtd_cavalos, frac_treino):
   banco = BaseDeDados()
   banco.conectaBaseDados('bf_gb_win_full.db')
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
      odds_cavalo_lay = None
      print("Corrida=", corrida, ", são=", datetime.now().time() )
      minutosCorrida = banco.obtemMinutosDaCorrida(corrida) # Quais minutos tem eventos registrado de odds
      if(len(minutosCorrida) != 0): todos_minutos = range(max(minutosCorrida),min(minutosCorrida)-1,-1) 
      else: todos_minutos = []
      tempo_minimo = min(minutos_back, minutos_lay) # Vendo até onde precisa de ir
      minutos_validos = [minuto for minuto in todos_minutos if minuto >= tempo_minimo ] # Minutos até o necessário
      for minuto in minutos_validos:
         if( minuto in minutosCorrida ): # Tem atualização
            retorno = banco.obtemOddsPorMinuto(minuto) # Todas as odds consolidadas
         if( retorno is not None ):
            lista_ordenada = retorno # Obtenho lista ordenada das odds dos cavalos participantes
            melhores_odds = list(lista_ordenada.items())
            if( minutos_back == minuto ):
               if( len(melhores_odds) > qtd_cavalos  ): # Não tem cavalo suficiente para essa estratégia
                  for y in range(qtd_cavalos):
                     nome_melhor = melhores_odds[y][0]
                     odds_cavalo_back = melhores_odds[y][1]
                     pl = fazApostaBack(odd_back=odds_cavalo_back, stack_back=20, wl_back=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)                  
                     if(pl is not None): 
                        if( pl_total is None ): 
                           pl_total = pl # Primeira vez
                           total_stack = 20
                        else: 
                           pl_total += pl # Concatena
                           total_stack = 40
                     #print("Aposta Back retornou=", pl, ", minuto=", minuto, ", odds=", odds_cavalo_back, ", W/L=", banco.obtemWinLoseAtual(nome_melhor) )
            if( minutos_lay == minuto ): 
               if( len(melhores_odds) > qtd_cavalos  ): # Não tem cavalo suficiente para essa estratégia
                  for y in range(qtd_cavalos):
                     nome_melhor = melhores_odds[y][0]
                     odds_cavalo_lay = melhores_odds[y][1]
                     pl = fazApostaLay(odd_lay=odds_cavalo_lay, stack_lay=20, wl_lay=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)
                     if(pl is not None): 
                        if( pl_total is None ): 
                           pl_total = pl # Primeira vez
                           total_stack = 20
                        else: 
                           pl_total += pl # Concatena
                           total_stack = 40
                     #print("Aposta Lay retornou=", pl, ", minuto=", minuto, ", odds=", odds_cavalo_lay, ", W/L=", banco.obtemWinLoseAtual(nome_melhor) )
      # Fim da corrida
      if(pl_total is not None): # Dados serão válidos para treino
         nome_mercado = banco.obtemNomeMercadoDaCorrida(corrida)
         handicap, novice, hurdle, maiden, stakes, claiming, amateur, trotting, listed, national_hunt_flat, steeplechase, hunt, nursery, listed, conditions, group1, group2, group3, selling, apprentice, tres_anos_ou_mais, tres_anos, quatro_anos_ou_mais, quatro_anos, cinco_anos_ou_mais, cinco_anos, charity, mare = obtemCaracteristicasDaCorrida(nome_mercado)
         distancia = obtemDistanciaDaPista(nome_mercado)
         pl_unitario = 1.0*pl_total/total_stack # Retorno unitário da corrida
         if( odds_cavalo_back is not None ): 
            dados_corrida.append( odds_cavalo_back )
            if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('odds_back')
         if( odds_cavalo_lay is not None ): 
            dados_corrida.append( odds_cavalo_lay )
            if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('odds_lay')
         dados_corrida.append(distancia)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('dist')
         dados_corrida.append(handicap)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('handicap')
         dados_corrida.append(novice)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('novice')
         dados_corrida.append(hurdle)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('hurdle')
         dados_corrida.append(maiden)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('maiden')
         dados_corrida.append(stakes)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('stakes')
         dados_corrida.append(claiming)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('claiming')
         dados_corrida.append(amateur)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('amateur')
         dados_corrida.append(trotting)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('trotting')
         dados_corrida.append(listed)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('listed')
         dados_corrida.append(national_hunt_flat)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('national_hunt_flat')
         dados_corrida.append(steeplechase)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('steeplechase')
         dados_corrida.append(hunt)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('hunt')
         dados_corrida.append(nursery)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('nursery')
         dados_corrida.append(listed)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('listed')
         dados_corrida.append(conditions)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('conditions')
         dados_corrida.append(group1)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('group1')
         dados_corrida.append(group2)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('group2')
         dados_corrida.append(group3)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('group3')
         dados_corrida.append(selling)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('selling')
         dados_corrida.append(apprentice)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('apprentice')
         dados_corrida.append(tres_anos_ou_mais)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('tres_anos_ou_mais')
         dados_corrida.append(tres_anos)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('tres_anos')
         dados_corrida.append(quatro_anos_ou_mais)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('quatro_anos_ou_mais')
         dados_corrida.append(quatro_anos)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('quatro_anos')
         dados_corrida.append(cinco_anos_ou_mais)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('cinco_anos_ou_mais')
         dados_corrida.append(cinco_anos)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('cinco_anos')
         dados_corrida.append(charity)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('charity')
         dados_corrida.append(mare)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('mare')
         dados_corrida.append(pl_unitario)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('pl')
         print("Linha_corrida=", dados_corrida, ", colunas=", nomes_colunas, ", tam=", len(lista_treino) )
         lista_treino.append(dados_corrida) # Lista de lista
   df = pd.DataFrame(lista_treino, columns = nomes_colunas)
   print("Dados coletados")
   return df

def calculaRegressaoLinear(df):
   #Embaralha o dataframe, apartir de um estado predefindo
   df=df.sample(frac=1.0, random_state=1)
   qtd_colunas_x = len(df.columns)-1 # Tem apenas um Y
   qtd_registros = len(df)
   X=df.iloc[:, :-1].values # Todos menos o último
   print("X=", X)
   Y=df.iloc[:,-1].values # Apenas o último
   print("Y=", Y)
   reg=LinearRegression().fit(X, Y)
   Y_reg=reg.predict(df.iloc[:qtd_registros,:qtd_colunas_x].values) # Y da Regressão Linear
   print('Coeficientes: \n', reg.coef_)
   print('Mean squared error: %.2f' % mean_squared_error(Y, Y_reg))
   print('LR:', sum(np.log(1+y*y_pred) for y_pred,y in zip(Y_reg,Y) if y_pred>0) )

if __name__ == '__main__':   
   #fazProspeccaoEstrategias(min_minutos_back = 9999, max_minutos_back = 9999, min_minutos_lay = 26, max_minutos_lay = 26, max_cavalos = 1) # Demora cerca de 42 horas na configuração padrão
   df = obtemDadosTreinoDaEstrategia(minutos_back = 9999, minutos_lay=26, qtd_cavalos=1, frac_treino=1.0) # Estratégia vencedora, por enquanto
   df.to_csv('out_full.csv', index=False) # Salvando para fuçar depois
   #df = pd.read_csv('out_full.csv') # Lendo para fazer a regressão
   #calculaRegressaoLinear(df)
   print("Fim do processamento!")