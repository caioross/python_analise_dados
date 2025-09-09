class Carro:
    def __init__(self, modelo, cor):
        self.modelo = modelo
        self.cor = cor
        self.velocidade = 0 # o carro começa parado

    def acelerar(self, incremento):
        self.velocidade += incremento
        print(f'O {self.modelo} acelerou para {self.velocidade} Km/h.')

    def desacelerar(self, decremento):
        self.velocidade -= decremento
        print(f'O {self.modelo} desacelerou para {self.velocidade} Km/h.')


# criando um objeto carro
meu_carro = Carro('Sz Jimny','Amarelo')
outro_carro = Carro('Fusca', 'Preto')

#usando os metodos
meu_carro.acelerar(20)
meu_carro.acelerar(20)
meu_carro.acelerar(20)
meu_carro.desacelerar(10)
    