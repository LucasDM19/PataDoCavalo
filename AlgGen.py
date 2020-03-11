
class AlgoritmoGenetico():
    def __init__(self, df):
        self.df = df
        self.tamanho_pop = 50 # Apenas chute
        
    def inicializaPopulacao(self):
        