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
   Obtem a lista de partidas que comecarao nos proximos trinta minutos.
   """
   def obtemListaDeCorridas(self, horas=24, minutos=0):
      import datetime
      now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
      future = (datetime.datetime.now() + datetime.timedelta(hours=horas, minutes=minutos)).strftime('%Y-%m-%dT%H:%M:%SZ')
      filtro=('{"filter":{"eventTypeIds":["' + self.horseRacingID + '"], '
         ' "marketStartTime":{"from":"' + now + '", "to":"' + future + '"}},'
         ' "marketCountries" : "GB" }')
      self.corridas = api.obtemTodosEventos(json_req=filtro) #Obtendo o Json das partidas

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
   """
   def obtemListaMercadosDoEvento(self, idEvento):
      filtro =('{"filter":{"eventIds":["' + idEvento + '"],"marketCountries":["GB"],"marketTypeCodes":["WIN"]},'\
                ' "sort":"FIRST_TO_START","maxResults":"5",\
                "marketProjection":["RUNNER_DESCRIPTION","EVENT"]}')
      mercados = api.obtemTodosMercadosDasPartidas(json_req=filtro)
      print("Mer=", mercados)
   
   """
   Pesquisando os preços da corrida em questão.
   """
   def obtemOddsDaCorrida(self, idMercado):
      filtro= '{ "marketIds": [' + idMercado + '], "priceProjection": { "priceData": ["EX_BEST_OFFERS"], "virtualise": "true" } }'
      odds = api.obtemOddsDosMercados(json_req=filtro)
      #print("Odds=", odds )
      #melhoresOdds = { odds[odds[idxRun]["runners"][idxSel]["selectionId"]]  :  odds[idxRun]["runners"][idxSel]["ex"]["availableToBack"][0]["price"]  for idxRun in range(len(odds))  for idxSel in range(len(odds[idxRun]["runners"])) if len(odds[idxRun]["runners"][idxSel]["ex"]["availableToBack"]) >= 1 }
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
      api.aposta(json_req=filtro)
      
   """
   Aposta Lay (contra) uma determinada seleção, com Starter Price. 
   """
   def apostaLaySP(self, idMercado, selectionId, stack_lay):
      filtro = '{"marketId": "' + idMercado + '",'\
               '"instructions": [ { "selectionId": "' + str(selectionId) + '", "handicap": "0", "side": "LAY", "orderType": "MARKET_ON_CLOSE", "marketOnCloseOrder": '\
               '{ "liability": "' + str(stack_lay) + '" } } ]}'
      api.aposta(json_req=filtro)
   
      
if __name__ == "__main__":
   print("Vai, malhado!")
   
   u, s, a = usuarioAPI, senhaAPI, APIKey
   api = BetfairAPI(usuario=u, senha=s, api_key=a)
   bot = Malhado(api )
   #corridaCavalosID = bot.obtemIdDoEsporte(eventTypeName="Horse Racing")
   print("ID=", bot.horseRacingID)
   bot.obtemListaCavalosWinInglaterra(horas=96)

   #for idx in range(len(bot.corridas)):
   #   print( "Partida# ",idx,": ID=",bot.corridas[idx]["event"]["id"], ", Nome=", bot.corridas[idx]["event"]["name"], ", timezone=",bot.corridas[idx]["event"]["timezone"], ", openDate=", bot.corridas[idx]["event"]["openDate"], ", marketCount=", bot.corridas[idx]["marketCount"] ) 
   
   #df = "2019-06-22T12:45:00.000Z"
   proxima_corrida = bot.corridasWin[0]["event"]["openDate"]   # Apenas a próxima corrida
   idMercado = bot.corridasWin[0]['marketId']
   nomeEvento = bot.corridasWin[0]['event']['name']
   print("Proxima corrida=", proxima_corrida)
   data_futura = datetime.strptime(proxima_corrida, '%Y-%m-%dT%H:%M:%S.%fZ')
   data_futura_1h = data_futura - timedelta(hours=1, minutes=0)   # Uma hora antes do jogo
   delta = data_futura - datetime.now()
   print("Sleep secs : {0}".format(delta.seconds))
   #sleep(delta.seconds)
   print("Acordei! Agora sao->", datetime.now())
   
   # Agora obtenho as odds da corrida acima (pelo ID)
   bot.obtemOddsDaCorrida(idMercado)
   selectionId = bot.OddsCorrida[idMercado][0]["runners"][0]['selectionId']
   #print("Selecion=", selectionId)
   nomeCavalo = [bot.corridasWin[0]['runners'][idxRunner]["runnerName"] for idxRunner in range(len(bot.corridasWin[0]['runners'])) if bot.corridasWin[0]['runners'][idxRunner]["selectionId"]==selectionId][0]
   odds_back = bot.OddsCorrida[idMercado][0]["runners"][0]['ex']['availableToBack'][0]['price']
   stack_lay = 20.0
   stack_back = round(stack_lay/odds_back,2)   # Retorno equilibrado com Lay
   print("{0} - Cavalo {1}, Lay com odds de {2} e stack de {3}, na corrida {4} ".format(datetime.now(), nomeCavalo, odds_back, stack_back, nomeEvento))
   
   # Agora é hora das duas apostas
   bot.apostaBack(idMercado, selectionId, odds_back, stack_back)
   bot.apostaLaySP(idMercado, selectionId, stack_lay)
   
   #for idx in range(len(bot.corridasWin)):
   #   print( "Market# ", idx, " ID=", bot.corridasWin[idx]['marketId'], "Market Name=", bot.corridasWin[idx]['marketName'],", melhor=", bot.corridasWin[idx]['runners'][0]['runnerName'], "selecionId=", bot.corridasWin[idx]['runners'][0]['selectionId'] )
   
