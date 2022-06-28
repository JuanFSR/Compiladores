# from urllib.request import build_opener
from curses.ascii import isdigit
from unicodedata import name
from unittest import expectedFailure
import pandas as pd
# from pyrsistent import T
import tpp_semantic
import numpy as np
from llvmlite import ir
from llvmlite import binding as llvm

global modulo
global arvore_podada
global tabela_simbolos
global builder

global escopo 
global pilha_bloco_saida
global pilha_loop_validacao
global pilha_loop
global variaveis_declaradas
global nome_escopo_alocada
global lista_declaracao_funcao
global lista_escopo
global parametros_lista

global escreva_inteiro
global escreva_float
global leia_inteiro
global leia_float

escopo = ''

pilha_loop = []
pilha_loop_validacao = []
pilha_bloco_saida = []
variaveis_declaradas = []
nome_escopo_alocada = []
lista_declaracao_funcao = []
lista_escopo = []
parametros_lista = []

def realiza_operacoes(expressao_esquerda_temp, expressao_direita_temp, operacao_sinal):
    print("-----------------------------")  
    print("REALIZANDO OPERAÇÃO", operacao_sinal)  

    # Cria variável temporária
    # retorno_temp = builder.alloca(ir.IntType(32), name='retorno_temp')
    # retorno_temp.align = 4

    if '+' == operacao_sinal:
        # Realiza soma
        print(expressao_esquerda_temp, expressao_direita_temp)
        expressao_resultado = builder.add(expressao_esquerda_temp, expressao_direita_temp)
        print("SOMA")
        # builder.store(retorno_temp, soma_expressao)

    elif '-' == operacao_sinal:
        # Realiza subtração
        expressao_resultado = builder.sub(expressao_esquerda_temp, expressao_direita_temp, name='subtracao')
        print("SUBTRAÇÃO")
    
    elif '*' == operacao_sinal:
        # Realiza multiplicação
        expressao_resultado = builder.mul(expressao_esquerda_temp, expressao_direita_temp, name='multiplicacao')
        print("MULTIPLICAÇÃO")
    
    elif '/' == operacao_sinal:
        # Realiza divisão
        expressao_resultado = builder.sdiv(expressao_esquerda_temp, expressao_direita_temp, name='divisao')
        print("DIVISAO")

    print("-----------------------------")  
    return expressao_resultado
    # builder.ret(expressao_resultado)


def encontra_expressao(expressao):
    operacoes_lista = ['+', '-', '*', '/']
    operacao = False

    # Em alguma momento será necessário verificar
    for filhos_expressao in expressao.children:
        if (len(filhos_expressao.children)) > 0:
            if filhos_expressao.children[0].label in operacoes_lista:
                operacao = True
        else:
            if filhos_expressao.label in operacoes_lista:
                operacao = True

    if (operacao):
        print("AQUI")
        if len(expressao.children) == 3:
            print("LEN EXPRESSAO", len(expressao.children[1].children))
            if len(expressao.children[1].children) == 0:
                return expressao.children[0].label, expressao.children[1].label, expressao.children[2].label
            else:
                return expressao.children[0].label, expressao.children[1].children[0].label, expressao.children[2].label

def procura_comparaca(no_ate):
    repita = no_ate.parent

    posicao_filho = 0
    posicao_ate = 0
    for filho_repita in repita.children:
        if filho_repita.label == 'ATE':
            posicao_ate = posicao_filho
        posicao_filho += 1
    
    quantidade_filhos_comparacao = (len(repita.children)-1) - posicao_ate

    if quantidade_filhos_comparacao == 3:
        return repita.children[posicao_ate+1].label, repita.children[posicao_ate+2].children[0].label, repita.children[posicao_ate+3].label

def declara_operacoes_condicionais(if_verdade, if_falso, se):
    comparacao_lista = ['<', '>']
    filhos = []

    print("PERCORRENDO TODOS OS FILHOS DO SE")
    posicao_filho = 0
    for filho in se.children:
        print(filho.label)
        if filho.label in comparacao_lista:
            print(f"Filho a esquerda {se.children[posicao_filho-1].label} Filho a direita{se.children[posicao_filho+1].label}")
            filhos.append(se.children[posicao_filho-1].label)
            filhos.append(se.children[posicao_filho+1].label)
            
            print("FILHOS", filhos)
            # Verificar se são variáveis ou são digitos
            for filho_adjacente in filhos:

                if (filho_adjacente.isdigit()):
                    # É um valor
                    print("FILHO ADJACENTE É UM VALOR")
                else:
                    # É uma variável
                    print("FILHO ADJACENTE É UMA VARIAVEL")

        posicao_filho += 1
            


def encontra_funcao_declarada(nome_funcao):
    funcao_encontrada = ''

    print("--------------------------------------------")
    print(lista_escopo)
    print(lista_declaracao_funcao)
    print("--------------------------------------------")

    if nome_funcao == 'principal':
        nome_funcao = 'main'

    # Primeiro procuro no escopo local e depois no global
    if nome_funcao in lista_escopo:
        # Pegar a posição onde se encontra esse valor e acessar as variaveis declaradas
        funcao_encontrada  = lista_declaracao_funcao[lista_escopo.index(nome_funcao)]
        print("Funcaoo declarada", funcao_encontrada)

    return funcao_encontrada

def encontra_variavel_declarada(nome_variavel):
    variavel_encontrada = ''

    # Primeiro procuro no escopo local e depois no global
    if nome_variavel+escopo in nome_escopo_alocada:
        # Pegar a posição onde se encontra esse valor e acessar as variaveis declaradas
        # print("NOME ESCOPO ALOCADA", nome_escopo_alocada)
        # print(nome_escopo_alocada.index(nome_variavel+escopo))

        print("LOCAL")
        variavel_encontrada  = variaveis_declaradas[nome_escopo_alocada.index(nome_variavel+escopo)]
        # print("Variavel declarada", variavel_declaracao_encontrada)

    else:
        if nome_variavel+'global' in nome_escopo_alocada:
            print("GLOBAL")
            variavel_encontrada  = variaveis_declaradas[nome_escopo_alocada.index(nome_variavel+'global')]
            # Pegar a posição onde se encontra esse valor e acessar as variaveis declaradas
            # print("NOME ESCOPO ALOCADA", nome_escopo_alocada)
            # print(nome_escopo_alocada.index(nome_variavel+'global'))
    
    return variavel_encontrada

def gera_codigo(arvore):
    global builder
    global modulo
    global pilha_bloco_saida
    global pilha_loop_validacao
    global pilha_loop
    global variaveis_declaradas
    global escopo
    global nome_escopo_alocada

    global escreva_inteiro
    global escreva_float
    global leia_inteiro
    global leia_float
    global parametros_lista


    linha = 0

    for no in arvore.children:
        if ('declaracao_variaveis' in no.label):
            linha = no.label.split(':')
            linha = linha[1]
            # print("LINHA ONDE AS VARIÁVEIS FORAM DECLARADAS %s" % linha)

            # procuro na tabela de símbolos
            variavel = tabela_simbolos[tabela_simbolos['linha'] == linha]
            print('VARIVEL %s' % variavel['Lexema'].values[0])
            print(variavel['escopo'].values[0])

            # Verifico o escopo da variável
            if 'global' == str(variavel['escopo'].values[0]):
                if 'inteiro' == str(variavel['Tipo'].values[0]):
                    # Declara variável global
                    variavel_global = ir.GlobalVariable(modulo, ir.IntType(32), variavel['Lexema'].values[0])
                    variavel_global.initializer = ir.Constant(ir.IntType(32), 0)
                    variavel_global.linkage = "common"
                    variavel_global.align = 4

                    variaveis_declaradas.append(variavel_global)
                    nome_escopo_alocada.append( variavel['Lexema'].values[0] + 'global')
            else:
                # Caso não seja no escopo global, verifico o tipo da variável
                print("VARIAVEL A SER DECLARADA NA FUNÇÃO MAIN")
                print(variavel)
                print('-----------------')
                print(variavel['valor'])
                print('-----------------')

                # Aloca a variável com valor zero
                if ('inteiro' == variavel['Tipo'].values[0]):
                    variavel_declarada = builder.alloca(ir.IntType(32), name=variavel['Lexema'].values[0])
                    variavel_declarada.initalizer = ir.Constant(ir.IntType(32), 0)
                    
                    variavel_declarada.linkage = "common"
                    variavel_declarada.align = 4
                    
                    print("------------------------------------")
                    print("Variável Declarada", variavel_declarada)
                    print("------------------------------------")

                    # Adiciona na lista de variáveis declaradas
                    variaveis_declaradas.append(variavel_declarada)
                    nome_escopo_alocada.append( variavel['Lexema'].values[0] + escopo)
                    
                    # zero_declaracao = ir.Constant(ir.IntType(32), 0)
                    
                    # builder.store(zero_declaracao, variavel_declarada) 



                # Defino o retorno da função onde a variável foi declarada
        elif ('declaracao_funcao' in no.label):
            linha = no.label.split(':')
            linha = linha[1]


            # procuro a função declarado nessa linha
            funcao_encontrada = tabela_simbolos[tabela_simbolos['linha'] == linha]
            # nome_funcao = funcao_encontrada['Lexema']
            # nome_funcao = nome_funcao[0]


            escopo = funcao_encontrada['Lexema'].values[0]

            # # Declara o retorno da função
            # retorno_funcao = ir.Constant(ir.IntType(32), 0)

            # print("TIPO DA FUNÇÃO")
            print("-----------------------------")
            print(f"Declarando a função{funcao_encontrada['Lexema'].values[0]} do tipo {funcao_encontrada['Tipo']}")
            # print(funcao_encontrada['Lexema'].values[0])   
            # print(funcao_encontrada['Tipo'])
            print("-----------------------------")   

            # Cria a função, porém é necessário verificar o tipo da função
            if ('inteiro' == funcao_encontrada['Tipo'].values[0]):
                if len(funcao_encontrada['parametros'].values[0]) == 0:
                    criacao_funcao = ir.FunctionType(ir.IntType(32), ())

                elif len(funcao_encontrada['parametros'].values[0]) == 1:
                    criacao_funcao = ir.FunctionType(ir.IntType(32), ir.IntType(32))
                
                else:
                    criacao_funcao = ir.FunctionType(ir.IntType(32), [ir.IntType(32), ir.IntType(32)])

            # Declara a função
            if funcao_encontrada['Lexema'].values[0] == 'principal':
                declaracao_funcao = ir.Function(modulo, criacao_funcao, name='main')
                lista_escopo.append('main')
                lista_declaracao_funcao.append(declaracao_funcao)
            
            else:
                # Necessário verifica se tem parâmetros
                print("LINHA TABELA")
                print(funcao_encontrada['parametros'].values[0])

                declaracao_funcao = ir.Function(modulo, criacao_funcao, name=funcao_encontrada['Lexema'].values[0])
                lista_escopo.append(funcao_encontrada['Lexema'].values[0])
                lista_declaracao_funcao.append(declaracao_funcao)
            
            parametros_funcao = funcao_encontrada['parametros'].values[0]
            # Passa por todos os argumentos e declara eles como argumentos
            quantidade_parametros = 0
            
            for parametros in parametros_funcao:
                for param_nome, _ in parametros.items():
                    print("-----------------------------") 
                    print("PARAMETRO NOME",param_nome) 
                    print("-----------------------------") 
                    declaracao_funcao.args[quantidade_parametros].name = param_nome
                    quantidade_parametros += 1

            parametros_lista.append(declaracao_funcao)
            # Declara os blocos de entrada e saída
            bloco_entrada = declaracao_funcao.append_basic_block('entry')    
            bloco_saida = declaracao_funcao.append_basic_block('exit')  

            # Coloca os blocos de saída em uma pilha
            pilha_bloco_saida.append(bloco_saida)
            # print("bloco saida", pilha_bloco_saida)

            # Adiciona o bloco de entrada
            builder = ir.IRBuilder(bloco_entrada)

        elif ('retorna' in no.label):
            print("-----------------------------")
            print("Retornando")
            print("-----------------------------")

            linha = no.label.split(':')
            linha = linha[1]

            retorno_encontrado = tabela_simbolos[tabela_simbolos['Lexema'] == 'retorna']
            # print("LINHA", linha)
            # print("RETORNO TABELA")
            # print(retorno_encontrado)
            
            retorno_valor = retorno_encontrado['valor'].values[0]
            # print("VALOR RETORNADO", retorno_valor)

            # Retira do topo da pilha
            # print("TAMANHO LISTA", len(pilha_bloco_saida))

            # Pego o último da pilha de blocos de saída
            topo_bloco_saida = pilha_bloco_saida.pop()
            # print("LISTA BLOCO SAÍDA", topo_bloco_saida)

            # print("CHEGOU AQUIIIIII", pilha_bloco_saida)
            # Crio um salto para o bloco de saída
            builder.branch(topo_bloco_saida)

            # Adiciona o bloco de saída
            builder.position_at_end(topo_bloco_saida)

            variavel_retornada_encontrada = ''

            # Está retornando apena uma variável ou um valor
            if len(no.children) ==1 :
                # Cria o valor de retorno, verificar ainda o retorno correto de cada função
                if ('inteiro' == retorno_encontrado['Tipo'].values[0]):
                    for ret in retorno_valor:
                        for variavel_retornada, tipo_retornado in ret.items():
                            print(f"Variavel retornada {variavel_retornada} tipo retornado {tipo_retornado}")
                            variavel_retornada_encontrada = variavel_retornada

                elif ('float' == retorno_encontrado['Tipo'].values[0]):
                    pass

                
                # Verifico se é um dígito
                if variavel_retornada_encontrada.isdigit():
                    print("ESTOU RETORNANDO UM DÍGITO")
                    retorno_zero = ir.Constant(ir.IntType(32), variavel_retornada)
                    builder.ret(retorno_zero)
                else:
                    # Estou retornando uma variável
                    print("ESTOU RETORNANDO UMA VARIÁVEL")
                    declaracao = encontra_variavel_declarada(variavel_retornada_encontrada)
                    builder.ret(builder.load(declaracao, ""))
        
            else:
            # Está retornando uma expressão
                print("ESTÁ RETORNANDO UMA EXPRESSÃO")
                expressao_esquerda, operacao_sinal, expressao_direita = encontra_expressao(no)
                print("-----------------------------")
                print(f"EXPRESSAO {expressao_esquerda} {operacao_sinal} {expressao_direita}")
                print("-----------------------------")

                # Verificar se as variáveis utilizadas para realizar a soma no retorno foram passadas por parâmetro
                print("-----------------------------")
                print("LINHA RETORNO", retorno_valor)
                print("-----------------------------")

                
                
                # if 'a' in retorno_variaveis:
                #     print("ESTÁÁÁÁÁÁÁÁ", retorno_variaveis)

                if (expressao_esquerda.isdigit()):
                    # Primeiramente é necessário encontrar as duas variáveis utilizadas na operação
                    expressao_esquerda_temp = ir.Constant(ir.IntType(32), expressao_esquerda)
                    expressao_direita_temp = ir.Constant(ir.IntType(32), expressao_direita)

                else:
                    print("-----------------------------")
                    print("OS DOIS SÃO VARIÁVEIS")
                    print("-----------------------------")
                    
                    funcao_variaveis_parametro = []
                    funcao_tabela_simbolos = tabela_simbolos[(tabela_simbolos['Lexema'] == escopo) & (tabela_simbolos['funcao'] == 'S')]
                    parametros_funcao_tabela_simbolos = funcao_tabela_simbolos['parametros'].values[0]

                    print("LINHA DECLARACAO FUNÇÃO", parametros_funcao_tabela_simbolos)

                    # Adiciona apenas o nome dos parametros recebidos na função em uma lista
                    for param_tabela_simbolos in parametros_funcao_tabela_simbolos:
                        for retorno_nome_tabela_simbolos, _ in param_tabela_simbolos.items():
                            funcao_variaveis_parametro.append(retorno_nome_tabela_simbolos)
                        
                    parametros_argumentos = parametros_lista.pop()

                    # Verifica se as variáveis utilizadas na operação são as passadas por parametro
                    if expressao_esquerda in funcao_variaveis_parametro:
                        posicao_variavel = funcao_variaveis_parametro.index(expressao_esquerda)
                        print("POSICAO DO PARAMETRO UTILIZADO NA OPERACAO", posicao_variavel)
                        expressao_esquerda_temp = parametros_argumentos.args[posicao_variavel]
                    else:
                        variavel_expressao_esquerda = encontra_variavel_declarada(expressao_esquerda)
                        expressao_esquerda_temp = builder.load(variavel_expressao_esquerda, name=str(expressao_esquerda) + '_temp')

                    if expressao_direita in funcao_variaveis_parametro:
                        posicao_variavel_direita = funcao_variaveis_parametro.index(expressao_direita)
                        expressao_direita_temp = parametros_argumentos.args[posicao_variavel_direita]
                    else:
                        variavel_expressao_direita = encontra_variavel_declarada(expressao_direita)
                        # Fazer o load das valores em uma variável temporária
                        expressao_direita_temp = builder.load(variavel_expressao_direita, name=str(expressao_direita) + '_temp')


                print("-----------------------------")
                print(f"DECLARANDO DIGITOS E PROCURANDO VARIAVEIS {expressao_esquerda_temp} {operacao_sinal} {expressao_direita_temp}")
                print("-----------------------------")

                resultado_op = realiza_operacoes(expressao_esquerda_temp, expressao_direita_temp, operacao_sinal)
                builder.ret(resultado_op)


        elif ('acao' == no.label):
            # print(len(no.children), no.children[1].label)
            if len(no.children) > 1: 
                if (no.children[1].label == ':='):
                    # -----------------------------------
                    # Essa atribuição pode ser a chamada de uma função ou uma operação
                    # -----------------------------------
                    # Verificar se o primeiro valor da atribuição é uma função ou não
                    verifica_nome_funcao = no.children[2].label

                    pesquisa_nome_funcao = tabela_simbolos[(tabela_simbolos['Lexema'] == verifica_nome_funcao) & (tabela_simbolos['funcao'] == 'S')]

                    if len(pesquisa_nome_funcao) > 0:
                        # Significa que é a chamada de uma função
                        print("-----------------------------")
                        print("É UMA CHAMADA DE FUNÇÃO")
                        print("CHAMANDO FUNÇÃO", no.children[2].label)
                        print("-----------------------------")

                        # Encontra a variável que recebe a chamada de função
                        recebe_chamada_funcao = encontra_variavel_declarada(no.children[0].label)

                        # Encontra função
                        encontra_chamada_funcao = encontra_funcao_declarada(no.children[2].label)
                        operador_esquerdo_declaracao = encontra_variavel_declarada(no.children[3].label)
                        operador_direito_declaracao = encontra_variavel_declarada(no.children[4].label)

                        chamada_funcao = builder.call(encontra_chamada_funcao, [builder.load(operador_esquerdo_declaracao), builder.load(operador_direito_declaracao)])
                        builder.store(chamada_funcao, recebe_chamada_funcao)

                    else:

                        # Identifica se é uma atribuição
                        if len(no.children) == 3:
                            
                            # x := y, representa o nome da variável x
                            nome_variavel_recebendo = no.children[0].label

                            # representa o nome da variável y
                            nome_variavel_atribuida = no.children[2].label
                            
                            print("-----------------------------")
                            print("Atribuição de valor para variável")
                            print("%s := %s" % (nome_variavel_recebendo, nome_variavel_atribuida))
                            print("-----------------------------")

                            # Procuro o tipo da variável atribuída
                            tipo_variavel_atribuida = tabela_simbolos[tabela_simbolos['Lexema'] == nome_variavel_atribuida]
                            
                            if len(tipo_variavel_atribuida) > 0:
                                tipo_variavel_atribuida = tipo_variavel_atribuida['Tipo'].values[0]
                            else:
                                # Verifico se é um valor 
                                if nome_variavel_atribuida.isdigit():
                                    # Verifico se é inteiro ou flutuante
                                    if '.' in nome_variavel_atribuida:
                                        tipo_variavel_atribuida = 'flutuante'
                                    else:
                                        tipo_variavel_atribuida = 'inteiro'


                            # print("TIPO VARIAVEL ATRIBUIDA", tipo_variavel_atribuida)
                            # print("TIPO VARIAVEL DECLARADAS", variaveis_declaradas)

                            variavel_declaracao_encontrada = ''
                            # Primeiro procuro no escopo local e depois no global
                            if nome_variavel_recebendo+escopo in nome_escopo_alocada:
                                # Pegar a posição onde se encontra esse valor e acessar as variaveis declaradas
                                # print("NOME ESCOPO ALOCADA", nome_escopo_alocada)
                                # print(nome_escopo_alocada.index(nome_variavel_recebendo+escopo))

                                variavel_declaracao_encontrada  = variaveis_declaradas[nome_escopo_alocada.index(nome_variavel_recebendo+escopo)]
                                # print("Variavel declarada", variavel_declaracao_encontrada)

                            else:
                                if nome_variavel_recebendo+'global' in nome_escopo_alocada:
                                    variavel_declaracao_encontrada  = variaveis_declaradas[nome_escopo_alocada.index(nome_variavel_recebendo+'global')]
                                    # Pegar a posição onde se encontra esse valor e acessar as variaveis declaradas
                                    # print("NOME ESCOPO ALOCADA", nome_escopo_alocada)
                                    # print(nome_escopo_alocada.index(nome_variavel_recebendo+'global'))
                                    
                            # print("VARIAVEL ALOCADA", variavel_declaracao_encontrada, nome_variavel_atribuida)
                            

                            # Verifica se o valor que está sendo atribuído é uma variável
                            valor_encontrado_atribuindo = encontra_variavel_declarada(nome_variavel_atribuida)

                            if valor_encontrado_atribuindo == '':
                                # Significa que o valor que está sendo atribuído não é uma variável
                                builder.store(ir.Constant(ir.IntType(32), nome_variavel_atribuida), variavel_declaracao_encontrada)
                            else:
                                # Significa que o valor que está sendo atribuído é uma variável
                                variavel_temporaria = builder.load(valor_encontrado_atribuindo, "")
                                builder.store(variavel_temporaria, variavel_declaracao_encontrada)

                        # Significa que é uma atribuição com uma operação matemática
                        else:
                            # Pegar a variável que estará recebendo a operação
                            nome_variavel_recebendo = encontra_variavel_declarada(no.children[0].label)
                            # nome_variavel_load = builder.load(nome_variavel_recebendo)


                            # Verifica o primeira parametro da operação, para ver se é uma variável ou um digito
                            nome_variavel_atribuida_esquerda = no.children[2].label
                            operacao_sinal = no.children[3].label
                            nome_variavel_atribuida_direita = no.children[4].label
                            
                            # Verifica para variável a esquerda da expressao (esquerda + direita)
                            if (nome_variavel_atribuida_esquerda.isdigit()):
                                nome_variavel_atribuida_esquerda_declarada = ir.Constant(ir.IntType(32), name=nome_variavel_atribuida_esquerda)
                                

                            else:
                                nome_variavel_atribuida_esquerda_encontrada = encontra_variavel_declarada(nome_variavel_atribuida_esquerda)
                                nome_variavel_atribuida_esquerda_declarada = builder.load(nome_variavel_atribuida_esquerda_encontrada, name=nome_variavel_atribuida_esquerda + '_temp')

                            # Verifica para variável a direita da expressao (esquerda + direita)
                            if (nome_variavel_atribuida_direita.isdigit()):
                                
                                nome_variavel_atribuida_direita_declarada = ir.Constant(ir.IntType(32), name=str(nome_variavel_atribuida_direita))
                                

                            else:
                                nome_variavel_atribuida_direita_declarada_encontrada = encontra_variavel_declarada(nome_variavel_atribuida_direita)
                                nome_variavel_atribuida_direita_declarada = builder.load(nome_variavel_atribuida_direita_declarada_encontrada, name=nome_variavel_atribuida_direita + '_temp')
                                
                            # Chama função que vai declarar a operação
                            operacao_declarada = realiza_operacoes(nome_variavel_atribuida_esquerda_declarada, nome_variavel_atribuida_direita_declarada, operacao_sinal)

                            builder.store(operacao_declarada, nome_variavel_recebendo)



                # Gera código da estrutura condicional se/senão
                else:
                    # Caso o filho seja um 'se', é necessário criar o código se uma estrutura condicional
                    if (no.children[0].label == 'se'):
                        print("SE")

                        # Tenho que procurar, utilizando o escopo atual, a declaração dessa função
                        declaracao_funcao_encontrada = encontra_funcao_declarada(escopo)
                        # print("DECLARACAO FUNCAO", declaracao_funcao_encontrada)
                        # Crio os blocos de entrada e saída do 'se'
                        if_verdade_1 = declaracao_funcao_encontrada.append_basic_block('iftrue_1')
                        if_falso_1 = declaracao_funcao_encontrada.append_basic_block('iffalse_1')
                        
                        if_saida_1 = declaracao_funcao_encontrada.append_basic_block('ifend1')
                        # Adiciono o bloco de saída na pilha
                        pilha_bloco_saida.append(if_saida_1)

                        # Percorrer apenas os filhos do 'se', até encontrar uma compação
                        declara_operacoes_condicionais(if_verdade_1, if_falso_1, no.children[0])


        elif ('senão' == no.label):
            # Retirar o bloco de saída do topo da pilha
            print("------------------------------")
            print("SENÃO")
            print(pilha_bloco_saida)
            print("------------------------------")
            # if_falso_1 = declaracao_funcao_encontrada.append_basic_block('iffalse_1')
            topo_bloco_saida = pilha_bloco_saida.pop()
            builder.branch(topo_bloco_saida)

        # Caso encontre o token Repita
        elif ('repita' == no.label):
            print("------------------------------")
            print("REPITA")
            print("------------------------------")

            # Cria os blocos de repetição
            loop = builder.append_basic_block('loop')
            loop_validacao = builder.append_basic_block('loop_val')
            loop_end = builder.append_basic_block('loop_end')

            # Adiciona na pila de blocos finais
            pilha_loop_validacao.append(loop_validacao)
            pilha_loop.append(loop)
            pilha_bloco_saida.append(loop_end)

            # Pula para o laço do loop
            builder.branch(loop)

            # Posiciona no inicio do bloco do loop
            builder.position_at_end(loop)

        elif ('ATE' == no.label):
            print("------------------------------")
            print("ATE")
            print("------------------------------")
        
            validacao = pilha_loop_validacao.pop()
            builder.branch(validacao)

            builder.position_at_end(validacao)

            saida = pilha_bloco_saida.pop()
            loop_inicial = pilha_loop.pop()

            comparacao_esquerda, comparacao_sinal, comparacao_direita = procura_comparaca(no)
            print("------------------------------")
            print(f"Comparacao esquerda {comparacao_esquerda}, comparacao sinal {comparacao_sinal}, comparacao_direita {comparacao_direita}")
            print("------------------------------")

            if (comparacao_direita.isdigit()):
                # Declara o uma constante que será utilizada para comparação
                comparacao_valor = ir.Constant(ir.IntType(32), int(comparacao_direita))

                print("COMPARACAO VALOR", comparacao_valor)

            # Procura a variável nas variáveis declaradas para realizar o load
            comparacao_variavel = encontra_variavel_declarada(comparacao_esquerda)
            print("------------------------------")
            print("VARIAVEL DECLARADA ENCONTRADA", comparacao_variavel)
            print("------------------------------")

            
            if ('=' == comparacao_sinal):
                expressao = builder.icmp_signed('==', builder.load(comparacao_variavel), comparacao_valor, name='expressao_igualdade')
            
            # Verifica se a expressão é verdadeira ou não
            builder.cbranch(expressao, loop_inicial, saida)

            # Define o que será executado após o fim do loop
            builder.position_at_end(saida)

            # # Cria um saltp para o bloco de saída
            # bloco_saida_funcao = pilha_bloco_saida.pop()
            # builder.position_at_end(bloco_saida_funcao)

        elif ('escreva' == no.label):
            # Verificar se vai ser necessário escrever qualquer coisa que não seja uma variável ou número, como uma expressaõ por exemplo
            valor_escrita = no.children[0].label

            print("------------------------------")
            print("VALOR ESCRITA", valor_escrita)
            print("------------------------------")
            if (valor_escrita.isdigit()):
                valor_escrita_constante = ir.Constant(ir.IntType(32), int(valor_escrita))
                builder.call(escreva_inteiro, args=[valor_escrita_constante])

            else:
                # Significa que está escrevendo uma variável
                variavel_escrever = encontra_variavel_declarada(valor_escrita)
                builder.call(escreva_inteiro, args=[builder.load(variavel_escrever)])

        elif ('leia' == no.label):
            print("LEIA A VARIÁVEL", no.children[0].label)
            print("------------------------------")
            
            # Variável onde será guardado o conteúdo lido
            variavel_leia = no.children[0].label

            variavel_recebe_leitura = encontra_variavel_declarada(variavel_leia)
            leia_funcao_chamada = builder.call(leia_inteiro, args=[])
            builder.store(leia_funcao_chamada, variavel_recebe_leitura, align=4)

                


        print(no.label)

        gera_codigo(no)

def main():
    # Chamando análise semantica
    global modulo
    global arvore_podada    
    global tabela_simbolos
    global escreva_inteiro
    global escreva_float
    global leia_inteiro
    global leia_float
    
    arvore_podada, tabela_simbolos = tpp_semantic.main()

    # # Ordenar por linha
    # linha_valores = tabela_simbolos['linha'].values
    # linha_valores = linha_valores.astype(int)

    # tabela_simbolos['linha'] = linha_valores
    # tabela_simbolos_ordenada = tabela_simbolos.sort_values(by=['linha'])

    print('------------------------------------')
    print("Geração Código")

    llvm.initialize()
    llvm.initialize_all_targets()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    # Cria módulo
    modulo = ir.Module('modulo_geracao_cod.bc')
    modulo.triple = llvm.get_process_triple()
    target = llvm.Target.from_triple(modulo.triple)
    target_machine = target.create_target_machine()
    modulo.data_layout = target_machine.target_data

    escreva_inteiro_funcao = ir.FunctionType(ir.VoidType(), [ir.IntType(32)])
    escreva_inteiro = ir.Function(modulo, escreva_inteiro_funcao, "escrevaInteiro")

    escreva_float_funcao = ir.FunctionType(ir.VoidType(), [ir.FloatType()])
    escreva_float = ir.Function(modulo, escreva_float_funcao, "escrevaFlutuante")

    leia_inteiro_funcao = ir.FunctionType(ir.IntType(32), [])
    leia_inteiro = ir.Function(modulo, leia_inteiro_funcao, "leiaInteiro")

    leia_float_funcao = ir.FunctionType(ir.FloatType(), [])
    leia_float = ir.Function(modulo, leia_float_funcao, "leiaFlutuante")

    # Chama função que gera o código llvm
    gera_codigo(arvore_podada)

    arquivo = open('modulo_geracao_cod.ll', 'w')
    arquivo.write(str(modulo))
    arquivo.close()

    print('------------------------------------')
    print('Código gerado')
    print(modulo)


if __name__ == "__main__":
    main()