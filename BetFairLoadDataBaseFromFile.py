#coding: utf-8
from Hush import caminhos_or, caminho_destino_bz2
from os import listdir
from os import path
import bz2
import json
from shutil import copyfile
import sqlite3
import operator # Para odenar um dicionário

def iniciaBanco(nome_banco):
   conn = sqlite3.connect(nome_banco)
   c = conn.cursor()

   c.execute('create table if not exists odds (RunnerId, RaceId, LastTradedPrice, PublishedTime)')
   c.execute('create table if not exists races (RaceId, MarketTime, InplayTimestamp, MarketName, MarketVenue)')
   c.execute('create table if not exists afs (RunnerId, RaceId, AdjustmentFactor, PublishedTime)')
   c.execute('create table if not exists runners (RunnerId, RaceId, RunnerName, WinLose, BSP)')
   c.execute('create table if not exists odds_position (RunnerId, RaceId, CurrentPrice, MinutesUntillRace)') # Odds por minuto
   return c, conn

def insere_bz2_sqlite(arquivo_bz2, arquivo):
   global c, conn
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
                print("Tem odds", odd['id'], race_id, odd['ltp'], time )
                c.execute("insert or replace into  odds values (?,?,?,datetime(?,'unixepoch'))", [odd['id'], race_id, odd['ltp'], time ])
         
         if 'marketDefinition' in obj['mc'][0]:
             md=obj['mc'][0]['marketDefinition']                
             
             if inplay_timestamp==0 and md['inPlay']==True:
               print("Tem races", race_id, md['marketTime'], inplay_timestamp,md['name'], md['venue'])
               inplay_timestamp=time        
               c.execute("insert or replace into races values (?,?,datetime(?,'unixepoch'),?,?)", [race_id, md['marketTime'], inplay_timestamp,md['name'], md['venue'] ])

             if md['inPlay']==False :
               #print("Tem afs", md['runners'][0]['id'], race_id, md['runners'][0]['adjustmentFactor'], time)
               for runner in md['runners']:
                  try:
                     c.execute("insert or replace into  afs values (?,?,?,datetime(?,'unixepoch'))", [runner['id'], race_id, runner['adjustmentFactor'], time ])
                  except KeyError:
                     pass
             
             if md['status']=='CLOSED':
               for runner in md['runners']:
                    print("Tem Runners", runner['id'], race_id, runner['name'],1 if runner['status']=='WINNER' else (0 if runner['status']=='LOSER' else -1), runner['bsp'] if 'bsp' in runner else -1 )
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
      except KeyError:
        print("CountryCode?", obj['mc'][0]['marketDefinition'] )
        x = 1/0
        pass
      except json.decoder.JSONDecodeError:
         pass

def verificaDiretorios():  
   #Verificando recursivamente os diretorios. Para quando encontra um arquivo.
   while( len(caminhos_or) > 0 ):
      caminho = caminhos_or.pop()
      for pasta in listdir(caminho):
         if(path.isfile(caminho+'\\'+pasta)):
            #print("Arquivo!", caminho+'\\'+pasta)
            #if(pasta == '1.166872140.bz2'): print("Arquivo!", caminho+'\\'+pasta)
            processa_bz2(arquivo_bz2=caminho+'\\'+pasta, arquivo=pasta)
         if(path.isdir(caminho+'\\'+pasta)):
            #print("dir=", caminho + '\\'+pasta)
            caminhos_or.append(caminho + '\\'+pasta)
   print("Carga completa")

def recriaIndices():
   global c, conn
   # Quando acaba tudo, cria (ou recria) os indices
   c.execute("DROP INDEX IF EXISTS idx_races_RaceId")
   c.execute("CREATE INDEX idx_races_RaceId ON races ( RaceId ASC )")
   c.execute("DROP INDEX IF EXISTS idx_runners_RaceId")
   c.execute("CREATE INDEX idx_runners_RaceId ON runners ( RaceId )")
   c.execute("DROP INDEX IF EXISTS idx_odds_RaceId")
   c.execute("CREATE INDEX idx_odds_RaceId ON odds ( RaceId ASC )")
   c.execute("DROP INDEX IF EXISTS idx_odds_RunnerId")
   c.execute("CREATE INDEX idx_odds_RunnerId ON odds ( RunnerId )")
   c.execute("DROP INDEX IF EXISTS idx_odds_RunnerId_PublishedTime")
   c.execute("CREATE INDEX idx_odds_RunnerId_PublishedTime ON odds (RunnerId, PublishedTime)")
   c.execute("DROP INDEX IF EXISTS idx_races_RaceId_MarketTime")
   c.execute("CREATE INDEX idx_races_RaceId_MarketTime ON races (RaceId, MarketTime)")
   conn.commit() # Agora sim grava tudo

def removeDuplicatas():
   global c, conn
   # Eliminar duplicatas
   for nome_tabela in ['races', 'runners', 'odds', 'afs']: # Todas as tabelas do BD
      print("Agora arrumando tabela", nome_tabela)
      c.execute("DROP TABLE IF EXISTS temp_table")
      c.execute("CREATE TABLE temp_table as SELECT DISTINCT * FROM " + nome_tabela)
      c.execute("DELETE FROM " + nome_tabela)
      c.execute("INSERT INTO " + nome_tabela + " SELECT * FROM temp_table")
      conn.commit() # Agora sim grava tudo
   print("Duplicatas removidas")

def consolidaOdds():
    global c, conn
    print("Agora agrupando odds por minuto")
    dados_corridas = {} # Agrupa por todas as corridas, por precaução
    lista_corridas = []
    odds_ordenadas = None # Por questão de lógica
    race_id_ant = None # Para o último minuto da corrida anterior
    c_grava = conn.cursor() # Para inserir os dados
    c.execute("""SELECT odds.RaceId, odds.RunnerId, odds.LastTradedPrice, odds.PublishedTime,
                   Cast (( JulianDay(races.MarketTime) - JulianDay(odds.PublishedTime) ) * 24 * 60 As Integer ) as Dif_Min
                   FROM odds, races
                   WHERE odds.RaceId = races.RaceId
                     AND odds.RaceId NOT IN (SELECT RaceId FROM odds_position)
                   ORDER BY odds.RaceId, odds.PublishedTime """) # Pergunta: quais corridas que tem odds, mas não tem dados consolidados?
    while True: 
        row = c.fetchone()
        if row == None: break  # Acabou o sqlite
        race_id, runner_id, last_traded_price, published_time, dif_min = row
        if( race_id not in dados_corridas ):
            lista_participantes = {}
            if( race_id_ant is not None ): # ùblicar último minuto da corrida anterior
                print("\n Aguenta1")
                for c_id in odds_ordenadas:
                    print("Agora sim. Tome!", c_id, race_id_ant, odds_ordenadas[c_id], published_time, dif_min_ant  )
                    c_grava.execute("insert or replace into odds_position values (?,?,?,?)", [c_id, race_id_ant, odds_ordenadas[c_id], dif_min_ant ])
                conn.commit()
            race_id_ant = race_id
            dif_min_ant = None # Salvo minuto anterior, para ver saltos
            #print("Zerou Ant=", dif_min_ant, race_id)
            c2 = conn.cursor() # Quais são todos os cavalos participantes dessa corrida?
            c2.execute(""" SELECT * FROM runners WHERE runners.RaceId = ? """, (race_id,) )       
            while True: 
                row2 = c2.fetchone()
                if row2 == None: break  # Acabou o sqlite
                runner_id2, race_id2, runner_name, WinLose, BSP = row2
                lista_participantes[runner_id2] = -1.01 # Odd inicial
            dados_corridas[race_id] = lista_participantes # Dictionaty para cada corrida
        if( dif_min_ant is None or dif_min != dif_min_ant ): # Teve quebra de minuto, ou é o primeiro minuto
            if(dif_min_ant is not None): 
                for min_silencio in range(dif_min_ant+1,dif_min): # Sem fluxo de odds novas - Tudo igual
                    for c_id in odds_ordenadas:
                        print("Agora sim. Silêncio...", c_id, race_id, odds_ordenadas[c_id], published_time, min_silencio, dif_min, dif_min_ant )
                        c_grava.execute("insert or replace into odds_position values (?,?,?,?)", [c_id, race_id_ant, odds_ordenadas[c_id], min_silencio ])
                        x = 1/0
                    conn.commit()
            if( odds_ordenadas is not None and dif_min_ant is not None):
                print("\n Aguenta2")
                for c_id in odds_ordenadas:
                    print("Agora sim. Tome!", c_id, race_id, odds_ordenadas[c_id], published_time, dif_min_ant  )
                    c_grava.execute("insert or replace into odds_position values (?,?,?,?)", [c_id, race_id, odds_ordenadas[c_id], dif_min_ant ])
                conn.commit()
            dif_min_ant = dif_min
        #if(len(dados_corridas) ==2 ): x = 1/0
        dados_corridas[race_id][runner_id] = last_traded_price #Atualiza as odds dessa corrida
        odds_ordenadas = dict( sorted( dados_corridas[race_id].items(), key=operator.itemgetter(1),reverse=False ) ) # Para ficar igual no site
        #for c_id in odds_ordenadas:
        #    print("Agora sim. Tome!", c_id, race_id, odds_ordenadas[c_id], published_time, dif_min  )
    if( odds_ordenadas is not None):
        print("\n Aguenta3")
        for c_id in odds_ordenadas:
            print("Agora sim. Tome!", c_id, race_id, odds_ordenadas[c_id], published_time, dif_min_ant  ) # O último minuto da última corrida
            c_grava.execute("insert or replace into odds_position values (?,?,?,?)", [c_id, race_id, odds_ordenadas[c_id], dif_min_ant ])
        conn.commit()    
    
def fazLimpeza():
   global c, conn
   # E ainda faz aquela limpeza geral
   c.execute("VACUUM")
   conn.commit() # Agora sim grava tudo

if __name__ == '__main__':   
   c, conn = iniciaBanco('bf_gb_win_full.db')
   #verificaDiretorios()
   #recriaIndices()
   #removeDuplicatas()
   consolidaOdds()
   #fazLimpeza()