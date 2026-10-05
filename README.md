###README

##Rodando o codigo
Este projeto foi realizado com o gerenciador de projetos "uv" (https://docs.astral.sh/uv/)
#Para rodar testes utilize:
#Todos os testes
uv run --env-file .env pytest -m "live or not live"
#Todos os testes com exceção do golden (Para economizar token por exemplo)
uv run --env-file .env pytest -m "not live"
#Testes somente do golden dataset
uv run --env-file .env pytest -m live
#Para rodar o codigo principal (smoke test) 
uv run --env-file .env trab_final   

##Variáveis (.env)
O arquivo com configuração de váriaveis está em trab_final/.env

##Execuções de testes e log
Existe um processo de log para registrar o que já foi testado, e identificar melhor o porque houve erro. Isso me ajudou muito no desenvolvimento, e estou deixando na solução, pois acho uma funcionalidade excelente. Fiz alguns testes no final do desenvolvimento para evidenciar a funcionalidade dos testes

#Usar dados cacheados
Para a execução de testes não floodar o servidor AURA, é utilizado a opção de usar informações cacheadas, caso a pergunta seja exatamente a mesma.
Para habilitar basta atribuir o valor '1' à variavel de ambiente AURA_MEMO.
Neste caso, a solução irá armazenar pesquisas ao AURA ja realizadas.

OBS: Esta funcionalidade foi utilizada para conseguir construir o golden dataset

##Testes de tamanho de resposta
Durante o desenvolvimento, foi encontrado que quando a aURA tentava responder com uma string muito grande o agente se perdia e não conseguia finalizar o json, e acabava vindo um json semi formatado.
Foi criado um teste para isso (test_resposta_longa_nao_quebra_formato)

##Testes de alucinação
Foi criado dois testes: um com uma pergunta fora dos documentos, e outra com respostas possiveis nos documentos, mas verifica-se se a resposta existe de fato no documento (ou seja, se ele não alucinou sem avisar)

##Golden Dataset
O golden dataset está no arquivo golden_dataset.json e é utilizado para testes relacionados. Para gravar o golden_dataset pode-se utilizar o comando abaixo
uv run --env-file .env python -m trab_final.gravar_golden
#Testes com Golden Dataset
Além disso, para testar os dados com golden dataset é necessário lançar o uso do seguinte comando
uv run --env-file .env pytest -m live

##Observações adicionais
Atualmente o teste está dando 4 falhas de fairness. Apesar de fazerem sentido, pelo retorno, vale levantar que o erro tem relação com erros de trucamento e quebra de formato (test_resposta_longa_nao_quebra_formato), e assim um erro leva ao outro. Como é o retorno que estou recebendo da API, decidi documentar aqui, mas não forçar uma correção ou coisa assim.