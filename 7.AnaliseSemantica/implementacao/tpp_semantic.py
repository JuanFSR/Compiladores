import tppparser
import pandas as pd

def encontra_indice(expressao):
    indice = ''
    for filhos in expressao.children:
        if filhos.label == 'numero':
            print("Encontra indice")
            indice = filhos.children[0].children[0].label 
            print(indice)
        indice = encontra_indice(filhos)
    
    return indice

def verifica_dimensoes(tree, dimensao, indice_1, indice_2):
    # Verifica sub-árvore da variável para verificar suas dimensões
    indice_1 = indice_1
    indice_2 = indice_2
    dimensao = dimensao


    for filho in tree.children:
        print(filho.label)
        if (filho.label == 'indice'):
            print("Encontrou o lable indice %s" % filho.label)
            dimensao += 1
            
            if dimensao == 1:
                print("Dimensao 1")
                print(filho.children[1].label)
                indice_1 = encontra_indice(filho.children[1])
                print(indice_1)
            
            elif dimensao == 2:
                print("Dimensao 2")
                print(filho.children[1].label)
                indice_2 = encontra_indice(filho.children[1])
                print("indice encontrado %s" % indice_2)

        if dimensao != 0:    
            print("DIMENSAO, TAM_DIM_1, TAM_DIM_2 --- dentro do verifica dimensões")
            print(dimensao, indice_1, indice_2)



        dimensao, indice_1, indice_2 = verifica_dimensoes(filho, dimensao, indice_1, indice_2)
    return dimensao, indice_1, indice_2
    

def monta_tabela_simbolos(tree, tabela_simbolos):
    dimensao_1 = ''
    dimensao_2 = ''
    dimensao = 0

    for filho in tree.children:
        # print(filho.label)
        if ('declaracao_variaveis' in filho.label):
            # Caso ele não seja um vetor ou uma matriz
            print("LABEL DECLARACAO VARIAVEIS", filho.label)
            dimensao, dimensao_1, dimensao_2 = verifica_dimensoes(filho, 0, '0', '0')
            print("Dimensoes monta tabela")
            print(dimensao, dimensao_1, dimensao_2)

            # Descomentar isso depois
            if (int(dimensao) >= 1):
                print("É uma declaração de uma matriz ou um vetor")
                return tabela_simbolos
            else:
                print("Adiciono isso na tabela de simbolos")
                print()
                linha_declaracao = filho.label.split(':')
                # print("LINHA DECLARACAO", linha_declaracao[1])
                linha_dataframe = ['ID',str(filho.children[2].children[0].children[0].children[0].label), str(filho.children[0].children[0].children[0].label), '0', '0', '0', escopo, 'N', linha_declaracao[1]]
                tabela_simbolos.loc[len(tabela_simbolos)] = linha_dataframe
                # print(filho.children[0].children[0].children[0].label, filho.children[1].children[0].label, filho.children[2].children[0].children[0].children[0].label)
                return tabela_simbolos
        monta_tabela_simbolos(filho, tabela_simbolos)

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

        # print("Variaveis %s" % variaveis)
    # Printar tudo que foi declarado
    # print("Variaveis")
    # print(variaveis)

def main():
    global escopo

    escopo = 'global'

    tree = tppparser.main()
    print("Tree")
    print(tree)
    # data = ['ID', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE', 'TESTE',]

    tabela_simbolos = pd.DataFrame(data=[], columns=['Token', 'Lexema', 'Tipo', 'dim', 'tam_dim1', 'tam_dim2', 'escopo', 'init', 'linha'])
    # tabela_simbolos.loc[len(tabela_simbolos)] = data
    # Montar a tabela de símbolos
    tabela_simbolos = monta_tabela_simbolos(tree, tabela_simbolos)
    # verifica_regras_semanticas(tabela_simbolos)
    print()
    print("TABELA DE SÍMBOLOS")
    print(tabela_simbolos)

if __name__ == "__main__":
    main()