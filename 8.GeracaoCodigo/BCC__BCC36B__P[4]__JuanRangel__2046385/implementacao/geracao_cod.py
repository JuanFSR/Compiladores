import pandas as pd
import tpp_semantic
import numpy as np

def gera_codigo(arvore_podada):
    for no in arvore_podada.children:
        print(no.label)

        gera_codigo(no)

def main():
    # Chamando análise semantica
    arvore_podada = tpp_semantic.main()

    print('------------------------------------')
    print("Geração Código")

    gera_codigo(arvore_podada)

if __name__ == "__main__":
    main()