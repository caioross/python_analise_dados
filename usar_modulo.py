import meu_modulo as mm

print(mm.soma(2,6))
print(mm.saudacao('Caio',66))

valor_a = int(input('Insira o primeiro valor:'))
valor_b = int(input('Insira o segundo valor:'))

print(mm.soma(valor_a,valor_b))

usuarioNasc = int(input('\nInforme o ano em que nasceu: '))
usuarioAtual = int(input('\nInforme o ano atual: '))
idade = mm.calcularIdade(usuarioNasc,usuarioAtual)
print(f'Você tem {idade} anos')

#print(f'Você tem { mm.calcularIdade(usuarioNasc,usuarioAtual)} anos')


