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

if __name__ == "__main__":
   print("Vai, malhado!")
   
   u, s, a = usuarioAPI, senhaAPI, APIKey
   api = BetfairAPI(usuario=u, senha=s, api_key=a)
   bot = Malhado(api )
   #corridaCavalosID = bot.obtemIdDoEsporte(eventTypeName="Horse Racing")
   print("ID=", bot.horseRacingID)
   bot.obtemListaDeCorridas()
   #bot.obtemListaCavalosWinInglaterra(horas=96)
   #print( bot.corridasWin )

   #for idx in range(len(bot.corridas)):
   #   print( "Partida# ",idx,": ID=",bot.corridas[idx]["event"]["id"], ", Nome=", bot.corridas[idx]["event"]["name"], ", timezone=",bot.corridas[idx]["event"]["timezone"], ", openDate=", bot.corridas[idx]["event"]["openDate"], ", marketCount=", bot.corridas[idx]["marketCount"] ) 
   
   #df = "2019-06-22T12:45:00.000Z"
   proxima_corrida = bot.corridas[0]["event"]["openDate"]
   print("Proxima corrida=", proxima_corrida)
   data_futura = datetime.strptime(proxima_corrida, '%Y-%m-%dT%H:%M:%S.%fZ')
   delta = data_futura - datetime.now()
   print("Sleep secs : {0}".format(delta.seconds))
   sleep(delta.seconds)
   print("Acordei!")
   
   #for idx in range(len(bot.corridasWin)):
   #   print( "Market# ", idx, " ID=", bot.corridasWin[idx]['marketId'], "Market Name=", bot.corridasWin[idx]['marketName'],", melhor=", bot.corridasWin[idx]['runners'][0]['runnerName'], "selecionId=", bot.corridasWin[idx]['runners'][0]['selectionId'] )
   
