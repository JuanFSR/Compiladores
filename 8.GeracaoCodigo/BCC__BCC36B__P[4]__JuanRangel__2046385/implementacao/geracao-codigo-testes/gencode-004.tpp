inteiro: n
inteiro: soma

inteiro principal()
	n := 10
	soma := 0
{	repita
		soma := soma + n
		n := n - 1
	até n = 0}

	leia(soma)
	leia(n)
	escreva(soma)

	retorna(0)
fim
