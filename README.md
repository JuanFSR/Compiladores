# Compiladores
Este repositório foi desenvolvido com o objetivo de registrar as atividades desenvolvidas durante a disciplina de Compiladores. Para construção deste compilador, utilizaremos uma linguagem simplificada desenvolvida especificamente para utilização desta matéria, chamada de TPP. O desenvolvimento deste compilador será separado em três partes, sendo elas: <a href= "https://github.com/JuanFSR/Compiladores/tree/main/3.AnaliseLexica/BCC__BCC36B__P%5B1%5D__JuanRangel_2046385"> Análise Léxica</a>, <a href="https://github.com/JuanFSR/Compiladores/tree/main/6.AnaliseSintatica/BCC__BCC36B__P%5B2%5D__JuanRangel__2046385"> Análise Sintática </a>, <a href="https://github.com/JuanFSR/Compiladores/tree/main/7.AnaliseSemantica/BCC__BCC36B__P%5B3%5D__JuanRangel__2046385"> Análise Semântica </a> e <a href="https://github.com/JuanFSR/Compiladores/tree/main/8.GeracaoCodigo/BCC__BCC36B__P%5B4%5D__JuanRangel__2046385/implementacao">Geração de Código </a>.

# Gramática da linguagem TPP
Como dito anteriormente, a <a href="https://docs.google.com/document/d/1e7_M-bD1RUbJAnyR8rZyJ35vKbYEN6KQG4l5L8FQ7_I/edit">gramática da linguagem TPP</a> é simplificada, sendo composta de estruturas de repetição, vetor e estruturas condicionais.

# PLY
Para implementação do sistema de varredura e análise léxica foi utilizado a biblioteca
<a href="https://www.dabeaz.com/ply/ply.html"> PLY (Python Lex-Yacc)</a>, que possui dois diferentes módulos, o lex.py e o yacc.py.
O primeiro módulo é o lex.py, o qual foi utilizado na implementação da Análise Léxica. Neste módulo através de expressões regulares, é possível identificar
os lexemas recebidos como entrada, através de um código TPP, e obter os seus respectivos
tokens, retornando então como saída, uma lista de tokens.
Já o módulo Yacc (yet another compiler-compiler)  ́e utilizado na implementação do analisador sintático, que utiliza o método de
análise LALR(1). 