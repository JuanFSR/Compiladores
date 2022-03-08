{Código tpp do Insertion Sort}

insertionSort(inteiro: arr, inteiro: n)
	inteiro: i, key, j
	repita 
        i = i + 1
        key = arr[i];
		j = i - 1;

		repita (j >= 0 && arr[j] > key)
			arr[j + 1] = arr[j];
			j = j - 1;
        até (j < 0 && arr[j] < key)
        fim
    fim
		
        arr[j + 1] = key;

    até i < n
	
fim

arrayPrint(inteiro: arr[], inteiro: n)
{
	inteiro: i := 0;
    repita 
        i = i + 1
		escreva(arr[i])
	escreva(endl)
}

int main()
	inteiro: arr := [12, 11, 13, 5, 6 ]
	inteiro: lenArr := 5
    inteiro n := lenArr / arr[2]

	insertionSort(arr, n);
	arrayPrint(arr, n);

	retorna 0
fim
