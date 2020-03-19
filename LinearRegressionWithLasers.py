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
      odds_cavalo_lay = None
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
             #print("Aposta Back retornou=", pl, ", minuto=", minuto, ", odds=", odds_cavalo_back, ", W/L=", banco.obtemWinLoseAtual(nome_melhor) )
        
      #Vendo como estava o mercado nos minutos Back
      retorno = banco.obtemOddsPorMinuto(minutos_back)
      if( retorno is not None ): # Tem realmente algo naqueles minutos
        lista_ordenada = retorno # Obtenho lista ordenada das odds dos cavalos participantes
        melhores_odds = list(lista_ordenada.items())
        if( len(melhores_odds) > qtd_cavalos  ): # Não tem cavalo suficiente para essa estratégia
          for y in range(qtd_cavalos):
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
                if( pl_total is None ): 
                   pl_total = pl # Primeira vez
                   if( pl != 0 ): total_stack = stack_lay # Soma Stack apenas quando não devolve aposta
                else: 
                   pl_total += pl # Concatena
                   if( pl != 0 ): total_stack += stack_lay
             print("Aposta Lay retornou=", pl, ", minuto=", minuto, ", odds=", odds_cavalo_lay, ", W/L=", banco.obtemWinLoseAtual(nome_melhor), ", stack=", stack_lay )
      # Fim da corrida
      if(pl_total is not None): # Dados serão válidos para treino
         nome_mercado = banco.obtemNomeMercadoDaCorrida(corrida)
         handicap, novice, hurdle, maiden, stakes, claiming, amateur, trotting, national_hunt_flat, steeplechase, hunt, nursery, listed, conditions, group1, group2, group3, selling, apprentice, tres_anos_ou_mais, tres_anos, quatro_anos_ou_mais, quatro_anos, cinco_anos_ou_mais, cinco_anos, charity, mare = obtemCaracteristicasDaCorrida(nome_mercado)
         distancia = obtemDistanciaDaPista(nome_mercado)
         if( distancia is None ): distancia = 0 # Sem distância fica como 0?
         if(total_stack is None): pl_unitario = 0.0 # Aposta devolvida
         else: pl_unitario = 1.0*pl_total/total_stack # Retorno unitário da corrida
         if( odds_cavalo_back is not None ): 
            dados_corrida.append( odds_cavalo_back )
            if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('odds_back')
         if( odds_cavalo_lay is not None ): 
            dados_corrida.append( odds_cavalo_lay )
            if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('odds_lay')
         dados_corrida.append(distancia)
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('dist')
         dados_corrida.append( len(melhores_odds) )
         if(len(dados_corrida) > len(nomes_colunas) ): nomes_colunas.append('qtd_cav')
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

def calculaRegressaoLinear(df, campos_ignorar=[], percentil_ignora=0):
   SomaLogs=[] 
   qtd_colunas_x = len(df.columns)-1 # Tem apenas um Y
   qtd_registros = len(df)
   prop_treino = 0.666 # Quanto fica para treino. O resto será teste
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
   #fazProspeccaoEstrategias(min_minutos_back = 9999, max_minutos_back = 9999, min_minutos_lay = 26, max_minutos_lay = 26, max_cavalos = 1) # Demora cerca de 42 horas na configuração padrão
   
   df = obtemDadosTreinoDaEstrategia(minutos_back = 9999, minutos_lay=26, qtd_cavalos=1, frac_treino=1.0) # Estratégia vencedora, por enquanto
   df.to_csv('out_dev_full_47.csv', index=False) # Salvando para fuçar depois
   
   #df = pd.read_csv('out_dev_full.csv') # Lendo para fazer a regressão
   #sem_esses = ['odds_lay', 'handicap', 'novice', 'hurdle', 'maiden', 'stakes', 'amateur', 'trotting', 'listed', 'national_hunt_flat', 'steeplechase', 'hunt', 'conditions', 'group1', 'group2', 'group3', 'selling', 'apprentice', 'tres_anos', 'quatro_anos_ou_mais', 'cinco_anos_ou_mais'] # Esse gerou 1.98 no antigo
   #sem_esses = ['charity', 'cinco_anos_ou_mais', 'tres_anos_ou_mais', 'quatro_anos_ou_mais', 'hunt', 'selling', 'national_hunt_flat', 'steeplechase', 'hurdle', 'stakes', 'handicap', 'amateur', 'group1', 'novice', 'maiden', 'listed', 'group3', 'nursery', 'conditions', 'claiming', 'apprentice', 'group2', 'mare', ]
   #frac_banca = criterioDeKelly(df, campos_ignorar=sem_esses )
   #print("Hello, my Kelly!", frac_banca)
   #sl = calculaRegressaoLinear(df, campos_ignorar=sem_esses, percentil_ignora=0 )
   #print("Soma dos logs sem o valor", sem_esses,":", round(np.nanmean(sl),2)  ) #nanmean ignora valores Nan
   #randomWalkerParametros(df)
   print("Fim do processamento!")