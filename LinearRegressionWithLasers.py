#coding: utf-8
from BDUtils import BaseDeDados
from sklearn.linear_model import LinearRegression

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
   def __init__(self, min_back, min_lay, max_cavalo):
      self.min_back = min_back
      self.min_lay = min_lay
      self.max_cavalo = max_cavalo
      self.saldo = 1000
      self.total_back = 0
      self.total_lay = 0

if __name__ == '__main__':   
   banco = BaseDeDados()
   banco.conectaBaseDados('bf_gb_win_full.db')
   #minutos_back = []
   #minutos_lay = []
   #maximo_cavalos = []
   estrategias = []
   for minutos1 in range(1,60+1):
      for minutos2 in range(1,60+1):
         for tantos_cavalos in range(3):
            est = Estrategia(min_back=minutos1, min_lay=minutos2, max_cavalo=tantos_cavalos)
            estrategias.append(est)
   print("Estratégias=", len(estrategias))
   #saldos = [1000 for s in range(len(minutos_back))]
   #totais_back = [0 for b in range(len(minutos_back))]
   #totais_lay = [0 for l in range(len(minutos_back))]
   data_inicial, data_final, total_corridas = banco.obtemSumarioDasCorridas()
   total_corridas = 2
   corridas = banco.obtemCorridas(qtd_corridas=total_corridas, ordem="ASC") # ASC - Antigas primeiro, DESC - Recentes primeiro
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
               #print("Passou", em.max_cavalo)
               for y in range(em.max_cavalo):
                  nome_melhor = melhores_odds[y][0]
                  odds_cavalo = melhores_odds[y][1]
                  pl = fazApostaBack(odd_back=odds_cavalo, stack_back=20, wl_back=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)
                  if(pl is not None): 
                     print("Aposta Back retornou=", pl)
                     em.total_back += 1
                     em.saldo += pl
            estrategias_com_minutos_lay = [e for e in estrategias if e.min_lay==minuto]
            for em in estrategias_com_minutos_lay:
               for y in range(em.max_cavalo):
                  nome_melhor = melhores_odds[y][0]
                  odds_cavalo = melhores_odds[y][1]
                  #pl = fazApostaLay(odd_lay=banco.obtemBSPAtual(nome_melhor), stack_lay=20, wl_lay=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)
                  pl = fazApostaLay(odd_lay=odds_cavalo, stack_lay=20, wl_lay=banco.obtemWinLoseAtual(nome_melhor), comissao = 0.065)
                  if(pl is not None): 
                     print("Aposta Lay retornou=", pl)
                     em.total_lay += 1
                     em.saldo += pl  
   memlhor_saldo = [es for es in estrategias if es.saldo==max([e.saldo for e in estrategias])][0]
   #for idx_final, saldo in enumerate(saldos): print("Fiz", totais_back[idx_final], "Backs e ", totais_lay[idx_final], "Lays. Saldo final:", round(saldos[idx_final],2) )
   print("Fiz", memlhor_saldo.total_back, "Backs e ", memlhor_saldo.total_lay, "Lays. Saldo final:", round(memlhor_saldo.saldo,2) )