import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


#máximo da banca em um uma única aposta
MAX_BANCA=0.33
COMISSAO=0.065


df=pd.read_csv('out_dev_full_47.csv')

#retira o pl zero
df=df[df.pl!=0]

#Faz o ajuste da odds como se fosse um back
df.pl=np.where(df.pl>0, (1-COMISSAO)/(df.odds_lay-1), -1)

#Só deixa corrida cujs distancia seja inferior a 20
df=df[df.dist<20]

#campos adicionais
df['D1']=np.log(1+df.dist)
df['D2']=np.log(1+df.D1)
df['D3']=np.log(1+df.D2)
df['Q1']=np.log(1+df.qtd_cav)
df['Q2']=np.log(1+df.Q1)
df['Q3']=np.log(1+df.Q2)
df['A1']=np.log(1+abs(df.af) )
df['A2']=np.log(1+df.A1)
df['A3']=np.log(1+df.A2)
df['F30a']=np.log(1+df.f_odd_lay_30m)
df['F30b']=np.log(1+df.F30a)
df['F30c']=np.log(1+df.F30b)
df['F31a']=np.log(1+df.f_odd_lay_31m)
df['F31b']=np.log(1+df.F31a)
df['F31c']=np.log(1+df.F31b)
df['F35a']=np.log(1+df.f_odd_lay_35m)
df['F35b']=np.log(1+df.F35a)
df['F35c']=np.log(1+df.F35b)
df['F36a']=np.log(1+df.f_odd_lay_36m)
df['F36b']=np.log(1+df.F36a)
df['F36c']=np.log(1+df.F36b)
df['F41a']=np.log(1+df.f_odd_lay_41m)
df['F41b']=np.log(1+df.F41a)
df['F41c']=np.log(1+df.F41b)
df['F45a']=np.log(1+df.f_odd_lay_45m)
df['F45b']=np.log(1+df.F45a)
df['F45c']=np.log(1+df.F45b)
df['F46a']=np.log(1+df.f_odd_lay_46m)
df['F46b']=np.log(1+df.F46a)
df['F46c']=np.log(1+df.F46b)
df['F51a']=np.log(1+df.f_odd_lay_51m)
df['F51b']=np.log(1+df.F51a)
df['F51c']=np.log(1+df.F51b)
df['F56a']=np.log(1+df.f_odd_lay_56m)
df['F56b']=np.log(1+df.F56a)
df['F56c']=np.log(1+df.F56b)
df['F60a']=np.log(1+df.f_odd_lay_1h)
df['F60b']=np.log(1+df.F60a)
df['F60c']=np.log(1+df.F60b)

#print([np.where(np.isnan(df))] ) # Para acessar o indice: df.iloc[[19289]]
#print( df.iloc[[4]] )

#todas as colunas exceto a ultima, que o pl
todas_colunas=df.loc[:, df.columns != 'pl'].columns

qtd_registros = len(df)
frac_treino = 0.75 # Qual a fracao para treino
qtd_train = int(frac_treino * qtd_registros)
qtd_test = qtd_registros - qtd_train

#Nossa função fit recebe um um string tamanho 30 de 0s e 1s, e retorna a lucratividade da combinação
def somaLog(codigo_genetico):
    global df, todas_colunas
    
    #Quais colunas que entraram na regressão
    colunas=','.join([ todas_colunas[i] for i,e in enumerate([int(c) for c in codigo_genetico]) if e])
    
    #Fitra o df baseado nas colunas
    df_=df[(colunas+',pl').split(',')]

    SLs=[] 
    for i in range(100):
        #Embaralha o dataframe baseado no random_state i 
        df_=df_.sample(frac=1, random_state=i)

        #Divide em 7 mil linhas para teste e o restante treinamento
        df_test, df_train =df_[:qtd_test],df_[qtd_test:]

        #Os Xs são todas as colunas exceto a PL que será o Y
        X_train,Y_train = df_train.loc[:,(df_train.columns!='pl') ], df_train.pl
        X_test, Y_test  = df_test.loc[:,(df_test.columns!='pl') ], df_test.pl

        #Treina a regressão os dados de treinamento
        reg=LinearRegression().fit(X_train,Y_train)
    
        #Veifica a lucratividade nos dados de teste
        SLs=[sum(np.log(1+y*(y_pred if y_pred<MAX_BANCA else MAX_BANCA )) for y_pred,y in zip(reg.predict(X_test),Y_test) if y_pred>0.00 ) ]
        #SLs+=[sum(np.log(1+y*y_pred) for y_pred,y in zip(reg.predict(X_test),Y_test) if y_pred>=-0.1 ) ]
    #print(SLs)
    #Mostra a lucrativida média e colunas selecionadas que deram origem a essa lucratividade
    return np.mean(SLs)

def exibeCoeficientes(campos_inclui):
   global df
   SomaLogs=[] 
   qtd_colunas_x = len(df.columns)-1 # Tem apenas um Y
   qtd_registros = len(df)
   prop_treino = 0.9999 # Quanto fica para treino. O resto será teste
   qtd_treino = int(qtd_registros*prop_treino)
   qtd_teste = qtd_registros-qtd_treino
   colunas = [col for col in df.columns if col in campos_inclui]

   #Fitra o df baseado nas colunas
   df=df[colunas]
   
   for i in range(100):
      #Embaralha o dataframe, apartir de um estado predefindo
      df=df.sample(frac=1.0, random_state=i)
      df_teste, df_treino = df[:qtd_teste], df[qtd_teste:]
      
      #Os Xs são todas as colunas exceto a PL que será o Y
      X_treino, Y_treino = df_treino.loc[:,(df_treino.columns!='pl')], df_treino.pl
      X_teste, Y_teste = df_teste.loc[:,(df_teste.columns!='pl')], df_teste.pl
      
      # Treina a regressão com os dados de treinamento
      reg=LinearRegression().fit(X_treino, Y_treino)
      print('\n Coeficientes #'+str(i)+':')
      for idx_c in range(len(reg.coef_)): 
         print("Coef do campo", df.columns[idx_c], ":", reg.coef_[idx_c] )

#Configurações
TAM_POP=50  #Tamano da população (número para para não zuar o barraco, ok :)
N_BITS=len(todas_colunas)  #Qtd de 0s e 1s do cromossomo
QTD_GERACOES = 800
TAXA_DE_REPRODUCAO=0.95
TAXA_DE_MUTACAO=0.05



#Gera a população incial
pop=[]
for _ in range(TAM_POP):
    code=''.join([ str(np.random.randint(2)) for i in range(N_BITS)  ])
    pop+=[ {'code':code, 'fit':somaLog(code) } ]



#Evolução da população
for n_gera in range(QTD_GERACOES):
    codes=[]
    
    #Para cada 2 indivudos gera novos 2 codigos genéticos a através do cruzamentos dada taxa de reprodução
    for pai,mae in zip(pop[:TAM_POP//2],pop[TAM_POP//2:]):
        corte=1+np.random.randint(N_BITS-1)
        if np.random.random()<TAXA_DE_REPRODUCAO:
            codes+=[pai['code'][:corte]+mae['code'][corte:corte+(N_BITS//2)]+pai['code'][corte+(N_BITS//2):],
                    mae['code'][:corte]+pai['code'][corte:corte+(N_BITS//2)]+mae['code'][corte+(N_BITS//2):] ]
        else:
            codes+=[pai['code'], mae['code']]

    #Para cada codigo genetico, toma bit a bit, troca os 0s por 1s, ou vice e versa dada taxa de mutação
    codes=[''.join([str(int(not(int(bit)))) if np.random.random()<TAXA_DE_MUTACAO  else bit for bit in code]) for code in codes ]


    #Adiciona os individuos a população, nesse momento pop tem 2*TAM_POP individuos
    pop+=[ {'code':code, 'fit':somaLog(code)} for code in codes]


    #Seleção por metodos do torneio para que pop tenha exatos TAM_POP individuos 
    pop=[ind1 if ind1['fit']>ind2['fit'] else ind2 for ind1,ind2 in zip(pop[:TAM_POP],pop[TAM_POP:])]

    #Embaralha os individuos da população
    np.random.shuffle(pop)
    
    print('Gera#:',n_gera,'Melhor fit:', max([ ind['fit'] for ind in pop ] ), 'Individuo:', [ [todas_colunas[i] for i,e in enumerate([int(c) for c in ind['code'] ]) if e] for ind in pop if ind['fit']==max([ ind['fit'] for ind in pop ]) ][0] )

#Verifica a melhor combinação
print('Melhor combinação de colunas:', ','.join([ todas_colunas[i] for i,e in enumerate([int(c) for c in sorted(pop, key=lambda x: -x['fit'])[0]['code']]) if e]))
exibeCoeficientes(campos_inclui=[ todas_colunas[i] for i,e in enumerate([int(c) for c in sorted(pop, key=lambda x: -x['fit'])[0]['code']]) if e]) # Exibo coeficientes