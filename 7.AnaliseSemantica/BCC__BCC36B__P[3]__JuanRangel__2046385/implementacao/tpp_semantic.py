from os import stat
from matplotlib.axis import Axis
from sqlalchemy import values
import tppparser
import pandas as pd
import sys

from anytree.exporter import UniqueDotExporter


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
            indice = ret.children[0].children[0].label 
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
    
    for filho in declaracao_funcao.children:
        if (filho.label == 'tipo'):
            tipo = filho.children[0].children[0].label

        elif (filho.label == 'lista_parametros'):
            if (filho.children[0].label == 'vazio'):
                parametros = 'vazio'
            else:
                print("Tem mais de um parâmetro")
            
        elif (filho.label == 'cabecalho'):
            nome_funcao = filho.children[0].children[0].label
            escopo = nome_funcao
        
        elif ('retorna' in filho.label):

            retorno_tipo_valor = encontra_valores_retorno(filho, [])
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
                linha_declaracao = filho.label.split(':')
                linha_dataframe = ['ID',str(filho.children[2].children[0].children[0].children[0].label), str(filho.children[0].children[0].children[0].label), dimensao, dimensao_1, dimensao_2, escopo, 'N', linha_declaracao[1], 'N', [], []]
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
                return tabela_simbolos
            else:
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

            # Não se esquecer de verificar também os parâmetros da função
            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]
            
            tipo, nome_funcao, _, retorno, tipo_retorno, linha_retorno = encontra_dados_funcao(filho, '', '', '', '', '', '')

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

            tipo, valor = encontra_indice_retorno(filho.children[2])
            variavel_atribuicao_nome = filho.children[0].children[0].children[0].label

            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]

            # Caso o tipo seja um ID, significa que está recebendo uma outra variável
            # É necessário procurar se essa variável já foi declarada
            if tipo == 'parametro':


                variavel_declarada = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == valor) & (tabela_simbolos['init'] == 'N')]

                tipo = variavel_declarada['Tipo'].values
                tipo = tipo[0]


            if tipo == 'NUM_INTEIRO':
                tipo = 'inteiro'

            elif tipo == 'NUM_PONTO_FLUTUANTE':
                tipo = 'flutuante'
    

            valor_atribuido[valor] = tipo
            valores.append(valor_atribuido)

            # A variável que recebe alguma coisa
            tipo_variavel_recebendo = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == variavel_atribuicao_nome) & (tabela_simbolos['init'] == 'N')]
            tipo_variavel_recebendo = tipo_variavel_recebendo['Tipo'].values
            
            if len(tipo_variavel_recebendo) > 0:
                tipo_variavel_recebendo = tipo_variavel_recebendo[0]


            # Necessário verificar se a variável tem uma dimensão ou mais:
            linha_dataframe = ['ID', variavel_atribuicao_nome, tipo_variavel_recebendo, 0, 0, 0, escopo, 'S', linha_declaracao, 'N', [], valores]
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
            


        monta_tabela_simbolos(filho, tabela_simbolos)

    return tabela_simbolos


def verifica_tipo_atribuicao(variavel_atual, tipo_variavel, escopo_variavel, inicializacao_variaveis, variaveis, funcoes, tabela_simbolos):
    # Vou verificar se a variável atual é do mesmo tipo da sua atribuição
    status = True
    tipo_atribuicao = ''
    nome_inicializacao = ''

    for ini_variaveis in inicializacao_variaveis:
        for ini_var in ini_variaveis:
            for nome_variavel_inicializacao, tipo_variavel_inicializacao in ini_var.items():
                nome_inicializacao = nome_variavel_inicializacao

                # Verificar se ela pertence ás funções ou ás variáveis
                if nome_variavel_inicializacao in funcoes:
                    tipo_atribuicao = tabela_simbolos.loc[tabela_simbolos['Lexema'] == nome_variavel_inicializacao]
                    tipo_atribuicao = tipo_atribuicao['Tipo'].values
                    tipo_atribuicao = tipo_atribuicao[0]

                    if tipo_variavel == tipo_atribuicao:
                        status = True
                    else:
                        status = False

                elif nome_variavel_inicializacao in variaveis['Lexema'].values:
                    tipo_atribuicao = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_variavel_inicializacao) & (tabela_simbolos['escopo'] == escopo_variavel)]
                    tipo_atribuicao = tipo_atribuicao['Tipo'].values
                    tipo_atribuicao = tipo_atribuicao[0]

                    if tipo_variavel == tipo_atribuicao:
                        # return True, tipo_atribuicao, nome_variavel_inicializacao
                        status = True
                    else:
                        status = False
                
                # Significa que é um digito
                elif tipo_variavel_inicializacao == 'inteiro' or tipo_variavel_inicializacao == 'flutuante':
                    if tipo_variavel_inicializacao == 'flutuante':
                        if tipo_variavel == 'flutuante':
                            # return True, 'flutuante', nome_variavel_inicializacao
                            status = True 
                            tipo_atribuicao = 'flutuante'
                        else:
                            # return False, 'inteiro', nome_variavel_inicializacao
                            status = False
                            tipo_atribuicao = 'inteiro'
                    
                    else:
                        if tipo_variavel == 'inteiro':
                            # return True, 'inteiro', nome_variavel_inicializacao
                            status =  True
                            tipo_atribuicao = 'inteiro'
                        else:
                            status = False
                            tipo_atribuicao = 'flutuante'
                    
    return status, tipo_atribuicao, nome_inicializacao

def verifica_regras_semanticas(tabela_simbolos):
    # variaveis = tabela_simbolos['Lexema'].unique()

    # pegar só as variáveis
    variaveis = tabela_simbolos.loc[tabela_simbolos['funcao'] == 'N']

    # Valores únicos das variáveis declaradas e inicializadas
    variaveis_repetidas_valores = variaveis['Lexema'].unique()

    # Tirando variáveis do mesmo escopo difente, ficar com a declaração
    for var_rep in variaveis_repetidas_valores:
        variaveis_repetidas = variaveis.loc[variaveis['Lexema'] == var_rep]

        if len(variaveis_repetidas) > 1:
            variaveis_repetidas_index = variaveis_repetidas[variaveis_repetidas['init'] == 'N'].index
            variaveis_repetidas_linhas = variaveis_repetidas[variaveis_repetidas['init'] == 'N']

            # Checar se elas são do mesmo escopo
            # Pego os escopos
            escopos_variaveis = variaveis_repetidas_linhas['escopo'].unique()

            # Passo por todas os escopos
            for esc in escopos_variaveis:
                variaveis_repetidas_escopo_igual_index = variaveis_repetidas_linhas.loc[variaveis_repetidas_linhas['escopo'] == esc].index
                variaveis.drop(variaveis_repetidas_escopo_igual_index[0] , inplace=True)

        elif len(variaveis_repetidas) == 0:
            print("Erro: Variável '%s' não declarada" % var_rep)


    funcoes = tabela_simbolos.loc[tabela_simbolos['funcao'] != 'N']
    funcoes = funcoes['Lexema'].unique()


    # retirar os repetidos novamente se houver
    repetidos_variaveis_atribuicao = variaveis['Lexema'].unique()
    for rep in repetidos_variaveis_atribuicao:
        tabela_variaveis_repetida = variaveis.loc[variaveis['Lexema'] == rep]
        tabela_variaveis_repetida_index = variaveis.loc[variaveis['Lexema'] == rep].index
        
        if len(tabela_variaveis_repetida_index) > 1:
            variaveis.drop(tabela_variaveis_repetida_index[0], inplace=True)
    
    # Verifica se existe a função principal
    if ('principal' not in funcoes):
        print('Erro: Função principal não declarada')

    # Verifica se as variaveis foram inicializadas

    # Itera sobre todas o dataFrame todo, assim é possível verificar o escopo
    # Passa por tudo que foi declarado (somente variáveis)
    for index, row in variaveis.iterrows():
        
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
            print("Aviso: Variável '%s' declarada e não utilizada" % row['Lexema'])
        

        # Verificar se o tipo da atribuição de variáveis são o mesmo
        # Inicialmente pego as variáveis que foram inicializadas que estão no mesmo escopo
        inicializacao_variaveis = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == row['Lexema']) & (tabela_simbolos['escopo'] == row['escopo']) & (tabela_simbolos['init'] == 'S')]
        inicializacao_variaveis = inicializacao_variaveis['valor'].values

        inicializacao_variaveis_valores = []
        if len(inicializacao_variaveis) > 0:
            inicializacao_variaveis_valores = inicializacao_variaveis


        # Depois de pegar o valor é necessário verificar se é uma variável ou uma função
        # Fazer uma função que retorna o tipo do valor atribuído

        if len(inicializacao_variaveis_valores) > 0:
            boolen_tipo_igual, tipo_atribuicao, nome_variavel_inicializacao = verifica_tipo_atribuicao(row, row['Tipo'], row['escopo'], inicializacao_variaveis_valores, variaveis, funcoes, tabela_simbolos)

            if (boolen_tipo_igual == False):
                print("Aviso: Atribuição de tipos distintos '%s' %s e '%s' %s" % (row['Lexema'], row['Tipo'], nome_variavel_inicializacao, tipo_atribuicao))


        # Procura na tabela se a variável tem duas linhas onde init == 'N'
        lista_declaracao_variavel = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == row['Lexema']) & (tabela_simbolos['init'] == 'N') & (tabela_simbolos['escopo'] == row['escopo'])]

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
                    
                    if len(quantidade_parametros_chamada) < len(quantidade_parametros_declaracao_funcao):
                        print("Erro: Chamada à função %s com número de parâmetros menor que o declarado" % func)
                    
                    elif len(quantidade_parametros_chamada) > len(quantidade_parametros_declaracao_funcao):
                        print("Erro: Chamada à função '%s' com número de parâmetros maior que o declarado" % func)
            

def retira_no(no_remove):
    pass


def main():
    # global escopo
    global remover_nos
    global deixa_proximos_nos

    escopo = 'global'

    tree = tppparser.main()
    print("Tree")
    print(tree)

    tabela_simbolos = pd.DataFrame(data=[], columns=['Token', 'Lexema', 'Tipo', 'dim', 'tam_dim1', 'tam_dim2', 'escopo', 'init', 'linha', 'funcao', 'parametros', 'valor'])
    # Montar a tabela de símbolos
    tabela_simbolos = monta_tabela_simbolos(tree, tabela_simbolos)
    verifica_regras_semanticas(tabela_simbolos)
    print()
    print("TABELA DE SÍMBOLOS")
    print(tabela_simbolos)


if __name__ == "__main__":
    main()