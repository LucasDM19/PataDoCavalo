from os import listdir
import bz2
import json
from shutil import copyfile
import sqlite3

conn = sqlite3.connect('bf_gb_win_2019.db')
c = conn.cursor()

def separa_win():
    caminho='c:\\t\\betfair'
    caminho_destino='C:\\t\\gbwin'
    for pasta in listdir(caminho):
        for arquivo in listdir(caminho+'\\'+pasta):
            arquivo_bz2=caminho+'\\'+pasta+'\\'+arquivo
            with bz2.open(arquivo_bz2, "rt") as bz_file:
                obj=json.loads( next(bz_file)  )
                marketType=obj['mc'][0]['marketDefinition']['marketType']
                countryCode=obj['mc'][0]['marketDefinition']['countryCode']
                if marketType=='WIN' and countryCode=='GB':
                        copyfile(arquivo_bz2, caminho_destino+'\\'+arquivo)

caminho='C:\\t\\gbwin2'
for arquivo in listdir(caminho):
    with bz2.open(caminho+'\\'+arquivo, "rt") as bz_file:
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

                if md['inPlay']==False:
                    for runner in md['runners']:
                        c.execute("insert or replace into  afs values (?,?,?,datetime(?,'unixepoch'))", [runner['id'], race_id, runner['adjustmentFactor'], time ])
                
                if md['status']=='CLOSED':
                    for runner in md['runners']:
                        c.execute("insert or replace into runners values (?,?,?,?,?)", [runner['id'], race_id, runner['name'],1 if runner['status']=='WINNER' else (0 if runner['status']=='LOSER' else -1), runner['bsp'] if 'bsp' in runner else -1 ])
                                           
        conn.commit()
        #print(inplay_timestamp)

# Quando acaba tudo, cria os indices
c.execute("CREATE INDEX idx_races_RaceId ON races ( RaceId ASC )")
c.execute("CREATE INDEX idx_runners_RaceId ON runners ( RaceId )")
c.execute("CREATE INDEX idx_odds_RaceId ON odds ( RaceId ASC )")
c.execute("CREATE INDEX idx_odds_RunnerId ON odds ( RunnerId )")