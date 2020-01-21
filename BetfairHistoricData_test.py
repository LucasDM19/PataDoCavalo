from os import listdir
from os import path
import bz2
import json
from shutil import copyfile
import sqlite3

conn = sqlite3.connect('D:\\Python\\Codes\\PataDoCavalo\\bf_gb_win_2009.db')
c = conn.cursor()

c.execute('create table if not exists odds (RunnerId, RaceId, LastTradedPrice, PublishedTime)')
c.execute('create table if not exists races (RaceId, MarketTime, InplayTimestamp, MarketName, MarketVenue)')
c.execute('create table if not exists afs (RunnerId, RaceId, AdjustmentFactor, PublishedTime)')
c.execute('create table if not exists runners (RunnerId, RaceId, RunnerName, WinLose, BSP)')

def insere_bz2_sqlite(arquivo_bz2, arquivo):
   with bz2.open(arquivo_bz2, "rt") as bz_file:
      md=json.loads( next(bz_file)  )['mc'][0]['marketDefinition']
      race_id=arquivo.replace('.bz2','')
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
   caminho_destino = 'D:\\Users\\lucas\\Documents\\Malhado_Arquivos_Temp\\output'
   with bz2.open(arquivo_bz2, "rt") as bz_file:
      try:
         obj=json.loads( next(bz_file)  )
         marketType=obj['mc'][0]['marketDefinition']['marketType']
         countryCode=obj['mc'][0]['marketDefinition']['countryCode']
         if marketType=='WIN' and countryCode=='GB':
               #copyfile(arquivo_bz2, caminho_destino+'\\'+arquivo)
               insere_bz2_sqlite(arquivo_bz2, arquivo)
      except json.decoder.JSONDecodeError:
         pass
      

caminhos_or= ['D:\\Users\\lucas\\Downloads\\data_Betfair\\' ,]
max_niveis=500000  # Controle recursividade
nivel = 0
achou=False
while( (nivel <= max_niveis) and (achou==False) ):
   caminho = caminhos_or.pop()
   for pasta in listdir(caminho):
      if(path.isfile(caminho+'\\'+pasta)):
         #achou=True
         print("Arquivo!", caminho+'\\'+pasta)
         processa_bz2(arquivo_bz2=caminho+'\\'+pasta, arquivo=pasta)
      if(path.isdir(caminho+'\\'+pasta)):
         #print("dir=", caminho + '\\'+pasta)
         caminhos_or.append(caminho + '\\'+pasta)
         nivel += 1

   