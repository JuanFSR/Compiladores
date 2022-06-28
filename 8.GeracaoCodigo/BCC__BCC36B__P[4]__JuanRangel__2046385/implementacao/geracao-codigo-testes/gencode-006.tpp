

inteiro soma(inteiro: a, inteiro:b)
    retorna(a + b)
fim

inteiro principal()
    inteiro: a
    inteiro: b
    inteiro: c
    inteiro: i

    b := 1
    i := 0

    repita
        leia(a)
        leia(b)
        c := soma(a, b)
        escreva(c)
        i := i + b
    até i = 5

    retorna(0)
fim
