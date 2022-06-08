from urllib.request import build_opener
import pandas as pd
import tpp_semantic
import numpy as np
from llvmlite import ir
from llvmlite import binding as llvm

global modulo
global arvore_podada
global tabela_simbolos
global builder

def gera_codigo(arvore):
    linha = 0
    global builder
    global modulo

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
                    variavel_declarada.align = 4
                    
                    zero_declaracao = ir.Constant(ir.IntType(32), 0)
                    
                    builder.store(zero_declaracao, variavel_declarada) 



                # Defino o retorno da função onde a variável foi declarada
        elif ('declaracao_funcao' in no.label):
            linha = no.label.split(':')
            linha = linha[1]

            # procuro a função declarado nessa linha
            funcao_encontrada = tabela_simbolos[tabela_simbolos['linha'] == linha]
            print("------------------------")                
            print("FUNCAO ENCONTRADA")                
            print(funcao_encontrada)      

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

            # Adiciona o bloco de entrada
            builder = ir.IRBuilder(bloco_entrada)

        elif ('retorna' in no.label):
            linha = no.label.split(':')
            linha = linha[1]

            retorno_encontrado = tabela_simbolos[tabela_simbolos['Lexema'] == 'retorna']
            print("RETORNO TABELA")
            print(retorno_encontrado)

            # Cria o valor de retorno, verificar ainda o retorno correto de cada função
            if ('inteiro' == retorno_encontrado['Tipo'].values[0]):
                # Declara o retorno da função
                retorno_funcao = ir.Constant(ir.IntType(32), 0)

                # Aloca a variável de retorno
                retorno = builder.alloca(ir.IntType(32), name='retorno')
                
                # Atribui o valor zero para o retorno da função
                builder.store(retorno_funcao, retorno)

                # Defini o retorno da função
                builder.ret(retorno)


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

    print('------------------------------------')
    print('Código gerado')
    print(modulo)


if __name__ == "__main__":
    main()