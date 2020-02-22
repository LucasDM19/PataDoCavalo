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

if __name__ == '__main__':   
   banco = BaseDeDados()
   banco.conectaBaseDados('bf_gb_win_full.db')
   
   corridas = banco.obtemCorridas(qtd_corridas=1, ordem="ASC") # ASC - Antigas primeiro, DESC - Recentes primeiro
   for corrida in corridas:
      minutosCorrida = banco.obtemMinutosDaCorrida(corrida) # Quais minutos tem eventos registrado de odds
      for minuto in minutosCorrida:
         retorno = banco.obtemOddsPorMinuto(minuto) # Todas as odds consolidadas
         if( retorno is not None ):
            melhores_odds = retorno # Obtenho lista ordenada das odds dos cavalos participantes
            print("Minuto=", minuto, ", Odds=", melhores_odds)
   