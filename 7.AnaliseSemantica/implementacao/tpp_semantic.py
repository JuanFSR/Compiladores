from sqlalchemy import values
import tppparser
import pandas as pd

global escopo
escopo = 'global'
pd.set_option('display.max_columns', None)

def encontra_indice_retorno(expressao):
    indice = ''
    tipo_retorno = ''

    for filhos in expressao.children:
        if filhos.label == 'numero':
            # print("Encontra indice")
            indice = filhos.children[0].children[0].label 
            # print(indice)
            tipo_retorno = filhos.children[0].label
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
    

def encontra_dados_funcao(declaracao_funcao, tipo, nome_funcao, parametros, retorno, tipo_retorno, linha_retorno):
    tipo = tipo 
    nome_funcao = nome_funcao 
    parametros = parametros
    tipo_retorno = tipo_retorno
    linha_retorno = linha_retorno

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
            linha_retorno = filho.label.split(':')
            linha_retorno = linha_retorno[1]
            token = filho.children[0].label
            retorno = ''

            tipo_retorno, retorno = encontra_indice_retorno(filho.children[2])
            return tipo, nome_funcao, parametros, retorno, tipo_retorno, linha_retorno

        tipo, nome_funcao, parametros, retorno, tipo_retorno, linha_retorno = encontra_dados_funcao(filho, tipo, nome_funcao, parametros, retorno, tipo_retorno, linha_retorno)

    return tipo, nome_funcao, parametros, retorno, tipo_retorno, linha_retorno

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
            print("PARAMETRO DICIONARIO")
            print(parametro)
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

            # Não se esquecer de verificar também os parâmetros da função
            linha_declaracao = filho.label.split(':')
            tipo, nome_funcao, parametros, retorno, tipo_retorno, linha_retorno = encontra_dados_funcao(filho, '', '', '', '', '', '')
            # print("TIPO %s, NOME %s, PARAMETROS %s, RETORNO %s TIPO_RETORNADO %s LINHA RETORNO %s" % (tipo, nome_funcao, parametros, retorno, tipo_retorno, linha_retorno))
            
            linha_dataframe = ['ID', nome_funcao, tipo, 0, 0, 0, escopo, 'N', linha_declaracao[1], 'S', [], []]
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
            
            if (retorno != ''):
                # Verificar se realmente veio algo no retorno
                linha_dataframe = ['ID', 'retorna', tipo, 0, 0, 0, escopo, 'N', linha_retorno,'S', [], []]
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe

        elif ('chamada_funcao' in filho.label):
            nome_funcao = ''
            # Utilizar um dicionario talvez
            parametros = []
            token = ''
            init = ''

            nome_funcao = filho.children[0].label
            parametros = encontra_parametros(filho, parametros)

            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]

            # print("PARAMETROS")
            # print(parametros)

            # Procuro primeiramente se existe uma declaração dessa função
            declaracao_funcao = tabela_simbolos.loc[tabela_simbolos['Lexema'] == nome_funcao]

            if len(declaracao_funcao) > 0:
                tipo_funcao = declaracao_funcao['Tipo']
            else:
                tipo_funcao = 'vazio'


            parametro_list = []

            if len(parametros) >= 1:
                for param in parametros:
                    for nome_param, tipo_param in param.items():
                        parametro_dic = {}

                        # print("NOME PARAMETRO %s TIPO PARAMETRO %s" % (str(nome_param), str(tipo_param)))
                        # Pesquiso no tabela para ver se foi declarada
                        
                        parametro_inicializado = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_param) & (tabela_simbolos['init'] == 'S')]
                        parametro_declarado = tabela_simbolos.loc[(tabela_simbolos['Lexema'] == nome_param)]
                        
                        # print("VERIFICANDO SE A VARIAVEL FOI DECLARADA")
                        # print(parametro_declarado)
                        # # Verifica se a variável foi declarada
                        if len(parametro_declarado) > 0:
                            tipo_param = parametro_declarado['Tipo'].values
                            tipo_param = tipo_param[0]
                        else:
                            tipo_param = 'vazio'

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

            tipo, valor = encontra_indice_retorno(filho.children[2])

            linha_declaracao = filho.label.split(':')
            linha_declaracao = linha_declaracao[1]

            # Caso o tipo seja um ID, significa que está recebendo uma outra variável
            # É necessário procurar se essa variável já foi declarada
            if tipo == 'ID':


                variavel_declarada = tabela_simbolos.loc[tabela_simbolos['Lexema'] == valor]
                tipo = variavel_declarada['Tipo'].values
                tipo = tipo[0]

                print("É UMA VARIÁVEL %s" % str(tipo))
            
            if tipo == 'NUM_INTEIRO':
                tipo = 'inteiro'
    
            valor_atribuido[valor] = tipo
            valores.append(valor_atribuido)

            variavel_atribuicao_nome = filho.children[0].children[0].children[0].label
            
            # Necessário verificar se a variável tem uma dimensão ou mais:
            linha_dataframe = ['ID', variavel_atribuicao_nome, tipo, 0, 0, 0, escopo, 'S', linha_declaracao, 'N', [], valores]
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
            


        monta_tabela_simbolos(filho, tabela_simbolos)

    return tabela_simbolos

def verifica_regras_semanticas(tabela_simbolos):
    # variaveis = tabela_simbolos['Lexema'].unique()

    # pegar só as variáveis
    variaveis = tabela_simbolos.loc[tabela_simbolos['funcao'] == 'N']
    variaveis = variaveis['Lexema'].unique()

    funcoes = tabela_simbolos.loc[tabela_simbolos['funcao'] != 'N']
    funcoes = funcoes['Lexema'].unique()

    print("VARIAVEIS")
    print(variaveis)

    print("FUNÇÕES / CHAMADAS DE FUNÇÕES")
    print(funcoes)



    # Verifica se existe a função principal
    if ('principal' not in funcoes):
        print('Erro: Função principal não declarada')

    # Verifica se as variaveis foram inicializadas

    # Passa por tudo que foi declarado (somente variáveis)
    for var in variaveis:
        print("VARRR")
        print(variaveis)
        # Verifica se não é a função principal
        inicializada = False

        df = tabela_simbolos.loc[tabela_simbolos['Lexema'] == var]
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

        if (inicializada == False):
            print("Aviso: Variável '%s' declarada e não utilizada" % var)
        


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