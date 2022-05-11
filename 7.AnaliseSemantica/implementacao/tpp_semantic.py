import tppparser
import pandas as pd

global escopo
escopo = 'global'

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
                linha_dataframe = ['ID',str(filho.children[2].children[0].children[0].children[0].label), str(filho.children[0].children[0].children[0].label), dimensao, dimensao_1, dimensao_2, escopo, 'N', linha_declaracao[1], 'N']
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
                return tabela_simbolos
            else:
                print("É uma declaração de uma variável com uma dimensão")
                print()
                linha_declaracao = filho.label.split(':')
                # print("LINHA DECLARACAO", linha_declaracao[1])
                linha_dataframe = ['ID',str(filho.children[2].children[0].children[0].children[0].label), str(filho.children[0].children[0].children[0].label), dimensao, dimensao_1, dimensao_2, escopo, 'N', linha_declaracao[1], 'N']
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
            print("TIPO %s, NOME %s, PARAMETROS %s, RETORNO %s TIPO_RETORNADO %s LINHA RETORNO %s" % (tipo, nome_funcao, parametros, retorno, tipo_retorno, linha_retorno))
            
            linha_dataframe = ['ID', nome_funcao, tipo, 0, 0, 0, escopo, 'N', linha_declaracao[1], 'S']
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
            
            # Verificar se realmente veio algo no retorno
            linha_dataframe = ['ID', 'retorna', tipo, 0, 0, 0, escopo, 'N', linha_retorno,'N']
            tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe


        monta_tabela_simbolos(filho, tabela_simbolos)

    return tabela_simbolos

def verifica_regras_semanticas(tabela_simbolos):
    # Verifica se existe a função principal
    if ('principal' not in tabela_simbolos['Lexema']):
        print('Erro: Função principal não declarada')

    # Verifica se as variaveis foram inicializadas
    variaveis = tabela_simbolos['Lexema'].unique()

    # Passa por tudo que foi declarado
    for var in variaveis:
        # Verifica se não é a função principal
        if var != 'principal':
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
        
        else:
            # Caso o lexema seja principal verificar se há um retorno e o tipo dele
            pass


def main():
    # global escopo

    escopo = 'global'

    tree = tppparser.main()
    print("Tree")
    print(tree)
    # data = ['ID', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE',]

    tabela_simbolos = pd.DataFrame(data=[], columns=['Token', 'Lexema', 'Tipo', 'dim', 'tam_dim1', 'tam_dim2', 'escopo', 'init', 'linha', 'funcao'])
    # tabela_simbolos.loc[len(tabela_simbolos)] = data
    # Montar a tabela de símbolos
    tabela_simbolos = monta_tabela_simbolos(tree, tabela_simbolos)
    # verifica_regras_semanticas(tabela_simbolos)
    print()
    print("TABELA DE SÍMBOLOS")
    print(tabela_simbolos)

if __name__ == "__main__":
    main()