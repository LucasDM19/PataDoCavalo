

from BDUtils import BaseDeDados

if __name__ == '__main__':   
   banco = BaseDeDados()
   banco.conectaBaseDados('bf_gb_win_full.db')
   
   nomes_mercados = banco.obtemNomesDosMercados()
   palavras_unicas_nome_mercado = []
   for nome_mercado in nomes_mercados:
      #print("Esse=", nome_mercado.split(), nome_mercado )
      for termo in nome_mercado.split():
         if( termo not in palavras_unicas_nome_mercado ):
            palavras_unicas_nome_mercado.append(termo)
   for punm in palavras_unicas_nome_mercado:
      try:
         qtd_miles = ''
         qtd_fur = ''
         if( 'm' in punm and 'f' in punm ):
            print("Termo=", punm)
            p1, p2 = punm.split('m')
            qtd_miles = int(p1)
            p3, p4 = p2.split('f')
            qtd_fur = int(p3)
            print("tem miles", str(qtd_miles), " tem furlong", str(qtd_fur) )
         elif( 'm' in punm ):
            print("Termo=", punm)
            p1, p2 = punm.split('m')
            qtd_miles = int(p1)
            print("tem miles", str(qtd_miles) )
         elif( 'f' in punm ):   
            print("Termo=", punm)
            p3, p4 = punm.split('f')
            qtd_fur = int(p3)
            print(" tem furlong", str(qtd_fur) )
      except ValueError:
         print(punm, " deu ruim")
      #if( 'm' in punm ): print("Termo=", punm, " tem mile")
   print("Total=", len(palavras_unicas_nome_mercado))