#coding: utf-8
from BDUtils import BaseDeDados

def obtemDistanciaDaPista(nome_mercado):
   distancia_milhas = '' 
   #milha_metro = 1609.34 # Quantos metros tem uma milha
   milha_milha = 1.0 # Padrão será em milhas
   #furlong_metro = 201.168 # Quantos metros tem um furlong
   furlong_milha = 0.125 # Quantos furlongs tem uma milha
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
         else: print("Mist=", punm)
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
   handicap, novice, hurdle, maiden, stakes, claiming, amateur, trotting, listed = 0
   if('Hcap' in nome_mercado ): handicap = 1 # Iguala o peso com base na vantagem
   if('Nov' in nome_mercado ): novice = 1 # 2 anos de idade que não ganharam mais de uma vez
   if('Hrd' in nome_mercado ): hurdle = 1 # Com aquelas barreiras para pular
   if('Mdn' in nome_mercado ): maiden = 1 # Nunca correu na vida
   if('Stks' in nome_mercado ): stakes = 1 # Sem o handicap
   if('Claim' in nome_mercado ): claiming = 1 # Todos tem o mesmo preço (Claiming Price) inicial igual antes da corrida
   if('Amateur' in nome_mercado or 'Amat' in nome_mercado ): amateur = 1 # Amador?
   if('Trot' in nome_mercado ): trotting = 1 # Corrida com mini biga
   if('Listed' in nome_mercado ): listed = 1 # 	Just below group class
   """
   M
   S
   R8
   R7
   PA
   3yo+
   4yo+
   Plt
   Pace
   Grd
   Grp1
   Grp3
   Magnolia
   Charity
   Sell
   Nursery
   """
   

if __name__ == '__main__':   
   banco = BaseDeDados()
   banco.conectaBaseDados('bf_gb_win_full.db')
   
   nomes_mercados = banco.obtemNomesDosMercados()
   dist_maxima, dist_minima = obtemExtremosDistancias(nomes_mercados)
   print("Distância Máxima:", dist_maxima, ", distância mínima:", dist_minima)