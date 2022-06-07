import tppparser
import pandas as pd
import sys

from sys import argv
from anytree.exporter import UniqueDotExporter


global escopo
global variavel_nao_declarada 
global avisos

escopo = 'global'
variavel_nao_declarada = []
avisos = []

pd.set_option('display.max_columns', None)


def encontra_expressao_retorno(retorna, lista_retorno):
    lista_retorno = lista_retorno
    retorno_dict = {}
    tipo_retorno = ''
    indice = ''

    for ret in retorna.children:
        if ret.label == 'numero':
            indice = ret.children[0].children[0].label 
            tipo_retorno = ret.children[0].label

            if (tipo_retorno == 'NUM_INTEIRO'):
                tipo_retorno = 'inteiro'
            
            elif (tipo_retorno == 'NUM_FLUTUANTE'):
                tipo_retorno = 'flutuante'

            retorno_dict[indice] = tipo_retorno
            lista_retorno.append(retorno_dict)

            return lista_retorno

        elif ret.label == 'ID':
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
            return retorno
        
        encontra_valores_retorno(ret, retorno)

    return retorno

def encontra_tipo_nome_parametro(parametro, tipo, nome):
    tipo = tipo
    nome = nome
    
    for param in parametro.children:

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

def atribuicao_expressao(expressao, valores):
    indice = ''
    tipo_retorno = ''
    valores = valores
    valor_dic = {}

    for filhos in expressao.children:
        if filhos.label == 'numero':
            indice = filhos.children[0].children[0].label 
            tipo_retorno = filhos.children[0].label

            if (tipo_retorno == 'NUM_INTEIRO'):
                tipo_retorno = 'inteiro'
            
            elif (tipo_retorno == 'NUM_PONTO_FLUTUANTE'):
                tipo_retorno = 'flutuante'

            valor_dic[indice] = tipo_retorno
            valores.append(valor_dic)

        elif filhos.label == 'ID':
            indice = filhos.children[0].label
            tipo_retorno = 'parametro'

            valor_dic[indice] = tipo_retorno
            valores.append(valor_dic)

        valores = atribuicao_expressao(filhos, valores)
    
    return valores

def encontra_indice_retorno(expressao):
    indice = ''
    tipo_retorno = ''

    for filhos in expressao.children:
        if filhos.label == 'numero':
            indice = filhos.children[0].children[0].label 
            tipo_retorno = filhos.children[0].label

            if (tipo_retorno == 'NUM_INTEIRO'):
                tipo_retorno = 'inteiro'
            
            elif (tipo_retorno == 'NUM_PONTO_FLUTUANTE'):
                tipo_retorno = 'flutuante'

            return tipo_retorno, indice

        elif filhos.label == 'ID':
            indice = filhos.children[0].label
            tipo_retorno = 'parametro'

            return tipo_retorno, indice

        tipo_retorno,indice = encontra_indice_retorno(filhos)
    
    return tipo_retorno,indice

def encontra_atribuicao_valor(expressao, valores):
    indice = ''
    tipo_retorno = ''
    valores = valores
    v = {}

    for filhos in expressao.children:
        if filhos.label == 'numero':
            indice = filhos.children[0].children[0].label 
            tipo_retorno = filhos.children[0].label

            if (tipo_retorno == 'NUM_INTEIRO'):
                tipo_retorno = 'inteiro'
            
            elif (tipo_retorno == 'NUM_PONTO_FLUTUANTE'):
                tipo_retorno = 'flutuante'

            v[indice] = tipo_retorno
            valores.append(v)

        elif filhos.label == 'ID':
            indice = filhos.children[0].label
            tipo_retorno = 'parametro'

            v[indice] = tipo_retorno
            valores.append(v)

        tipo_retorno,indice = encontra_indice_retorno(filhos)
    
    return tipo_retorno, valores

def verifica_dimensoes(tree, dimensao, indice_1, indice_2):
    # Verifica sub-árvore da variável para verificar suas dimensões
    indice_1 = indice_1
    indice_2 = indice_2
    dimensao = dimensao

    for filho in tree.children:

        if (filho.label == 'indice'):
            # Posso verificar se o filho 0 do indice também é índice
            # Se for, quer dizer que tem mais de uma dimensão
            if (filho.children[0].label == 'indice'):
                dimensao = 2
                _, indice_1 = encontra_indice_retorno(filho.children[0].children[1])
                _, indice_2 = encontra_indice_retorno(filho.children[2])
                return dimensao, indice_1, indice_2
            
            else:
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
    
    for filho in declaracao_funcao.children:
        if (filho.label == 'tipo'):
            tipo = filho.children[0].children[0].label

        elif (filho.label == 'lista_parametros'):
            if (filho.children[0].label == 'vazio'):
                parametros = 'vazio'
            else:
                pass
            
        elif (filho.label == 'cabecalho'):
            nome_funcao = filho.children[0].children[0].label
            escopo = nome_funcao
        
        elif ('retorna' in filho.label):

            retorno_tipo_valor = encontra_valores_retorno(filho, [])
            linha_retorno = filho.label.split(':')
            linha_retorno = linha_retorno[1]
            token = filho.children[0].label
            retorno = ''

            tipo_retorno = 'vazio'


            return tipo, nome_funcao, parametros, retorno_tipo_valor, tipo_retorno, linha_retorno

        tipo, nome_funcao, parametros, retorno_tipo_valor, tipo_retorno, linha_retorno = encontra_dados_funcao(filho, tipo, nome_funcao, parametros, retorno_tipo_valor, tipo_retorno, linha_retorno)

    return tipo, nome_funcao, parametros, retorno_tipo_valor, tipo_retorno, linha_retorno

def encontra_parametro_funcao(no, parametros):

    parametros = parametros
    parametro = {}

    for n in no.children:
        if (no.label == 'parametro'):
            tipo, nome = encontra_tipo_nome_parametro(no, '', '')

            parametro[nome] = tipo

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
        if (no.label == 'expressao'):
            tipo, nome = encontra_indice_retorno(no)
            parametro[nome] = tipo
            parametros.append(parametro)
            
            return parametros

        encontra_parametros(no, parametros)
    return parametros


def monta_tabela_simbolos(tree, tabela_simbolos):
    dimensao_1 = ''
    dimensao_2 = ''
    dimensao = 0

    for filho in tree.children:
        if ('declaracao_variaveis' in filho.label):
            # Caso ele não seja um vetor ou uma matriz
            dimensao, dimensao_1, dimensao_2 = verifica_dimensoes(filho, 0, 0, 0)

            # Descomentar isso depois
            if (int(dimensao) > 1):
                linha_declaracao = filho.label.split(':')
                linha_dataframe = ['ID',str(filho.children[2].children[0].children[0].children[0].label), str(filho.children[0].children[0].children[0].label), dimensao, dimensao_1, dimensao_2, escopo, 'N', linha_declaracao[1], 'N', [], []]
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
                return tabela_simbolos
            else:
                linha_declaracao = filho.label.split(':')
                linha_dataframe = ['ID',str(filho.children[2].children[0].children[0].children[0].label), str(filho.children[0].children[0].children[0].label), dimensao, dimensao_1, dimensao_2, escopo, 'N', linha_declaracao[1], 'N', [], []]
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
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
            parametros = encontra_parametro_funcao(filho, parametros)

            # Não se esquecer de verificar também os parâmetros da função
            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]
            
            tipo, nome_funcao, _, retorno, tipo_retorno, linha_retorno = encontra_dados_funcao(filho, '', '', '', '', '', '')

            if tipo == '':
                tipo = 'vazio'

            linha_dataframe = ['ID', nome_funcao, tipo, 0, 0, 0, escopo, 'N', linha_declaracao, 'S', parametros, []]
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
            
            # Declara as variáveis passada por parametro 
            for p in parametros:
                for nome_param, tipo_param in p.items():

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
                        if len(tipo_variaveis_retorno) > 0:
                            tipo_variaveis_retorno = tipo_variaveis_retorno[0]
                        else:
                            tipo_variaveis_retorno = 'vazio'


                        muda_tipo_retorno = {}
                        muda_tipo_retorno[nome_retorno] = tipo_variaveis_retorno
                        muda_tipo_retorno_lista.append(muda_tipo_retorno)


                        tipos.append(tipo_variaveis_retorno)
                        pos += 1

                if len(tipos) > 0:
                    if ('flutuante' in tipos):
                        tipo = 'flutuante'
                    else:
                        tipo = 'inteiro'

                # Verificar se realmente veio algo no retorno
                linha_dataframe = ['ID', 'retorna', tipo, 0, 0, 0, escopo, 'N', linha_retorno,'S', [], muda_tipo_retorno_lista]
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe

        elif ('retorna' in filho.label):
            tipos = []
            
            # Verifico se já existe uma linha retorna na tabela para essa função (ou seja, com esse escopo)
            linha_retorno = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == 'retorna') & (tabela_simbolos['escopo'] == escopo)]

            # Pega a linha do dataframe
            linha_retorno_index = tabela_simbolos.index[(tabela_simbolos['Lexema'] == 'retorna') & (tabela_simbolos['escopo'] == escopo)].tolist()
            linha_retorno_index = linha_retorno_index[0]

            # Pego os retornos
            retorno_linha = linha_retorno['valor'].values.tolist()
            retorno = retorno_linha[0]


            if len(linha_retorno) > 0:
                pos = 0
                muda_tipo_retorno_lista = []
                global variavel_nao_declarada

                for ret in retorno:
                    for nome_retorno, tipo_retorno in ret.items():
                        # procura na tabela de símbolos as variáveis
                        tipo_retorno = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_retorno) & (tabela_simbolos['escopo'] == escopo)]
                        
                        tipo_variaveis_retorno = tipo_retorno['Tipo'].values

                        if len(tipo_variaveis_retorno) > 0:
                            tipo_variaveis_retorno = tipo_variaveis_retorno[0]
                        else:
                            if nome_retorno not in variavel_nao_declarada:
                                print("Erro: Variável '%s' não declarada" % nome_retorno)
                                variavel_nao_declarada.append(nome_retorno)
                            tipo_variaveis_retorno = 'vazio'
                            

                        muda_tipo_retorno = {}
                        muda_tipo_retorno[nome_retorno] = tipo_variaveis_retorno
                        muda_tipo_retorno_lista.append(muda_tipo_retorno)

                        tipos.append(tipo_variaveis_retorno)
                        pos += 1

                if len(tipos) > 0:
                    if ('flutuante' in tipos):
                        tipo = 'flutuante'
                    else:
                        tipo = 'inteiro'
                
                # Verificar se realmente veio algo no retorno
                tabela_simbolos.at[linha_retorno_index, 'valor'] = muda_tipo_retorno_lista
                tabela_simbolos.at[linha_retorno_index, 'Tipo'] = tipo

        elif ('chamada_funcao' in filho.label):
            nome_funcao = ''
            # Utilizar um dicionario talvez
            parametros = []
            token = ''
            init = ''

            nome_funcao = filho.children[0].children[0].label
            parametros = encontra_parametros(filho, parametros)

            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]

            # Procuro primeiramente se existe uma declaração dessa função
            declaracao_funcao = tabela_simbolos.loc[tabela_simbolos['Lexema'] == nome_funcao]


            if len(declaracao_funcao) > 0:
                tipo_funcao = declaracao_funcao['Tipo'].values
                tipo_funcao = tipo_funcao[0]
            else:
                tipo_funcao = 'vazio'

            parametro_list = []

            if len(parametros) >= 1:
                for param in parametros:
                    for nome_param, tipo_param in param.items():
                        parametro_dic = {}

                        # Pesquiso no tabela para ver se foi declarada
                        parametro_inicializado = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_param) & (tabela_simbolos['init'] == 'S')]
                        parametro_declarado = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_param)]
                        
                        # Insere uma lista de parametro
                        parametro_dic[nome_param] = tipo_param
                        parametro_list.append(parametro_dic)

                        if len(parametro_inicializado) > 0:
                            init = 'S'
                        else:
                            init = 'N'

                
            # Cria linha da chamada da função
            linha_dataframe = ['ID', filho.children[0].children[0].label, tipo_funcao, 0, 0, 0, escopo, 'N', linha_declaracao, 'chamada_funcao', parametro_list, []]
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe

        elif ('atribuicao' in filho.label):
            valor_atribuido = {}
            valores = []
            tipo_valor = []
            dimensoes = 0
            tam_dimensao_1 = 0
            tam_dimensao_2 = 0

            tipo_valor = atribuicao_expressao(filho.children[2], [])

            variavel_atribuicao_nome = filho.children[0].children[0].children[0].label

            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]


            # Caso o tipo seja um ID, significa que está recebendo uma outra variável
            # É necessário procurar se essa variável já foi declarada
            for i in tipo_valor:
                for valor, tipo in i.items():

                    if tipo == 'parametro':

                        variavel_declarada = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == valor) & (tabela_simbolos['init'] == 'N')]

                        if len(variavel_declarada) > 0:
                            tipo = variavel_declarada['Tipo'].values
                            tipo = tipo[0]
                        elif len(variavel_declarada) == 0:
                            print("Erro: Variável '%s' não declarada" % valor)


                    if tipo == 'NUM_INTEIRO':
                        tipo = 'inteiro'

                    elif tipo == 'NUM_PONTO_FLUTUANTE':
                        tipo = 'flutuante'
            

                    valor_atribuido[valor] = tipo
                    valores.append(valor_atribuido)

                    # A variável que recebe alguma coisa / tenho que verificar o escopo também
                    # tipo_variavel_recebendo = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_atribuicao_nome) & (tabela_simbolos['init'] == 'N')]
                    tipo_variavel_recebendo = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_atribuicao_nome) & (tabela_simbolos['init'] == 'N') & (tabela_simbolos['escopo'] == escopo)]
                    
                    if tipo == 'ID':
                        tipo_variavel_recebendo_global = tipo_variavel_recebendo
                        
                        tipo_variavel_recebendo = tipo_variavel_recebendo['Tipo'].values
                    
                    if len(tipo_variavel_recebendo) > 0:
                        if len(tipo_variavel_recebendo) == 1:
                            tipo_variavel_recebendo = tipo_variavel_recebendo
                        
                        else:
                            tipo_variavel_recebendo = tipo_variavel_recebendo[0]


                    # Caso não tenha nenhuma variável declarada nesse escopo, verificar o escopo global
                    if len(tipo_variavel_recebendo) == 0 and (tipo != 'inteiro' and tipo != 'flutuante'):
                        tipo_variavel_recebendo_global = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_atribuicao_nome) & (tabela_simbolos['init'] == 'N')]

                        # Quer dizer que foi declarada globalmente
                        # Então pega esse tipo da variável declarada globalmente
                        if len(tipo_variavel_recebendo_global) > 0:
                            tipo_variavel_recebendo_global = tipo_variavel_recebendo_global['Tipo'].values
                            tipo_variavel_recebendo_global = tipo_variavel_recebendo_global[0]

                            tipo_variavel_recebendo = tipo_variavel_recebendo_global
                    
                    # Recebendo um valor inteiro ou flutuante
                    else: 
                        tipo_variavel_valor = tipo
                        tipo_variavel_recebendo = tipo_variavel_valor


                    dimensoes = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_atribuicao_nome) & (tabela_simbolos['init'] == 'N')]
                    tam_dimensao_1 = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_atribuicao_nome) & (tabela_simbolos['init'] == 'N')]
                    tam_dimensao_2 = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_atribuicao_nome) & (tabela_simbolos['init'] == 'N')]

                    dimensoes = dimensoes['dim'].values

                    if len(dimensoes) > 0:
                        dimensoes = dimensoes[0]
                    else:
                        dimensoes = 0

                    tam_dimensao_1 = tam_dimensao_1['tam_dim1'].values

                    if len(tam_dimensao_1) > 0:
                        tam_dimensao_1 = tam_dimensao_1[0]

                    tam_dimensao_2 = tam_dimensao_2['tam_dim2'].values

                    if len(tam_dimensao_2) > 0:
                        tam_dimensao_2 = tam_dimensao_2[0]

                    # Verifica se tem mais de uma dimensão
                    # Caso tenha, tenho que pegar a posição que ele acessa
                    if int(dimensoes) > 0:
                        dimensoes, tam_dimensao_1, tam_dimensao_2 = verifica_dimensoes(filho, 0, 0, 0)

                    # Necessário verificar se a variável tem uma dimensão ou mais:
                    linha_dataframe = ['ID', variavel_atribuicao_nome, tipo_variavel_recebendo, dimensoes, tam_dimensao_1, tam_dimensao_2, escopo, 'S', linha_declaracao, 'N', [], valores]
                    tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
                


        monta_tabela_simbolos(filho, tabela_simbolos)

    return tabela_simbolos


def verifica_tipo_atribuicao(variavel_atual, tipo_variavel, escopo_variavel, inicializacao_variaveis, variaveis, funcoes, tabela_simbolos):
    # Vou verificar se a variável atual é do mesmo tipo da sua atribuição
    status = True
    tipo_atribuicao = ''
    nome_inicializacao = ''
    tipo_variavel_inicializacao_retorno = ''
    tipo_variavel_novo = ''
    tipos_distintos = []

    # Nome da variável que está recebendo um valor
    nome_variavel = variavel_atual['Lexema']
    for ini_variaveis in inicializacao_variaveis:
        for ini_var in ini_variaveis:
            for nome_variavel_inicializacao, tipo_variavel_inicializacao in ini_var.items():
                
                status = True
                nome_inicializacao = nome_variavel_inicializacao
                # Pegar a declaração da variável que está recebendo um valor no escopo
                # Caso não encontre, procurar no escopo global
                declaracao_variavel = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_variavel) & (tabela_simbolos['escopo'] == escopo_variavel) & (tabela_simbolos['init'] == 'N')]

                if len(declaracao_variavel) == 0:
                    declaracao_variavel_global = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_variavel) & (tabela_simbolos['escopo'] == 'global') & (tabela_simbolos['init'] == 'N')]
                    
                    if len(declaracao_variavel_global) > 0:
                        tipo_variavel_novo = declaracao_variavel_global['Tipo'].values[0]
                else:
                    tipo_variavel_novo = declaracao_variavel['Tipo'].values[0]

                
                # Verificar se ela pertence ás funções ou ás variáveis
                if nome_variavel_inicializacao in funcoes:
                    tipo_atribuicao = tabela_simbolos.loc[tabela_simbolos['Lexema'] == nome_variavel_inicializacao]
                    tipo_atribuicao = tipo_atribuicao['Tipo'].values
                    tipo_atribuicao = tipo_atribuicao[0]

                    if tipo_variavel_novo == tipo_atribuicao:
                        status = True
                    else:
                        status = False
                    
                    
                    if status == False:
                        aviso_string = "Aviso: Atribuição de tipos distintos '%s' %s e '%s' %s" % (nome_variavel, tipo_variavel_novo, nome_variavel_inicializacao, tipo_variavel_inicializacao)
                        if aviso_string not in avisos:
                            avisos.append(aviso_string)
                            print("Aviso: Atribuição de tipos distintos '%s' %s e '%s' %s" % (nome_variavel, tipo_variavel_novo, nome_variavel_inicializacao, tipo_variavel_inicializacao))

                    return status, tipo_variavel_inicializacao,tipo_variavel_novo, nome_inicializacao


                elif nome_variavel_inicializacao in variaveis['Lexema'].values:
                    tipo_atribuicao = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_variavel_inicializacao) & (tabela_simbolos['escopo'] == escopo_variavel) & (tabela_simbolos['init'] == 'N')]
                    
                    if len(tipo_atribuicao) == 0:
                        tipo_atribuicao = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_variavel_inicializacao) & (tabela_simbolos['escopo'] == 'global') & (tabela_simbolos['init'] == 'N')]

                    tipo_atribuicao = tipo_atribuicao['Tipo'].values
                    if len(tipo_atribuicao) > 0:
                        tipo_atribuicao = tipo_atribuicao[0]
                    
                    if len(tipo_variavel_novo)> 0 and len(tipo_atribuicao)> 0:
                        if tipo_variavel_novo == tipo_atribuicao:
                            status = True
                        else:
                            status = False
                    
                    if status == False:
                        aviso_variavel_string = "Aviso: Atribuição de tipos distintos '%s' %s e '%s' %s" % (nome_variavel, tipo_variavel_novo, nome_variavel_inicializacao, tipo_variavel_inicializacao)
                        if aviso_variavel_string not in avisos:
                            avisos.append(aviso_variavel_string)
                            print("Aviso: Atribuição de tipos distintos '%s' %s e '%s' %s" % (nome_variavel, tipo_variavel_novo, nome_variavel_inicializacao, tipo_variavel_inicializacao))


                    
                # Significa que é um digito
                elif tipo_variavel_inicializacao == 'inteiro' or tipo_variavel_inicializacao == 'flutuante':
                    
                    declaracao_variavel_valor = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_variavel) & (tabela_simbolos['escopo'] == escopo_variavel) & (tabela_simbolos['init'] == 'N')]

                    if len(declaracao_variavel_valor) == 0:
                        declaracao_variavel_global_valor = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_variavel) & (tabela_simbolos['escopo'] == 'global') & (tabela_simbolos['init'] == 'N')]
                        
                        if len(declaracao_variavel_global_valor) > 0:
                            tipo_variavel_novo = declaracao_variavel_global_valor['Tipo'].values[0]
                    else:
                        tipo_variavel_novo = declaracao_variavel['Tipo'].values[0]


                    if '.' in str(nome_variavel_inicializacao):
                        tipo_variavel = 'flutuante'

                    if tipo_variavel_inicializacao == 'flutuante':
                        if tipo_variavel == 'flutuante':
                            status = True 
                            tipo_variavel_novo = 'flutuante'
                        else:
                            status = False
                            tipo_variavel_novo = 'inteiro'
                    
                    else:
                        if tipo_variavel_novo == 'inteiro':
                            status =  True
                            tipo_variavel_novo = 'inteiro'
                        else:
                            status = False
                            tipo_variavel_novo = 'flutuante'

                    if status == False:
                        aviso_variavel_string = "Aviso: Atribuição de tipos distintos '%s' %s e '%s' %s" % (nome_variavel, tipo_variavel_novo, nome_variavel_inicializacao, tipo_variavel_inicializacao)

                        if aviso_variavel_string not in avisos:
                            avisos.append(aviso_variavel_string)
                            print("Aviso: Atribuição de tipos distintos '%s' %s e '%s' %s" % (nome_variavel, tipo_variavel_novo, nome_variavel_inicializacao, tipo_variavel_inicializacao))


                tipo_variavel_inicializacao_retorno = tipo_variavel_inicializacao
    
    return status, tipo_variavel_inicializacao_retorno,tipo_variavel_novo, nome_inicializacao

def verifica_regras_semanticas(tabela_simbolos):
    # pegar só as variáveis
    variaveis = tabela_simbolos.loc[tabela_simbolos['funcao'] == 'N']
    
    funcoes = tabela_simbolos.loc[tabela_simbolos['funcao'] != 'N']
    funcoes = funcoes['Lexema'].unique()

    i = 0
    
    # Valores únicos das variáveis declaradas e inicializadas
    variaveis_repetidas_valores_inicio = variaveis['Lexema'].unique()
    var_verificacao = variaveis
    # Retira as repetidas
    for var in variaveis_repetidas_valores_inicio:

        linhas = tabela_simbolos[tabela_simbolos['Lexema'] == var].index.tolist()
        linha = tabela_simbolos[tabela_simbolos['Lexema'] == var]

        if len(linhas) > 1:
            linhas = linha[linha['init'] == 'N'].index.tolist()
            if len(linhas) > 1:
                var_verificacao.drop(linhas[0])
        
    # dropar as declarações
    for index, row in variaveis.iterrows():
        lista_declaracao_variavel = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == row['Lexema']) & (tabela_simbolos['init'] == 'N') & (tabela_simbolos['escopo'] == row['escopo'])]

        if len(lista_declaracao_variavel) > 1:
            string_variavel_declarada = "Aviso: Variável '%s' já declarada anteriormente" % row['Lexema']
            if string_variavel_declarada not in avisos:
                avisos.append(string_variavel_declarada)
                print("Aviso: Variável '%s' já declarada anteriormente" % row['Lexema'])


    # Se ainda tiver alguma variável do mesmo escopo
    escopo_variaveis_verificacao = var_verificacao['escopo'].unique()
    for e in escopo_variaveis_verificacao:
        for var in variaveis_repetidas_valores_inicio:
            mesmo_escopo = var_verificacao[(var_verificacao['escopo'] == e) & (var_verificacao['Lexema'] == var)]

            if len(mesmo_escopo) > 1:
                linha_mesmo_escopo = mesmo_escopo.index.tolist()
                var_verificacao.drop(linha_mesmo_escopo[0])


    for linha in var_verificacao.index:   
        inicializacao_variaveis = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variaveis['Lexema'][linha]) & (tabela_simbolos['escopo'] == variaveis['escopo'][linha]) & (tabela_simbolos['init'] == 'S')]
        inicializacao_variaveis = inicializacao_variaveis['valor'].values

        inicializacao_variaveis_valores = []
        if len(inicializacao_variaveis) > 0:
            inicializacao_variaveis_valores = inicializacao_variaveis


        # Depois de pegar o valor é necessário verificar se é uma variável ou uma função
        # Fazer uma função que retorna o tipo do valor atribuído
        if len(inicializacao_variaveis_valores) > 0:
            boolen_tipo_igual, tipo_variavel_atribuida, tipo_atribuicao, nome_variavel_inicializacao = verifica_tipo_atribuicao(variaveis.iloc[i], variaveis['Tipo'][linha], variaveis['escopo'][linha], inicializacao_variaveis_valores, variaveis, funcoes, tabela_simbolos)

        i += 1

    # # Valores únicos das variáveis declaradas e inicializadas
    variaveis_repetidas_valores = variaveis['Lexema'].unique()

    for var_rep in variaveis_repetidas_valores:
        variaveis_repetidas = variaveis.loc[variaveis['Lexema'] == var_rep]

        if len(variaveis_repetidas) > 1:
            variaveis_repetidas_index = variaveis_repetidas[variaveis_repetidas['init'] == 'N'].index
            variaveis_repetidas_linhas = variaveis_repetidas[variaveis_repetidas['init'] == 'N']
            # print("VARIAVEIS REPETIDAS")
            # print(variaveis_repetidas_linhas)
            # Checar se elas são do mesmo escopo
            # Pego os escopos
            escopos_variaveis = variaveis_repetidas_linhas['escopo'].unique()

            # Passo por todas os escopos
            for esc in escopos_variaveis:
                variaveis_repetidas_escopo_igual_index = variaveis_repetidas_linhas.loc[variaveis_repetidas_linhas['escopo'] == esc].index
                variaveis.drop(variaveis_repetidas_escopo_igual_index[0])

        elif len(variaveis_repetidas) == 0:
            print("Erro: Variável '%s' não declarada" % var_rep)

    # retirar os repetidos novamente se houver
    repetidos_variaveis_atribuicao = variaveis['Lexema'].unique()
    for rep in repetidos_variaveis_atribuicao:
        tabela_variaveis_repetida = variaveis.loc[variaveis['Lexema'] == rep]
        tabela_variaveis_repetida_index = variaveis.loc[variaveis['Lexema'] == rep].index
        
        if len(tabela_variaveis_repetida_index) > 1:
            variaveis.drop(tabela_variaveis_repetida_index[0])
    
    # Verifica se existe a função principal
    if ('principal' not in funcoes):
        print('Erro: Função principal não declarada')


    for index, row in variaveis.iterrows():
        dimensao_variavel = row['dim']
        
        if int(dimensao_variavel) > 0:
            if int(dimensao_variavel) == 1:
                # Verifica se a dimensão tem um '.'
                if '.' in str(row['tam_dim1']):
                    aviso_indice = "Erro: índice de array '%s' não inteiro" % row['Lexema']
                    if aviso_indice not in avisos:
                        avisos.append(aviso_indice)
                        print("Erro: índice de array '%s' não inteiro" % row['Lexema'])

            # Verifica se tem mais de uma dimensão
            elif int(dimensao_variavel) == 2:
                # Verifica se a dimensão tem um '.'
                if '.' in str(row['tam_dim2']):
                    print("Erro: índice de array '%s' não inteiro" % row['Lexema'])

        inicializada = False

        df = tabela_simbolos.loc[tabela_simbolos['Lexema'] == row['Lexema']]

        # Caso tenha mais de uma linha com o mesmo valor na coluna Lexema
        if (len(df) > 1):
            for lin in range(len(df)):
                if (df.iloc[lin]['init'] != 'N'):
                    inicializada = True
        else:
            if (tabela_simbolos.iloc[0]['init'] != 'N'):
                inicializada = True

        # Procura nos retornos onde o escopo é diferente de principal
        # E vê se está no retorno
        retorna_parametros = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == 'retorna') & (tabela_simbolos['escopo'] == row['escopo'])]
        retorna_parametros = retorna_parametros['valor']
        retorna_parametros = retorna_parametros.values

        # Caso tenha algum retorno que esteja no mesmo escopo que a declaração da variável
        if len(retorna_parametros) > 0:
            # Só verifica se a variável está nos parâmetros do retorno
            for  retornos_variaveis in retorna_parametros:
                for rt_vs in retornos_variaveis:
                    for nome_variavel_retorno, tipo_variavel_retorno in rt_vs.items():
                        
                        if (row['Lexema'] == nome_variavel_retorno):
                            inicializada = True

        if (inicializada == False):
            string_declarada_nao_utilizada = "Aviso: Variável '%s' declarada e não utilizada" % row['Lexema']
            if string_declarada_nao_utilizada not in avisos:
                avisos.append(string_declarada_nao_utilizada)
                print("Aviso: Variável '%s' declarada e não utilizada" % row['Lexema'])
        

    # Verifica todas as funções/chamadas de funções
    for func in funcoes:
        if func == 'principal':
            # Caso o lexema seja principal verificar se há um retorno e o tipo dele
            tabela_retorno = tabela_simbolos.loc[tabela_simbolos['Lexema'] == 'retorno']

            if (tabela_retorno.shape[0] == 0):
                print("Erro: Função principal deveria retornar inteiro, mas retorna vazio")

            # Verificar se a função principal chama ela mesma
            chamada_funcao_principal = tabela_simbolos.loc[(tabela_simbolos['funcao'] == 'chamada_funcao') & (tabela_simbolos['Lexema'] == 'principal')]

            if len(chamada_funcao_principal) > 0:
                verifica_escopo = chamada_funcao_principal['escopo'].values[0]

                if verifica_escopo == 'principal':
                    print("Aviso: Chamada recursiva para principal")
                else:
                    print("Erro: Chamada para a função principal não permitida")
        else:
            # Verificar se há uma chamada de função
            chamada_funcao = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == func) & (tabela_simbolos['funcao'] == 'chamada_funcao')]
            declaracao_funcao = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == func) & (tabela_simbolos['funcao'] == 'S')]
            
            # Verifica se o tipo da função é do mesmo tipo do retorno
            if (func == 'retorna'):
                escopo_retorno = declaracao_funcao['escopo'].values
                escopo_retorno = escopo_retorno[0]

                # Pego a variável retornada
                variavel_retornada = declaracao_funcao['valor'].values[0]
                for var in variavel_retornada:
                    for n, t in var.items():
                        variavel_retornada = n

                # Atribuo o valor do tipo da funçao
                tipo_retorno_funcao = declaracao_funcao['Tipo'].values
                tipo_retorno_funcao = tipo_retorno_funcao[0]

                if variavel_retornada in tabela_simbolos['Lexema'].unique():
                    declaracao_variavel = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_retornada) & (tabela_simbolos['escopo'] == escopo_retorno) & (tabela_simbolos['init'] == 'N')]

                    if len(declaracao_variavel) == 0:
                        
                        declaracao_variavel_global = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_retornada) & (tabela_simbolos['escopo'] == 'global') & (tabela_simbolos['init'] == 'N')]

                        if len(declaracao_variavel_global) == 0:
                            declaracao_variavel_global = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_retornada) & (tabela_simbolos['escopo'] == escopo_retorno) & (tabela_simbolos['init'] == 'S')]

                        tipo_retorno_funcao = declaracao_variavel_global['Tipo'].values[0]

                

                procura_funcao_escopo = tabela_simbolos.loc[(tabela_simbolos['funcao'] == 'S') & (tabela_simbolos['escopo'] == escopo_retorno) & (tabela_simbolos['Lexema'] != 'retorna')]
                
                nome_funcao = procura_funcao_escopo['Lexema'].values
                nome_funcao = nome_funcao[0]

                tipo_funcao = procura_funcao_escopo['Tipo'].values
                tipo_funcao = tipo_funcao[0]

                if (tipo_funcao != tipo_retorno_funcao):
                    print("Erro: Função '%s' do tipo %s retornando %s" % (nome_funcao, tipo_funcao, tipo_retorno_funcao))


            # Verifica se há alguma chamada de função
            if len(chamada_funcao) > 0:
                
                # Se há uma declaração
                if len(declaracao_funcao) < 1:
                    print("Erro: Chamada a função '%s' que não foi declarada" % func)
                else:
                # Agora verifico a quantidade de parâmetro
                    quantidade_parametros_chamada = chamada_funcao['parametros']
                    quantidade_parametros_chamada = quantidade_parametros_chamada.values
                    quantidade_parametros_chamada = quantidade_parametros_chamada[0]

                    quantidade_parametros_declaracao_funcao = declaracao_funcao['parametros']
                    quantidade_parametros_declaracao_funcao = quantidade_parametros_declaracao_funcao.values
                    quantidade_parametros_declaracao_funcao = quantidade_parametros_declaracao_funcao[0]
                    
                    if len(quantidade_parametros_chamada) < len(quantidade_parametros_declaracao_funcao):
                        print("Erro: Chamada à função '%s' com número de parâmetros menor que o declarado" % func)
                    
                    elif len(quantidade_parametros_chamada) > len(quantidade_parametros_declaracao_funcao):
                        print("Erro: Chamada à função '%s' com número de parâmetros maior que o declarado" % func)
            
            else:
                # Caso não tenha nenhuma chamada, porém ainda houve uma declaração
                if len(declaracao_funcao) > 0:
                    if func != 'retorna':
                        print("Aviso: Função '%s' declarada, mas não utilizada" % func)


def retira_no(no_remove):
    auxilixar_arvore = []
    pai = no_remove.parent

    if no_remove.name in remover_nos:
        for filho in range(len(pai.children)):
            # Verifico se está na lista de nós que quero remover
            if pai.children[filho].name ==  no_remove.name:
                auxilixar_arvore += no_remove.children
            
            # Caso nao esteja eu adiciono na lista do auxiliar
            else:
                auxilixar_arvore.append(pai.children[filho])
        pai.children = auxilixar_arvore

    elif no_remove.name.split(':')[0] in remover_nos:
        for filho in range(len(pai.children)):
            # Verifico se está na lista de nós que quero remover
            if pai.children[filho].name ==  no_remove.name:
                auxilixar_arvore += no_remove.children
            
            # Caso nao esteja eu adiciono na lista do auxiliar
            else:
                auxilixar_arvore.append(pai.children[filho])

        pai.children = auxilixar_arvore

    if no_remove.name in verificar_nos:
        if len(no_remove.children) == 0:
            for filho in range(len(pai.children)):
            # Verifico se está na lista de nós que quero remover
                if pai.children[filho].name ==  no_remove.name:
                    auxilixar_arvore += no_remove.children

                elif pai.children[filho].name.split(':')[0] == no_remove.name:
                    auxilixar_arvore += no_remove.children


                # Caso nao esteja eu adiciono na lista do auxiliar
                else:
                    auxilixar_arvore.append(pai.children[filho])
            
            pai.children = auxilixar_arvore
    
    elif no_remove.name.split(':')[0] in verificar_nos:
        if len(no_remove.children) == 0:
            for filho in range(len(pai.children)):
            # Verifico se está na lista de nós que quero remover
                if pai.children[filho].name ==  no_remove.name:
                    auxilixar_arvore += no_remove.children

                elif pai.children[filho].name.split(':')[0] == no_remove.name:
                    auxilixar_arvore += no_remove.children


                # Caso nao esteja eu adiciono na lista do auxiliar
                else:
                    auxilixar_arvore.append(pai.children[filho])
            
            pai.children = auxilixar_arvore
        


def poda_arvore(arvore_abstrata):
    for no in arvore_abstrata.children:
        
        poda_arvore(no)
    retira_no(arvore_abstrata)
    

def main():
    # global escopo
    global remover_nos
    global verificar_nos
    global deixa_proximos_nos

    arg_tabela = argv[2]

    escopo = 'global'

    tree = tppparser.main()

    tabela_simbolos = pd.DataFrame(data=[], columns=['Token', 'Lexema', 'Tipo', 'dim', 'tam_dim1', 'tam_dim2', 'escopo', 'init', 'linha', 'funcao', 'parametros', 'valor'])
    # Montar a tabela de símbolos
    tabela_simbolos = monta_tabela_simbolos(tree, tabela_simbolos)
    verifica_regras_semanticas(tabela_simbolos)

    if arg_tabela != '--ntabela':
        print()
        print("TABELA DE SÍMBOLOS")
        print(tabela_simbolos)

    # Nós que tem o valor de linhas nos nomes
    verificar_nos = ['retorna', 'corpo', 'leia', 'escreva', 'se', 'repita', 'até']

    # Nós que serão retirados na poda
    remover_nos = ['ID', 'var', 'lista_variaveis', 'dois_pontos', 'tipo',
                    'INTEIRO',  'NUM_INTEIRO','lista_declaracoes', 'declaracao', 'indice',
                    'numero', 'fator','abre_colchete', 'fecha_colchete', 'menos', 'menor_igual',
                    'maior_igual','expressao', 'expressao_logica',  'ABRE_PARENTESE', 'FECHA_PARENTESE', 
                    'MAIS', 'chamada_funcao', 'MENOS','expressao_simples', 'expressao_aditiva', 'expressao_multiplicativa',
                    'expressao_unaria', 'inicializacao_variaveis', 'ATRIBUICAO','NUM_NOTACAO_CIENTIFICA', 'LEIA', 
                    'abre_parentese', 'fecha_parentese', 'atribuicao', 'fator', 'cabecalho', 'FIM','operador_soma',
                    'mais', 'chamada_funcao', 'lista_argumentos', 'VIRGULA','virgula', 'lista_parametros', 'vazio',
                    '(', ')', ':', ',', 'FLUTUANTE', 'NUM_PONTO_FLUTUANTE', 'RETORNA', 'ESCREVA', 'SE', 'ENTAO', 'SENAO',
                    'maior','menor', 'REPITA', 'igual', 'menos', 'menor_igual', 'maior_igual', 'operador_logico',
                    'operador_multiplicacao', 'vezes','id', 'declaracao_variaveis', 'atribuicao', 'operador_relacional', 'MAIOR']

    # Verificar retorno (nenhum filho)
    poda_arvore(tree)
    print()
    print()

    # Gera imagem da árvore podada
    UniqueDotExporter(tree).to_picture(f"{sys.argv[1]}.prunned.unique.ast.png")
    print(f"Grafo da Árvore Sintática Abstrata foi gerada. \nArquivo de Saída: {sys.argv[1]}.prunned.unique.ast.png")


if __name__ == "__main__":
    main()