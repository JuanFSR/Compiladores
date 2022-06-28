all:
	clang -emit-llvm -S io.c
	llc -march=x86-64 -filetype=obj io.ll -o io.o
	python3 geracao_cod.py geracao-codigo-testes/gencode-017.tpp --ntabela
	llvm-link modulo_geracao_cod.ll io.ll -o modulo_geracao_cod.bc
	clang modulo_geracao_cod.bc -o modulo_geracao_cod.o

clean:
	rm *.ll *.o *.bc