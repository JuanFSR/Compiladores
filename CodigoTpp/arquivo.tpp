{Código tpp do Insertion Sort}

insertionSort(inteiro: x, inteiro: arr)
	inteiro: chave,i, j

	i := 1

	repita 
        i := i + 1
        chave := arr[i]
		j := i - 1

		repita (j >= 0 e arr[j] > chave)
			arr[j + 1] := arr[j]
			j := j - 1
        até (j < 0 && arr[j] < chave)
        fim
	até i < x	
    fim
		
        arr[j + 1] = chave

    até i < x
	
fim

{Função que passa pelo array e escreve na saída}
escreveArray(inteiro: x, inteiro: arr[])

	inteiro: i 
	i := 0

    repita 
        i := i + 1
		escreva(arr[i] )
	até i < x
	fim

fim


{Função principal}
main()
	inteiro: arr 
	arr := [10, 8, 7, 10, 4]
	
	inteiro: x 
	x := 5
    
	insertionSort(x,arr)
	escreveArray(x,arr)

fim
