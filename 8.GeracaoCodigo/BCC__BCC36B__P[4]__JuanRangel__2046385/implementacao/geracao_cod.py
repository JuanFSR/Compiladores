# from urllib.request import build_opener
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
global variaveis_declaradas
global nome_escopo_alocada

escopo = ''
pilha_bloco_saida = []
variaveis_declaradas = []
nome_escopo_alocada = []

def encontra_variavel_declarada(nome_variavel):
    variavel_encontrada = ''

    # Primeiro procuro no escopo local e depois no global
    if nome_variavel+escopo in nome_escopo_alocada:
        # Pegar a posição onde se encontra esse valor e acessar as variaveis declaradas
        # print("NOME ESCOPO ALOCADA", nome_escopo_alocada)
        # print(nome_escopo_alocada.index(nome_variavel+escopo))

        variavel_encontrada  = variaveis_declaradas[nome_escopo_alocada.index(nome_variavel+escopo)]
        # print("Variavel declarada", variavel_declaracao_encontrada)

    else:
        if nome_variavel+'global' in nome_escopo_alocada:
            variavel_encontrada  = variaveis_declaradas[nome_escopo_alocada.index(nome_variavel+'global')]
            # Pegar a posição onde se encontra esse valor e acessar as variaveis declaradas
            # print("NOME ESCOPO ALOCADA", nome_escopo_alocada)
            # print(nome_escopo_alocada.index(nome_variavel+'global'))
    
    return variavel_encontrada

def gera_codigo(arvore):
    global builder
    global modulo
    global pilha_bloco_saida
    global variaveis_declaradas
    global escopo
    global nome_escopo_alocada

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
                    print("------------------------------------")
                    print("Variável Declarada", variavel_declarada)
                    print("------------------------------------")
                    variavel_declarada.align = 4

                    # Adiciona na lista de variáveis declaradas
                    variaveis_declaradas.append(variavel_declarada)
                    nome_escopo_alocada.append( variavel['Lexema'].values[0] + escopo)
                    
                    zero_declaracao = ir.Constant(ir.IntType(32), 0)
                    
                    builder.store(zero_declaracao, variavel_declarada) 



                # Defino o retorno da função onde a variável foi declarada
        elif ('declaracao_funcao' in no.label):
            linha = no.label.split(':')
            linha = linha[1]


            # procuro a função declarado nessa linha
            funcao_encontrada = tabela_simbolos[tabela_simbolos['linha'] == linha]
            # nome_funcao = funcao_encontrada['Lexema']
            # nome_funcao = nome_funcao[0]


            print("------------------------")                
            print("FUNCAO ENCONTRADA")                
            print(funcao_encontrada['Lexema'].values[0])      
            escopo = funcao_encontrada['Lexema'].values[0]

            # # Declara o retorno da função
            # retorno_funcao = ir.Constant(ir.IntType(32), 0)

            print("TIPO DA FUNÇÃO")
            print(funcao_encontrada['Tipo'])

            # Cria a função, porém é necessário verificar o tipo da função
            if ('inteiro' == funcao_encontrada['Tipo'].values[0]):
                criacao_funcao = ir.FunctionType(ir.IntType(32), ())

            # Declara a função
            declaracao_funcao = ir.Function(modulo, criacao_funcao, name=funcao_encontrada['Lexema'].values[0])
            
            # Declara os blocos de entrada e saída
            bloco_entrada = declaracao_funcao.append_basic_block('entry')    
            bloco_saida = declaracao_funcao.append_basic_block('exit')  

            # Coloca os blocos de saída em uma pilha
            pilha_bloco_saida.append(bloco_saida)
            # print("bloco saida", pilha_bloco_saida)

            # Adiciona o bloco de entrada
            builder = ir.IRBuilder(bloco_entrada)

        elif ('retorna' in no.label):
            linha = no.label.split(':')
            linha = linha[1]

            retorno_encontrado = tabela_simbolos[tabela_simbolos['Lexema'] == 'retorna']
            print("LINHA", linha)
            print("RETORNO TABELA")
            print(retorno_encontrado)
            
            retorno_valor = retorno_encontrado['valor'].values[0]
            print("VALOR RETORNADO", retorno_valor)

            # Retira do topo da pilha
            print("TAMANHO LISTA", len(pilha_bloco_saida))

            # Pego o último da pilha de blocos de saída
            topo_bloco_saida = pilha_bloco_saida.pop()

            # Crio um salto para o bloco de saída
            builder.branch(topo_bloco_saida)

            # Adiciona o bloco de saída
            builder.position_at_end(topo_bloco_saida)

            variavel_retornada_encontrada = ''
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
        
        elif ('acao' == no.label):
            # print(len(no.children), no.children[1].label)

            if len(no.children) > 1:
                # Identifica se é uma atribuição
                if (no.children[1].label == ':='):
                    
                    # x := y, representa o nome da variável x
                    nome_variavel_recebendo = no.children[0].label

                    # representa o nome da variável y
                    nome_variavel_atribuida = no.children[2].label
                    
                    print("-----------------------------")
                    print("-----------------------------")
                    print("-----------------------------")
                    print("Atribuição de valora para variável")
                    print("%s := %s" % (nome_variavel_recebendo, nome_variavel_atribuida))

                    # Procuro o tipo da variável atribuída
                    tipo_variavel_atribuida = tabela_simbolos[tabela_simbolos['Lexema'] == nome_variavel_atribuida]
                    
                    if len(tipo_variavel_atribuida) > 0:
                        tipo_variavel_atribuida = tipo_variavel_atribuida['Tipo'].values[0]
                    else:
                        # Verifico se é um valor 
                        if nome_variavel_atribuida.isdigit():
                            print("É UM DIGITOOOOOOOOOOO")
                            # Verifico se é inteiro ou flutuante
                            if '.' in nome_variavel_atribuida:
                                tipo_variavel_atribuida = 'flutuante'
                            else:
                                tipo_variavel_atribuida = 'inteiro'


                    print("TIPO VARIAVEL ATRIBUIDA", tipo_variavel_atribuida)
                    print("TIPO VARIAVEL DECLARADAS", variaveis_declaradas)

                    variavel_declaracao_encontrada = ''
                    # Primeiro procuro no escopo local e depois no global
                    if nome_variavel_recebendo+escopo in nome_escopo_alocada:
                        # Pegar a posição onde se encontra esse valor e acessar as variaveis declaradas
                        print("NOME ESCOPO ALOCADA", nome_escopo_alocada)
                        print(nome_escopo_alocada.index(nome_variavel_recebendo+escopo))

                        variavel_declaracao_encontrada  = variaveis_declaradas[nome_escopo_alocada.index(nome_variavel_recebendo+escopo)]
                        print("Variavel declarada", variavel_declaracao_encontrada)

                    else:
                        if nome_variavel_recebendo+'global' in nome_escopo_alocada:
                            variavel_declaracao_encontrada  = variaveis_declaradas[nome_escopo_alocada.index(nome_variavel_recebendo+'global')]
                            # Pegar a posição onde se encontra esse valor e acessar as variaveis declaradas
                            print("NOME ESCOPO ALOCADA", nome_escopo_alocada)
                            print(nome_escopo_alocada.index(nome_variavel_recebendo+'global'))
                            

                    
                    # variavel = variaveis_declaradas[nome_variavel_recebendo+escopo]
                    # variavel_alocada.append(variavel)

                    print("VARIAVEL ALOCADA", variavel_declaracao_encontrada)
                    builder.store(ir.Constant(ir.IntType(32), nome_variavel_atribuida), variavel_declaracao_encontrada)

                    # if len(variavel_alocada) >= 1:
                    #     pass
                    # else:
                    #     variavel_alocada = variaveis_declaradas[nome_variavel_recebendo+'global']

                    # print("VARIAVEL ALOCADA --- ", variavel_alocada)
                    # if len(variavel_alocada) > 0:
                    #     builder.store(ir.Constant(ir.IntType(32), nome_variavel_atribuida), variavel)

                    # nome_variavel_recebendo = str(nome_variavel_recebendo)
                    # nome_variavel_atribuida = int(nome_variavel_atribuida)

                    # if tipo_variavel_atribuida == 'inteiro':
                    #     print(nome_variavel_recebendo, nome_variavel_atribuida)


                    # else:
                    #     nome_variavel_atribuida = float(nome_variavel_atribuida)
                    #     builder.store(ir.Constant(ir.FloatType(), nome_variavel_atribuida), nome_variavel_recebendo)


        print(no.label)

        gera_codigo(no)

def main():
    # Chamando análise semantica
    global modulo
    global arvore_podada    
    global tabela_simbolos
    
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