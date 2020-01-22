from Hush import caminhos_or, caminho_destino_bz2
from os import listdir
from os import path
import bz2
import json
from shutil import copyfile
import sqlite3

conn = sqlite3.connect('bf_gb_win_teste.db')
c = conn.cursor()

c.execute('create table if not exists odds (RunnerId, RaceId, LastTradedPrice, PublishedTime)')
c.execute('create table if not exists races (RaceId, MarketTime, InplayTimestamp, MarketName, MarketVenue)')
c.execute('create table if not exists afs (RunnerId, RaceId, AdjustmentFactor, PublishedTime)')
c.execute('create table if not exists runners (RunnerId, RaceId, RunnerName, WinLose, BSP)')

def insere_bz2_sqlite(arquivo_bz2, arquivo):
   with bz2.open(arquivo_bz2, "rt") as bz_file:
      md=json.loads( next(bz_file)  )['mc'][0]['marketDefinition']
      race_id=arquivo.replace('.bz2','')
      #if(race_id == '1.153066480.bz2'): print("Tem!", arquivo)
      inplay_timestamp=0

      for linha in bz_file:
         obj=json.loads( linha  )
         race_id=obj['mc'][0]['id']
         time=obj['pt']/1000.0
         if 'rc' in obj['mc'][0]:
             for odd in obj['mc'][0]['rc']:
               c.execute("insert or replace into  odds values (?,?,?,datetime(?,'unixepoch'))", [odd['id'], race_id, odd['ltp'], time ])
         
         if 'marketDefinition' in obj['mc'][0]:
             md=obj['mc'][0]['marketDefinition']                
             
             if inplay_timestamp==0 and md['inPlay']==True:
                 inplay_timestamp=time        
                 c.execute("insert or replace into races values (?,?,datetime(?,'unixepoch'),?,?)", [race_id, md['marketTime'], inplay_timestamp,md['name'], md['venue'] ])

             if md['inPlay']==False :
                 for runner in md['runners']:
                     try:
                        c.execute("insert or replace into  afs values (?,?,?,datetime(?,'unixepoch'))", [runner['id'], race_id, runner['adjustmentFactor'], time ])
                     except KeyError:
                        pass
             
             if md['status']=='CLOSED':
                 for runner in md['runners']:
                     c.execute("insert or replace into runners values (?,?,?,?,?)", [runner['id'], race_id, runner['name'],1 if runner['status']=='WINNER' else (0 if runner['status']=='LOSER' else -1), runner['bsp'] if 'bsp' in runner else -1 ])

      conn.commit()

def processa_bz2(arquivo_bz2, arquivo):
   with bz2.open(arquivo_bz2, "rt") as bz_file:
      try:
         obj=json.loads( next(bz_file)  )
         marketType=obj['mc'][0]['marketDefinition']['marketType']
         countryCode=obj['mc'][0]['marketDefinition']['countryCode']
         if marketType=='WIN' and countryCode=='GB':
            #copyfile(arquivo_bz2, caminho_destino_bz2 +'\\'+arquivo) #Copiar fisicamente em algum lugar
            insere_bz2_sqlite(arquivo_bz2, arquivo)
      except json.decoder.JSONDecodeError:
         pass
      
#Verificando recursivamente os diretorios. Para quando encontra um arquivo.
while( len(caminhos_or) > 0 ):
   caminho = caminhos_or.pop()
   for pasta in listdir(caminho):
      if(path.isfile(caminho+'\\'+pasta)):
         print("Arquivo!", caminho+'\\'+pasta)
         #if(pasta == '1.166872140.bz2'): print("Arquivo!", caminho+'\\'+pasta)
         processa_bz2(arquivo_bz2=caminho+'\\'+pasta, arquivo=pasta)
      if(path.isdir(caminho+'\\'+pasta)):
         #print("dir=", caminho + '\\'+pasta)
         caminhos_or.append(caminho + '\\'+pasta)
print("Carga completa")

# Eliminar duplicatas
for nome_tabela in ['races', 'runners', 'odds', 'afs']: # Todas as tabelas do BD
   c.execute("DROP TABLE IF EXISTS temp_table")
   c.execute("CREATE TABLE temp_table as SELECT DISTINCT * FROM " + nome_tabela)
   c.execute("DELETE FROM " + nome_tabela)
   c.execute("INSERT INTO " + nome_tabela + " SELECT * FROM temp_table")
   conn.commit() # Agora sim grava tudo
print("Duplicatas removidas")
   
# Quando acaba tudo, cria (ou recria) os indices
c.execute("DROP INDEX IF EXISTS idx_races_RaceId")
c.execute("CREATE INDEX idx_races_RaceId ON races ( RaceId ASC )")
c.execute("DROP INDEX IF EXISTS idx_runners_RaceId")
c.execute("CREATE INDEX idx_runners_RaceId ON runners ( RaceId )")
c.execute("DROP INDEX IF EXISTS idx_odds_RaceId")
c.execute("CREATE INDEX idx_odds_RaceId ON odds ( RaceId ASC )")
c.execute("DROP INDEX IF EXISTS idx_odds_RunnerId")
c.execute("CREATE INDEX idx_odds_RunnerId ON odds ( RunnerId )")
conn.commit() # Agora sim grava tudo