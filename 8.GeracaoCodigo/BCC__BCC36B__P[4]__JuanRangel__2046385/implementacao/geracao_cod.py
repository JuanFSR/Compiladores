import pandas as pd
import tpp_semantic
import numpy as np
from llvmlite import ir
from llvmlite import binding as llvm

global modulo
global arvore_podada
global tabela_simbolos

def gera_codigo(arvore):
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