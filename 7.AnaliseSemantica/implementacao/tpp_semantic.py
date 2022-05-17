from matplotlib.axis import Axis
from sqlalchemy import values
import tppparser
import pandas as pd

global escopo
escopo = 'global'
pd.set_option('display.max_columns', None)

def encontra_expressao_retorno(retorna, lista_retorno):
    lista_retorno = lista_retorno
    retorno_dict = {}
    tipo_retorno = ''
    indice = ''

    for ret in retorna.children:
        if ret.label == 'numero':
            # print("Encontra indice")
            indice = ret.children[0].children[0].label 
            # print(indice)
            tipo_retorno = ret.children[0].label

            if (tipo_retorno == 'NUM_INTEIRO'):
                tipo_retorno = 'inteiro'
            
            elif (tipo_retorno == 'NUM_FLUTUANTE'):
                tipo_retorno = 'flutuante'

            retorno_dict[indice] = tipo_retorno
            lista_retorno.append(retorno_dict)

            print("ENCONTRA INDICE RETORNO %s  %s" % (tipo_retorno, indice))
            return lista_retorno

        elif ret.label == 'ID':
            print("ENCONTREI UMA VARIAVEL %s" % ret.children[0].label)
            indice = ret.children[0].label
            tipo_retorno = 'parametro'

            retorno_dict[indice] = tipo_retorno
            lista_retorno.append(retorno_dict)

            return lista_retorno

        lista_retorno = encontra_expressao_retorno(ret, lista_retorno)
    
    return lista_retorno

def encontra_valores_retorno(retorna, retorno):
    retorno = retorno


    for ret in retorna.children:
        expressoes = ['expressao_aditiva', 'expressao_multiplicativa', ]
        if (ret.label in expressoes):
            retorno = encontra_expressao_retorno(ret, retorno)
            # print("AQUIIIIIIIIIIIIIIIIIIIIIIII")
            # print(retorno)
            return retorno
        
        encontra_valores_retorno(ret, retorno)

    return retorno

def encontra_tipo_nome_parametro(parametro, tipo, nome):
    tipo = tipo
    nome = nome
    
    for param in parametro.children:
        # print("PARAM LABELLL %s" % param.label)

        if param.label == 'INTEIRO':
            tipo = param.children[0].label
            return tipo, nome
        
        elif param.label == 'FLUTUANTE':
            tipo = param.children[0].label
            return tipo, nome

        if param.label == 'id':
            nome = param.children[0].label
            return tipo, nome
        
        tipo, nome = encontra_tipo_nome_parametro(param, tipo, nome)
    return tipo, nome

def encontra_indice_retorno(expressao):
    indice = ''
    tipo_retorno = ''

    for filhos in expressao.children:
        if filhos.label == 'numero':
            # print("Encontra indice")
            indice = filhos.children[0].children[0].label 
            # print(indice)
            tipo_retorno = filhos.children[0].label

            if (tipo_retorno == 'NUM_INTEIRO'):
                tipo_retorno = 'inteiro'
            
            elif (tipo_retorno == 'NUM_PONTO_FLUTUANTE'):
                tipo_retorno = 'inteiro'

            # print("ENCONTRA INDICE RETORNO %s  %s" % (tipo_retorno, indice))
            return tipo_retorno, indice

        elif filhos.label == 'ID':
            # print("ENCONTREI UMA VARIAVEL %s" % filhos.children[0].label)
            indice = filhos.children[0].label
            tipo_retorno = 'parametro'

            return tipo_retorno, indice

        tipo_retorno,indice = encontra_indice_retorno(filhos)
    
    return tipo_retorno,indice

def verifica_dimensoes(tree, dimensao, indice_1, indice_2):
    # Verifica sub-árvore da variável para verificar suas dimensões
    indice_1 = indice_1
    indice_2 = indice_2
    dimensao = dimensao

    # print("DIMENSAO, TAM_DIM_1, TAM_DIM_2 --- dentro do verifica dimensões")
    # print(dimensao, indice_1, indice_2)

    for filho in tree.children:

        if (filho.label == 'indice'):
            # Posso verificar se o filho 0 do indice também é índice
            # Se for, quer dizer que tem mais de uma dimensão
            if (filho.children[0].label == 'indice'):
                # print("TEM 2 DIMENSOES")
                print("LABEL EXPRESSAO %s" % filho.children[0].children[1].label)
                dimensao = 2
                _, indice_1 = encontra_indice_retorno(filho.children[0].children[1])
                _, indice_2 = encontra_indice_retorno(filho.children[2])
                return dimensao, indice_1, indice_2
            
            else:
                # print("TEM 1 DIMENSAO")
                dimensao = 1
                _, indice_1 = encontra_indice_retorno(filho.children[1])
                indice_2 = 0
                return dimensao, indice_1, indice_2

        dimensao, indice_1, indice_2 = verifica_dimensoes(filho, dimensao, indice_1, indice_2)
    return dimensao, indice_1, indice_2
    

def encontra_dados_funcao(declaracao_funcao, tipo, nome_funcao, parametros, retorno_tipo_valor, tipo_retorno, linha_retorno):
    tipo = tipo 
    nome_funcao = nome_funcao 
    parametros = parametros
    tipo_retorno = tipo_retorno
    linha_retorno = linha_retorno
    retorno_tipo_valor = retorno_tipo_valor

    global escopo
    
    # print("TIPO %s, NOME %s, PARAMETROS %s, RETORNO %s" % (tipo, nome_funcao, parametros, retorno))

    for filho in declaracao_funcao.children:
        # print("PASSANDO PELA DECLARACAO FUNCAO %s" % filho.label)
        if (filho.label == 'tipo'):
            tipo = filho.children[0].children[0].label

        elif (filho.label == 'lista_parametros'):
            if (filho.children[0].label == 'vazio'):
                parametros = 'vazio'
            else:
                print("TEM UM PARAMETRO OU MAIS")
            
        elif (filho.label == 'cabecalho'):
            nome_funcao = filho.children[0].children[0].label
            escopo = nome_funcao
        
        elif ('retorna' in filho.label):

            retorno_tipo_valor = encontra_valores_retorno(filho, [])
            print("RETORNOOOOOooo")
            print(retorno_tipo_valor)

            linha_retorno = filho.label.split(':')
            linha_retorno = linha_retorno[1]
            token = filho.children[0].label
            retorno = ''

            # tipo_retorno, retorno_tipo_valor = encontra_indice_retorno(filho.children[2])
            tipo_retorno = 'vazio'


            return tipo, nome_funcao, parametros, retorno_tipo_valor, tipo_retorno, linha_retorno

        tipo, nome_funcao, parametros, retorno_tipo_valor, tipo_retorno, linha_retorno = encontra_dados_funcao(filho, tipo, nome_funcao, parametros, retorno_tipo_valor, tipo_retorno, linha_retorno)

    return tipo, nome_funcao, parametros, retorno_tipo_valor, tipo_retorno, linha_retorno

def encontra_parametro_funcao(no, parametros):

    parametros = parametros
    parametro = {}

    for n in no.children:
        if (no.label == 'parametro'):
            # print("ENTRE AQUI")
            tipo, nome = encontra_tipo_nome_parametro(no, '', '')
            # print("TIPO %s NOME %s" % (tipo, nome))

            parametro[nome] = tipo

            # print("PARAMETRO DICIONARIO 2")
            # print(parametro)
            parametros.append(parametro)

            return parametros
        encontra_parametro_funcao(n, parametros)

    return parametros

def encontra_parametros(no_parametro, parametros):
    no_parametro = no_parametro
    parametros = parametros
    parametro = {}
    tipo = ''
    nome = ''


    for no in no_parametro.children:
        # print("NO EXPRESSAO LABEL %s" % no.label)

        if (no.label == 'expressao'):
            tipo, nome = encontra_indice_retorno(no)
            parametro[nome] = tipo
            # print("PARAMETRO DICIONARIO 1")
            # print(parametro)
            parametros.append(parametro)
            
            return parametros

        encontra_parametros(no, parametros)
    return parametros


def monta_tabela_simbolos(tree, tabela_simbolos):
    dimensao_1 = ''
    dimensao_2 = ''
    dimensao = 0

    for filho in tree.children:
        # print(filho.label)
        if ('declaracao_variaveis' in filho.label):
            # Caso ele não seja um vetor ou uma matriz
            # print("LABEL DECLARACAO VARIAVEIS", filho.label)
            dimensao, dimensao_1, dimensao_2 = verifica_dimensoes(filho, 0, 0, 0)

            # Descomentar isso depois
            if (int(dimensao) > 1):
                print("É uma declaração de uma matriz ou um vetor")
                print()
                linha_declaracao = filho.label.split(':')
                linha_dataframe = ['ID',str(filho.children[2].children[0].children[0].children[0].label), str(filho.children[0].children[0].children[0].label), dimensao, dimensao_1, dimensao_2, escopo, 'N', linha_declaracao[1], 'N', [], []]
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
                return tabela_simbolos
            else:
                print("É uma declaração de uma variável com uma dimensão")
                print()
                linha_declaracao = filho.label.split(':')
                # print("LINHA DECLARACAO", linha_declaracao[1])
                linha_dataframe = ['ID',str(filho.children[2].children[0].children[0].children[0].label), str(filho.children[0].children[0].children[0].label), dimensao, dimensao_1, dimensao_2, escopo, 'N', linha_declaracao[1], 'N', [], []]
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
                # print(filho.children[0].children[0].children[0].label, filho.children[1].children[0].label, filho.children[2].children[0].children[0].children[0].label)
                return tabela_simbolos
        
        elif ('declaracao_funcao' in filho.label):
            # preciso do valor retornado e tipo do retorno
            tipo = ''
            nome_funcao = ''
            tipo_retorno = ''
            parametros = []
            retorno = []
            tipos = []

            # Encontrando os parametros
            # VERIFICAR SE ELES TEM DIMENSAO IGUAL A 1 OU MAIOR
            parametros = encontra_parametro_funcao(filho, parametros)

            # print("PARAMETROS DA FUNCAO DECLARADAAAAAAAAAAAAA")
            # print(parametros)

            # Não se esquecer de verificar também os parâmetros da função
            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]
            
            tipo, nome_funcao, _, retorno, tipo_retorno, linha_retorno = encontra_dados_funcao(filho, '', '', '', '', '', '')
            # print("TIPO %s, NOME %s, PARAMETROS %s, RETORNO %s TIPO_RETORNADO %s LINHA RETORNO %s" % (tipo, nome_funcao, parametros, retorno, tipo_retorno, linha_retorno))
            
            # print("AQUI RETORNNAAAAAAAAAAAAAAAAA")
            # print(retorno)

            linha_dataframe = ['ID', nome_funcao, tipo, 0, 0, 0, escopo, 'N', linha_declaracao, 'S', parametros, []]
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
            
            # Declara as variáveis passada por parametro 
            for p in parametros:
                for nome_param, tipo_param in p.items():
                    # print("PARAMETROS DA FUNCAO DECLARADAAAAAAAAAAAAA")
                    # print(nome_param, tipo_param)

                    linha_dataframe = ['ID', nome_param, tipo_param, 0, 0, 0, escopo, 'S', linha_declaracao, 'N', [], []]
                    tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe



            if (retorno != ''):
                # Verifica o tipo do retorno
                pos = 0
                muda_tipo_retorno_lista = []
                for ret in retorno:
                    for nome_retorno, tipo_retorno in ret.items():

                        # tipos_variaveis_retorno.append(tipo_retorno)

                        # procura na tabela de símbolos as variáveis
                        tipo_retorno = tabela_simbolos.loc[tabela_simbolos['Lexema'] == nome_retorno]
                        
                        tipo_variaveis_retorno = tipo_retorno['Tipo'].values
                        tipo_variaveis_retorno = tipo_variaveis_retorno[0]

                        muda_tipo_retorno = {}
                        muda_tipo_retorno[nome_retorno] = tipo_variaveis_retorno
                        muda_tipo_retorno_lista.append(muda_tipo_retorno)


                        tipos.append(tipo_variaveis_retorno)
                        pos += 1
                        # print("RETORNO NOMEEEEEEEEEEEEEEEE TIPOOOOOOOOOOOOOO")
                        # print(nome_retorno, tipo_variaveis_retorno)


                if len(tipos) > 0:
                    if ('flutuante' in tipos):
                        tipo = 'flutuante'
                    else:
                        tipo = 'inteiro'

                # Verificar se realmente veio algo no retorno
                linha_dataframe = ['ID', 'retorna', tipo, 0, 0, 0, escopo, 'N', linha_retorno,'S', [], muda_tipo_retorno_lista]
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe



        elif ('chamada_funcao' in filho.label):
            nome_funcao = ''
            # Utilizar um dicionario talvez
            parametros = []
            token = ''
            init = ''

            nome_funcao = filho.children[0].children[0].label
            parametros = encontra_parametros(filho, parametros)

            # print("CHAMADA FUNCAOOOOOOO")
            # print(parametros)

            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]

            print("PARAMETROS")
            print(parametros)

            # Procuro primeiramente se existe uma declaração dessa função
            declaracao_funcao = tabela_simbolos.loc[tabela_simbolos['Lexema'] == nome_funcao]


            if len(declaracao_funcao) > 0:
                tipo_funcao = declaracao_funcao['Tipo'].values
                tipo_funcao = tipo_funcao[0]
            else:
                tipo_funcao = 'vazio'

            # print("LENN DECLARACAO FUNCAO")
            # print(len(declaracao_funcao), tipo_funcao)

            parametro_list = []

            if len(parametros) >= 1:
                for param in parametros:
                    for nome_param, tipo_param in param.items():
                        # print("CHAMADA FUNCAOOOOOOO")
                        # print(nome_param, tipo_param)

                        parametro_dic = {}

                        # print("NOME PARAMETRO %s TIPO PARAMETRO %s" % (str(nome_param), str(tipo_param)))
                        # Pesquiso no tabela para ver se foi declarada
                        
                        parametro_inicializado = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_param) & (tabela_simbolos['init'] == 'S')]
                        parametro_declarado = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_param)]
                        
                        # print("VERIFICANDO SE A VARIAVEL FOI DECLARADA")
                        # print(parametro_declarado)
                        # # Verifica se a variável foi declarada
                        # if len(parametro_declarado) > 0:
                            # tipo_param = parametro_declarado['Tipo'].values
                            # tipo_param = tipo_param[0]
                        # if len(parametro_declarado) < 1:
                        #     tipo_param = 'vazio'

                        # Insere uma lista de parametro
                        parametro_dic[nome_param] = tipo_param
                        parametro_list.append(parametro_dic)

                        if len(parametro_inicializado) > 0:
                            init = 'S'
                        else:
                            init = 'N'

                        # print("NOME PARAMETRO", nome_param)
                        # linha_dataframe = ['ID', nome_param, tipo_param, 0, 0, 0, escopo, init, linha_declaracao, 'N', []]
                
            # Cria linha da chamada da função
            linha_dataframe = ['ID', filho.children[0].children[0].label, tipo_funcao, 0, 0, 0, escopo, 'N', linha_declaracao, 'chamada_funcao', parametro_list, []]
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
            # print('PARAMETRO LIST')
            # print(parametro_list)
            # tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
            # tabela_simbolos['parametros'] = parametro_list

        elif ('atribuicao' in filho.label):
            valor_atribuido = {}
            valores = []
            print("----------------------------------------------------")

            tipo, valor = encontra_indice_retorno(filho.children[2])
            variavel_atribuicao_nome = filho.children[0].children[0].children[0].label
            print("INICIALIZAÇÃO VARIAVEISSSS TIPO %s" % valor)

            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]

            # Caso o tipo seja um ID, significa que está recebendo uma outra variável
            # É necessário procurar se essa variável já foi declarada
            if tipo == 'parametro':


                variavel_declarada = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_atribuicao_nome) & (tabela_simbolos['init'] == 'N')]
                print("TIPO VARIAVEL INICIALIZADA")
                print(variavel_declarada)


                tipo = variavel_declarada['Tipo'].values
                tipo = tipo[0]


                # print("É UMA VARIÁVEL %s" % str(tipo))
            
            if tipo == 'NUM_INTEIRO':
                tipo = 'inteiro'
    

            valor_atribuido[valor] = tipo
            valores.append(valor_atribuido)

            # DESCOMENTAR AQUI
            # variavel_atribuicao_nome = filho.children[0].children[0].children[0].label
            
            print("----------------------------------------------------")
            print("VARIAVEL ATRIBUICAO NOME %s TIPO %s" % (variavel_atribuicao_nome, tipo))

            # Necessário verificar se a variável tem uma dimensão ou mais:
            linha_dataframe = ['ID', variavel_atribuicao_nome, tipo, 0, 0, 0, escopo, 'S', linha_declaracao, 'N', [], valores]
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
            


        monta_tabela_simbolos(filho, tabela_simbolos)

    return tabela_simbolos

# def commpara_tipo(tipo_variavel, tipo_atribuicao, tabela_simbolos):
#     if tipo_variavel == tipo_atribuicao:
#         tipo_atribuicao = tabela_simbolos.loc[tabela_simbolos['Lexema'] == nome_variavel_inicializacao]
#         tipo_atribuicao = tipo_atribuicao['Tipo'].values
#         tipo_atribuicao = tipo_atribuicao[0]
#         return True
#     else:
#         return False

def verifica_tipo_atribuicao(variavel_atual, tipo_variavel, escopo_variavel, inicializacao_variaveis, variaveis, funcoes, tabela_simbolos):
    # Vou verificar se a variável atual é do mesmo tipo da sua atribuição
    print("INICIALIZAÇÃO VARIÁVEL")
    print(inicializacao_variaveis)

    for ini_variaveis in inicializacao_variaveis:
        # for ini_var in ini_variaveis:
        for nome_variavel_inicializacao, tipo_variavel_inicializacao in ini_variaveis.items():
            print("NOME DA VARIÁVEL QUE FOI ATRIBUÍDA OU VALOR %s" % nome_variavel_inicializacao)

            # Verificar se ela pertence ás funções ou ás variáveis
            if nome_variavel_inicializacao in funcoes:
                tipo_atribuicao = tabela_simbolos.loc[tabela_simbolos['Lexema'] == nome_variavel_inicializacao]
                tipo_atribuicao = tipo_atribuicao['Tipo'].values
                tipo_atribuicao = tipo_atribuicao[0]

                print("O TIPO DA FUNÇÃO QUE FOI CHAMADA NA ATRIBUIÇÃO DE UMA VARIÁVEL %s" % tipo_atribuicao)

                if tipo_variavel == tipo_atribuicao:
                    # tipo_atribuicao = tabela_simbolos.loc[tabela_simbolos['Lexema'] == nome_variavel_inicializacao]
                    # tipo_atribuicao = tipo_atribuicao['Tipo'].values
                    # tipo_atribuicao = tipo_atribuicao[0]
                    return True, tipo_atribuicao, nome_variavel_inicializacao
                else:
                    return False, tipo_atribuicao, nome_variavel_inicializacao

            elif nome_variavel_inicializacao in variaveis['Lexema'].values:
                tipo_atribuicao = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_variavel_inicializacao) & (tabela_simbolos['escopo'] == escopo_variavel)]
                tipo_atribuicao = tipo_atribuicao['Tipo'].values
                tipo_atribuicao = tipo_atribuicao[0]
                print("ESTAAAAA DENTRO DE VARIÁVEISSSSSSSS")

                if tipo_variavel == tipo_atribuicao:
                    return True, tipo_atribuicao, nome_variavel_inicializacao
                else:
                    return False, tipo_atribuicao, nome_variavel_inicializacao
            
            # Significa que é um digito
            elif tipo_variavel_inicializacao == 'inteiro' or tipo_variavel_inicializacao == 'flutuante':
                print("O VALOR ATRIBUIDO É UM NÚMERO", tipo_variavel) 
                if tipo_variavel_inicializacao == 'flutuante':
                    if tipo_variavel == 'flutuante':
                        return True, 'flutuante', nome_variavel_inicializacao
                    else:
                        return False, 'inteiro', nome_variavel_inicializacao
                
                else:
                    if tipo_variavel == 'inteiro':
                        return True, 'inteiro', nome_variavel_inicializacao
                    else:
                        return False, 'flutuante', nome_variavel_inicializacao
                

def verifica_regras_semanticas(tabela_simbolos):
    # variaveis = tabela_simbolos['Lexema'].unique()

    # pegar só as variáveis
    variaveis = tabela_simbolos.loc[tabela_simbolos['funcao'] == 'N']

    # Valores únicos das variáveis declaradas e inicializadas
    variaveis_repetidas_valores = variaveis['Lexema'].unique()

    # Tirando variáveis do mesmo escopo difente, ficar com a declaração
    for var_rep in variaveis_repetidas_valores:
        # print("----------------------------------------------------")
        # print("VARRRRR REPPPPP %s" % (var_rep))
        variaveis_repetidas = variaveis.loc[variaveis['Lexema'] == var_rep]

        if len(variaveis_repetidas) > 1:
            variaveis_repetidas_index = variaveis_repetidas[variaveis_repetidas['init'] == 'N'].index
            variaveis_repetidas_linhas = variaveis_repetidas[variaveis_repetidas['init'] == 'N']
            print("----------------------------------------------------")
            print("VARRRRR REPPPPP %s" % (variaveis_repetidas_index))
            # Checar se elas são do mesmo escopo
            # Pego os escopos
            escopos_variaveis = variaveis_repetidas_linhas['escopo'].unique()

            # Passo por todas os escopos
            for esc in escopos_variaveis:
                print("ESCOPOOOOOOOOOOOOO", esc)
                variaveis_repetidas_escopo_igual_index = variaveis_repetidas_linhas.loc[variaveis_repetidas_linhas['escopo'] == esc].index
                # print("VARIAVEIS DO MESMO ESCOPO")
                # print(variaveis_repetidas_escopo_igual)
                variaveis.drop(variaveis_repetidas_escopo_igual_index[0] , inplace=True)



            # DESCOMENTAR ISSO AQUI
            # variaveis.drop(variaveis_repetidas_index , inplace=True)
        # dropar em variáveis a linha que contém a declaração da variável

        # print(variaveis)

    print()
    # variaveis = variaveis['Lexema'].unique()
    print("VARIAVEIS")
    print(variaveis)

    print("ITERANDO SOBRE ROWS")

    # variaveis = variaveis.reset_index()

    funcoes = tabela_simbolos.loc[tabela_simbolos['funcao'] != 'N']
    funcoes = funcoes['Lexema'].unique()

    # print("FUNÇÕES / CHAMADAS DE FUNÇÕES")
    # print(funcoes)



    # Verifica se existe a função principal
    if ('principal' not in funcoes):
        print('Erro: Função principal não declarada')

    # Verifica se as variaveis foram inicializadas

    # Itera sobre todas o dataFrame todo, assim é possível verificar o escopo
    # Passa por tudo que foi declarado (somente variáveis)
    for index, row in variaveis.iterrows():
        print('LEXEMAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', row['Lexema'])
        
    # for var in variaveis:
        # print("VARRR")
        # print(variaveis)
        # Verifica se não é a função principal
        inicializada = False

        # df = tabela_simbolos.loc[tabela_simbolos['Lexema'] == var]
        df = tabela_simbolos.loc[tabela_simbolos['Lexema'] == row['Lexema']]
        # print("Verificando se as variáveis foram inicializadas")
        # print(df)

        # Caso tenha mais de uma linha com o mesmo valor na coluna Lexema
        if (len(df) > 1):
            for lin in range(len(df)):
                if (df.iloc[lin]['init'] != 'N'):
                    inicializada = True
        else:
            # val = str(tabela_simbolos.iloc[0]['init'])
            # print(val)
            if (tabela_simbolos.iloc[0]['init'] != 'N'):
                inicializada = True

        # Procura nos retornos onde o escopo é diferente de principal
        # E vê se está no retorno
        # MELHOR PASSAR COM O ESCOPO AO PASSAR PELAS VARIÁVEIS
        # DESSE JEITO SE TIVER UMA VARIÁVEL COM O MESMO NOME EM ESCOPOS DIFERENTES NÃO VAI SER CONSIDERADO
        retorna_parametros = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == 'retorna') & (tabela_simbolos['escopo'] == row['escopo'])]
        retorna_parametros = retorna_parametros['valor']
        retorna_parametros = retorna_parametros.values



        # print("ESCOPO VARIÁVEL: %s  VARIÁVEL: %s" % (row['escopo'], row['Lexema']))
        print("ESCOPO RETORNO: %s" % retorna_parametros)
        
        # Caso tenha algum retorno que esteja no mesmo escopo que a declaração da variável
        if len(retorna_parametros) > 0:
            # Só verifica se a variável está nos parâmetros do retorno
            for  retornos_variaveis in retorna_parametros:
                print("RETORNO VARIÁVEIS", retornos_variaveis)
                for rt_vs in retornos_variaveis:
                    for nome_variavel_retorno, tipo_variavel_retorno in rt_vs.items():
                        print("NOME RETORNA VARIÁVEL %s TIPO VARIÁVEL RETORNA %s" % (nome_variavel_retorno, tipo_variavel_retorno))
                        
                        if (row['Lexema'] == nome_variavel_retorno):
                            inicializada = True
                            print("VARIÁVEL %s ESTÁ SENDO UTILIZADA NO RETORNO" % row['Lexema'])

        if (inicializada == False):
            print("Aviso: Variável '%s' declarada e não utilizada" % row['Lexema'])
        

        # Verificar se o tipo da atribuição de variáveis são o mesmo
        # Inicialmente pego as variáveis que foram inicializadas que estão no mesmo escopo
        inicializacao_variaveis = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == row['Lexema']) & (tabela_simbolos['escopo'] == row['escopo']) & (tabela_simbolos['init'] == 'S')]
        inicializacao_variaveis = inicializacao_variaveis['valor'].values
        print("AQUIIIIIIII AHHHHHHHHH", inicializacao_variaveis)

        inicializacao_variaveis_valores = []
        if len(inicializacao_variaveis) > 0:
            inicializacao_variaveis_valores = inicializacao_variaveis[0]


        # Depois de pegar o valor é necessário verificar se é uma variável ou uma função
        # Fazer uma função que retorna o tipo do valor atribuído
        print("VARIÁVEL %s E SEU VALOR ATRIBUÍDO %s LENN %s" % (row['Lexema'], inicializacao_variaveis_valores, len(inicializacao_variaveis_valores)))

        if len(inicializacao_variaveis_valores) > 0:
            boolen_tipo_igual, tipo_atribuicao, nome_variavel_inicializacao = verifica_tipo_atribuicao(row, row['Tipo'], row['escopo'], inicializacao_variaveis_valores, variaveis, funcoes, tabela_simbolos)
            print("BOOLLLLLLLLL", boolen_tipo_igual)

            if (boolen_tipo_igual == False):
                print("Aviso: Atribuição de tipos distintos '%s' %s e '%s' %s" % (row['Lexema'], row['Tipo'], nome_variavel_inicializacao, tipo_atribuicao))


        # Procura na tabela se a variável tem duas linhas onde init == 'N'
        lista_declaracao_variavel = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == row['Lexema']) & (tabela_simbolos['init'] == 'N') & (tabela_simbolos['escopo'] == row['escopo'])]
        # lista_declaracao_variavel = lista_declaracao_variavel['Lexema'].values
        print("-----------------------------------------------------------")

        print("TAMANHOOOOOOOOOO DECLARACAOOOOOOOOOO", len(lista_declaracao_variavel))
        print(lista_declaracao_variavel)

        print("-----------------------------------------------------------")
        if len(lista_declaracao_variavel) > 1:
            print("Aviso: Variável '%s' já declarada anteriormente" % row['Lexema'])

    # Verifica todas as funções/chamadas de funções
    for func in funcoes:
        if func == 'principal':
            # Caso o lexema seja principal verificar se há um retorno e o tipo dele
            tabela_retorno = tabela_simbolos.loc[tabela_simbolos['Lexema'] == 'retorno']

            if (tabela_retorno.shape[0] == 0):
                print("Erro: Função principal deveria retornar inteiro, mas retorna vazio")

        else:
            # Verificar se há uma chamada de função
            chamada_funcao = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == func) & (tabela_simbolos['funcao'] == 'chamada_funcao')]
            
            if len(chamada_funcao) > 0:
                declaracao_funcao = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == func) & (tabela_simbolos['funcao'] == 'S')]
                
                # Se há uma declaração
                if len(declaracao_funcao) < 1:
                    print("Erro: Chamada a função %s que não foi declarada" % func)
                else:
                # Agora verifico a quantidade de parâmetro
                    quantidade_parametros_chamada = chamada_funcao['parametros']
                    quantidade_parametros_chamada = quantidade_parametros_chamada.values
                    quantidade_parametros_chamada = quantidade_parametros_chamada[0]

                    quantidade_parametros_declaracao_funcao = declaracao_funcao['parametros']
                    quantidade_parametros_declaracao_funcao = quantidade_parametros_declaracao_funcao.values
                    quantidade_parametros_declaracao_funcao = quantidade_parametros_declaracao_funcao[0]
                    
                    # print("QUANTIDADE DE PARAMETROS CHAMADA")
                    # print(quantidade_parametros_chamada, len(quantidade_parametros_chamada))

                    # print("QUANTIDADE DE PARAMETROS DECLARACAO")
                    # print(quantidade_parametros_declaracao_funcao, len(quantidade_parametros_declaracao_funcao))

                    if len(quantidade_parametros_chamada) < len(quantidade_parametros_declaracao_funcao):
                        print("Erro: Chamada à função %s com número de parâmetros menor que o declarado" % func)
                    
                    elif len(quantidade_parametros_chamada) > len(quantidade_parametros_declaracao_funcao):
                        print("Erro: Chamada à função '%s' com número de parâmetros maior que o declarado" % func)
            

def main():
    # global escopo

    escopo = 'global'

    tree = tppparser.main()
    print("Tree")
    print(tree)
    # data = ['ID', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE',]

    tabela_simbolos = pd.DataFrame(data=[], columns=['Token', 'Lexema', 'Tipo', 'dim', 'tam_dim1', 'tam_dim2', 'escopo', 'init', 'linha', 'funcao', 'parametros', 'valor'])
    # tabela_simbolos.loc[len(tabela_simbolos)] = data
    # Montar a tabela de símbolos
    tabela_simbolos = monta_tabela_simbolos(tree, tabela_simbolos)
    verifica_regras_semanticas(tabela_simbolos)
    print()
    print("TABELA DE SÍMBOLOS")
    print(tabela_simbolos)

if __name__ == "__main__":
    main()