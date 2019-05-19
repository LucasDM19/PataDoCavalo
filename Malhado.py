from RestAPI import *
from Hush import *

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
   def obtemListaDeCorridas(self, horas=12, minutos=0):
      import datetime
      now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
      future = (datetime.datetime.now() + datetime.timedelta(hours=horas, minutes=minutos)).strftime('%Y-%m-%dT%H:%M:%SZ')
      filtro=('{"filter":{"eventTypeIds":["' + self.horseRacingID + '"], '
         ' "marketStartTime":{"from":"' + now + '", "to":"' + future + '"}},'
         ' "marketCountries" : "GB" }')
      self.corridas = api.obtemTodosEventos(json_req=filtro) #Obtendo o Json das partidas
      
      
   """
   As partidas relevantes sao apenas aquelas do GB. Todo o resto sera ignorado.
   """
   def filtraPartidasInglesas(self, pais="GB"):
      #print( [self.corridas[idx] for idx in range(len(self.corridas)) if self.corridas[idx]["event"]["countryCode"] == pais] )
      self.corridas = [self.corridas[idx] for idx in range(len(self.corridas)) if self.corridas[idx]["event"]["countryCode"] == pais]

if __name__ == "__main__":
   print("Vai, malhado!")
   
   u, s, a = usuarioAPI, senhaAPI, APIKey
   api = BetfairAPI(usuario=u, senha=s, api_key=a)
   bot = Malhado(api )
   #corridaCavalosID = bot.obtemIdDoEsporte(eventTypeName="Horse Racing")
   print("ID=", bot.horseRacingID)
   bot.obtemListaDeCorridas()
   bot.filtraPartidasInglesas(pais="AU")
   print( bot.corridas )
   
   #for idx in range(len(bot.corridas)):
   #   print( "Partida# ",idx,": ID=",bot.jPartidas[idx]["event"]["id"], ", Nome=", bot.jPartidas[idx]["event"]["name"], ", timezone=",bot.jPartidas[idx]["event"]["timezone"], ", openDate=", bot.jPartidas[idx]["event"]["openDate"], ", marketCount=", bot.jPartidas[idx]["marketCount"] ) 
      
   
   