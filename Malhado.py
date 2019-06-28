# -*- coding: utf-8 -*-
from RestAPI import *
from Hush import *
from datetime import datetime
from datetime import timedelta
from time import sleep

class Malhado():
   def __init__(self, api=None):
      if(api is None): #Nao poderia
         raise Exception('Invalid API values for BotFair!')
      if(api.estaLogado() == False): #Falta o logon
         api.fazLogin()
      self.api = api
      self.horseRacingID = self.obtemIdDoEsporte(eventTypeName="Horse Racing", lazyMode=True) #Sempre eh 1
      
   """
   Obtem o ID de um esporte, com base no nome.
   """
   def obtemIdDoEsporte(self, eventTypeName="Horse Racing", lazyMode=False):
      if( lazyMode and eventTypeName == "Horse Racing" ) : return '7' #Para evitar chamadas desnecessarias
      filtroVazio = '{"filter":{ }}'
      je = self.api.listaTiposDeEventos()
      eventID = [je[idx]['eventType']['id'] for idx in range(len(je)) if je[idx]['eventType']['name']== eventTypeName ][0] #Ja sei que o ID de Soccer eh 1
      return eventID

   """
   O mercado que interessa e o mais simples. O Win.
   """
   def obtemListaCavalosWinInglaterra(self, horas=24, minutos=0):
      import datetime
      now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
      future = (datetime.datetime.now() + datetime.timedelta(hours=horas, minutes=minutos)).strftime('%Y-%m-%dT%H:%M:%SZ')
      filtro=('{"filter":{"eventTypeIds":["' + self.horseRacingID + '"],"marketCountries":["GB"],"marketTypeCodes":["WIN"],'\
                '"marketStartTime":{"from":"' + now + '", "to":"' + future + '"}},"sort":"FIRST_TO_START","maxResults":"5",\
                "marketProjection":["RUNNER_DESCRIPTION","EVENT"]}, "id": 1}')
      self.corridasWin = api.obtemTodosMercadosDasPartidas(json_req=filtro)
      
   """
   Pesquisando os preços da corrida em questão.
   """
   def obtemOddsDaCorrida(self, idMercado):
      filtro= '{ "marketIds": [' + idMercado + '], "priceProjection": { "priceData": ["EX_BEST_OFFERS"], "virtualise": "true" } }'
      odds = api.obtemOddsDosMercados(json_req=filtro)
      melhoresOdds = odds
      
      try:
         self.OddsCorrida[idMercado] = melhoresOdds
      except AttributeError:
         self.OddsCorrida = {}
         self.OddsCorrida[idMercado] = melhoresOdds
   
   """
   Aposta Back (favor) de uma determinada seleção.
   """   
   def apostaBack(self, idMercado, selectionId, odds_back, stack_back):
      filtro = '{"marketId":"' + idMercado + '","instructions":'\
               '[{"selectionId":"' + str(selectionId) + '","handicap":"0","side":"BACK","orderType":"LIMIT","limitOrder":'\
               '{"size":"' + str(stack_back) + '","price":"'+ str(odds_back) +'","persistenceType":"LAPSE"}}],"customerRef":"test1919191919"}'
      dados_aposta = api.aposta(json_req=filtro)
      return dados_aposta
      
   """
   Aposta Lay (contra) uma determinada seleção, com Starter Price. 
   """
   def apostaLaySP(self, idMercado, selectionId, stack_lay):
      filtro = '{"marketId": "' + idMercado + '",'\
               '"instructions": [ { "selectionId": "' + str(selectionId) + '", "handicap": "0", "side": "LAY", "orderType": "MARKET_ON_CLOSE", "marketOnCloseOrder": '\
               '{ "liability": "' + str(stack_lay) + '" } } ]}'
      dados_aposta = api.aposta(json_req=filtro)
      return dados_aposta
   
      
if __name__ == "__main__":
   print("Vai, malhado!")
   
   u, s, a = usuarioAPI, senhaAPI, APIKey
   api = BetfairAPI(usuario=u, senha=s, api_key=a)
   bot = Malhado(api )
   bot.obtemListaCavalosWinInglaterra(horas=24)
   #sorted(bot.corridasWin, key = lambda i: i["event"]["openDate"])   # Não ajudou muito

   for idx_corrida in range(len(bot.corridasWin)):   # Para cada próxima corrida
      proxima_corrida = bot.corridasWin[idx_corrida]["event"]["openDate"]   # Apenas a próxima corrida
      idMercado = bot.corridasWin[idx_corrida]['marketId']
      nomeEvento = bot.corridasWin[idx_corrida]['event']['name']
      print("Proxima corrida=", proxima_corrida, ", Mkt=", idMercado)
      data_futura = datetime.strptime(proxima_corrida, '%Y-%m-%dT%H:%M:%S.%fZ')
      data_futura_1h = data_futura - timedelta(hours=1, minutes=0)   # Uma hora antes do jogo
      data_fuso_londres = data_futura_1h - timedelta(hours=3, minutes=0) # Três horas de fuso horário
      delta = data_fuso_londres - datetime.now()
      if( delta.seconds <= 0 ): # Não tem Delorean
         print("Delta {0} negativo!".format(delta))
         continue   # Próxima corrida
      print("Aguardarei {0} segundos. Até a data {1}".format(delta.seconds, data_fuso_londres))
      sleep(delta.seconds)
      print("Acordei! Agora sao->", datetime.now())
      
      # Agora obtenho as odds da corrida acima (pelo ID)
      bot.obtemOddsDaCorrida(idMercado)
      selectionId = bot.OddsCorrida[idMercado][0]["runners"][0]['selectionId']
      #print("Selecion=", selectionId)
      nomeCavalo = [bot.corridasWin[idx_corrida]['runners'][idxRunner]["runnerName"] for idxRunner in range(len(bot.corridasWin[idx_corrida]['runners'])) if bot.corridasWin[idx_corrida]['runners'][idxRunner]["selectionId"]==selectionId][0]
      odds_back = bot.OddsCorrida[idMercado][0]["runners"][0]['ex']['availableToBack'][0]['price']
      stack_lay = 20.0
      stack_back = round(stack_lay/(odds_back-1),2)   # Retorno equilibrado com Lay
      print("{0} - Cavalo {1}, Lay com odds de {2} e stack de {3}, na corrida {4} ".format(datetime.now(), nomeCavalo, odds_back, stack_back, nomeEvento))
      
      # Agora é hora das duas apostas
      dados_aposta_back = bot.apostaBack(idMercado, selectionId, odds_back, stack_back)
      dados_aposta_lay = bot.apostaLaySP(idMercado, selectionId, stack_lay)
   
   