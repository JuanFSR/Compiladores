from lib2to3.pgen2.pgen import DFAState
from statistics import mode
from sys import argv, exit

import logging

logging.basicConfig(
     level = logging.DEBUG,
     filename = "log.txt",
     filemode = "w",
     format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

import ply.lex as lex
from ply.lex import TOKEN

tokens = [  
    # identificador
    "ID", 
    # numerais
    "NUM_NOTACAO_CIENTIFICA",   # ponto flutuante em notaçao científica
    "NUM_PONTO_FLUTUANTE",      # ponto flutuate
    "NUM_INTEIRO",              # inteiro
    # operadores binarios
    "MAIS",                     # +
    "MENOS",                    # -
    "MULTIPLICACAO",            # *
    "DIVISAO",                  # /
    "E_LOGICO",                 # &&
    "OU_LOGICO",                # ||
    "DIFERENCA",                # <>
    "MENOR_IGUAL",              # <=
    "MAIOR_IGUAL",              # >=
    "MENOR",                    # <
    "MAIOR",                    # >
    "IGUAL",                    # =
    # operadores unarios
    "NEGACAO",                  # !
    # simbolos
    "ABRE_PARENTESE",           # (
    "FECHA_PARENTESE",          # )
    "ABRE_COLCHETE",            # [
    "FECHA_COLCHETE",           # ]
    "VIRGULA",                  # ,
    "DOIS_PONTOS",              # :
    "ATRIBUICAO",               # :=
]

# Palavras reservas (tipos, estrutura de repetições e condicionais, ler input e escrever output e retorno)
reserved_words = {
    "se": "SE",
    "então": "ENTAO",
    "senão": "SENAO",
    "fim": "FIM",
    "repita": "REPITA",
    "flutuante": "FLUTUANTE",
    "retorna": "RETORNA",
    "até": "ATE",
    "leia": "LEIA",
    "escreva": "ESCREVA",
    "inteiro": "INTEIRO",
}

# Adiciona os tokens das palavras reservadas a lista de tokens
tokens = tokens + list(reserved_words.values())

digito = r"([0-9])"
letra = r"([a-zA-ZáÁãÃàÀéÉíÍóÓõÕ])"
sinal = r"([\-\+]?)"

""" 
    id deve começar com uma letra
"""
id = (
    r"(" + letra + r"(" + digito + r"+|_|" + letra + r")*)"
)  # o mesmo que '((letra)(letra|_|([0-9]))*)'

# Expressão regular para identificação de um número inteiro
inteiro = r"\d+"

# Expressão regular para identificação de um número flutuante
flutuante = (
    r'\d+[eE][-+]?\d+|(\.\d+|\d+\.\d*)([eE][-+]?\d+)?'
    )

# Expressão regular para identificação de uma notação científica
notacao_cientifica = (
    r"(" + sinal + r"([1-9])\." + digito + r"+[eE]" + sinal + digito + r"+)"
)  # o mesmo que '(([-\+]?)([1-9])\.([0-9])+[eE]([-\+]?)([0-9]+))'

# Expressões Regulares para identificação do lexema de símbolos, operadores lógicos e relacionais.
# Símbolos.
t_MAIS = r'\+'
t_MENOS = r'-'
t_MULTIPLICACAO = r'\*'
t_DIVISAO = r'/'
t_ABRE_PARENTESE = r'\('
t_FECHA_PARENTESE = r'\)'
t_ABRE_COLCHETE = r'\['
t_FECHA_COLCHETE = r'\]'
t_VIRGULA = r','
t_ATRIBUICAO = r':='
t_DOIS_PONTOS = r':'

# Operadores Lógicos.
t_E_LOGICO = r'&&'
t_OU_LOGICO = r'\|\|'
t_NEGACAO = r'!'

# Operadores Relacionais.
t_DIFERENCA = r'<>'
t_MENOR_IGUAL = r'<='
t_MAIOR_IGUAL = r'>='
t_MENOR = r'<'
t_MAIOR = r'>'
t_IGUAL = r'='

@TOKEN(id)
def t_ID(token):
    token.type = reserved_words.get(
        token.value, "ID"
    )  # não é necessário fazer regras/regex para cada palavra reservada
    # se o token não for uma palavra reservada automaticamente é um id
    # As palavras reservadas têm precedências sobre os ids

    return token

@TOKEN(notacao_cientifica)
def t_NUM_NOTACAO_CIENTIFICA(token):
    return token

@TOKEN(flutuante)
def t_NUM_PONTO_FLUTUANTE(token):
    return token

@TOKEN(inteiro)
def t_NUM_INTEIRO(token):
    return token

t_ignore = " \t"

# para poder contar as quebras de linha dentro dos comentarios
def t_COMENTARIO(token):
    r"(\{((.|\n)*?)\})"
    token.lexer.lineno += token.value.count("\n")

# Expressão regular para identificação da quebra de uma linha
def t_newline(token):
    r"\n+"
    token.lexer.lineno += len(token.value)

# Caso padrão caso um lexema inválido seja identificado
def t_error(token):

    line = token.lineno

    if (status_mode):
        debug_message = "Caracter inválido '%s' encontrado na linha '%s'" % (token.value[0], token.lineno)
        print(debug_message)
    else:
        message = "Caracter inválido '%s'" % token.value[0]
        print(message)

    token.lexer.skip(1)


def main():
    aux = argv[1].split('.')
    global status_mode;
    status_mode = False

    # Verifico de passou o parametro para executar em modo "debug"
    if len(argv) > 2:
        if argv[2] == "debug":
            status_mode = True

    # Verifica se o código passado como parametro é tpp
    if aux[-1] != 'tpp':
        error_message = "ERRO: Estamos esperando por um arquivo .tpp, porém recebemos como entrada um arquivo .%s" % aux[-1] 
        print("\n")
        print(error_message)
        print("\n")
        raise IOError("Not a .tpp file!")
        
    # Abre o arquivo passado como parametro
    data = open(argv[1])

    source_file = data.read()
    lexer.input(source_file)

    # Passa por todo o arquivo
    while True:
      tok = lexer.token()
      if not tok: 
        break 
        
    # Retorno os tokens encontrados  
      print(tok.type)

# Build the lexer.
# __file__ = "lex.py"
lexer = lex.lex(optimize=True,debug=True,debuglog=log)

if __name__ == "__main__":
    main()
