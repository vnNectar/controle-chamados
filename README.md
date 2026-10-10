 Sistema de Controle de Chamados de Manutenção

Projeto de Web Back End desenvolvido em Python, usando Flask e SQLite.

 Problema e solução

Em uma pequena empresa, os pedidos de manutenção podem chegar por mensagens ou ficar anotados em lugares diferentes. Isso dificulta o acompanhamento e pode fazer com que alguns pedidos sejam esquecidos.

Para resolver esse problema, foi desenvolvida uma API que centraliza os chamados. Com ela, é possível registrar o problema, informar o local e atualizar o status conforme a manutenção acontece.

O sistema não possui uma interface visual. As operações são realizadas por requisições HTTP, e as respostas são enviadas em JSON.

## O que o sistema faz

- Cadastra chamados de manutenção.
- Lista os chamados e filtra por status.
- Consulta um chamado pelo ID.
- Atualiza o status para `aberto`, `em andamento` ou `concluido`.
- Exclui um chamado cadastrado por engano.
- Protege o acesso aos chamados com uma chave de API.

## Tecnologias utilizadas

 Tecnologia e Motivo da escolha 

  Python - Já foi estudado durante o curso e permite escrever um código fácil de acompanhar. 
  
  Flask - Facilita a criação das rotas da API e atende ao tamanho do projeto. 
  
  SQLite - Salva os dados em um arquivo e não precisa de um servidor de banco separado.
  
  Ambiente  virtual - Mantém as dependências do projeto organizadas e separadas de outros projetos. 
  
  Git e GitHub - Permitem registrar as alterações e disponibilizar o trabalho. 

A infraestrutura funciona no próprio computador. Isso simplifica a configuração e permite executar e demonstrar o projeto sem contratar hospedagem.

## Organização e arquitetura

Foi utilizada uma arquitetura monolítica, ou seja, o sistema funciona como uma única aplicação. Para manter o código organizado, as responsabilidades foram divididas:

 Arquivo e Responsabilidade
 
 `app.py` - Rotas da API, validações, verificação da chave e respostas 
 
 `banco.py` - Conexão com o banco e operações de cadastro, consulta, atualização e exclusão 
 
 `requirements.txt` - Dependência necessária para executar o projeto 
 
 `.gitignore` - Define quais arquivos não devem ser enviados ao GitHub 
 
 `README.md` - Documentação do sistema 

A integração acontece por chamadas de funções. O Flask recebe a requisição, o código verifica os dados e utiliza as funções de `banco.py` para acessar o SQLite. Depois, a API retorna o resultado em JSON.

## Banco de dados

O banco é criado automaticamente no arquivo `chamados.db`. Ele possui uma tabela chamada `chamados`, com os campos:

 Campo  e Informação armazenada
 
 `id` - Identificador gerado automaticamente 
 
 `titulo` - Resumo do problema 
 
 `descricao` - Detalhes do problema 
 
 `local` - Local que precisa de manutenção 
 
 `status` - Situação atual, começando como `aberto` 
 
 `criado_em` - Data e hora do cadastro, em UTC 

Título, descrição e local são obrigatórios. A API aceita até 100 caracteres no título e no local, e até 1.000 na descrição.

## Rotas da API

Endereço base: `http://127.0.0.1:5000`

 Método, Rota e Operação 
 
 GET  `/`  Verificar se a API está funcionando 

 GET  `/chamados` - Listar chamados 
 
 GET  `/chamados?status=aberto` - Filtrar por status

 GET  `/chamados/{id}` - Consultar pelo ID 
 
 POST  `/chamados` - Cadastrar 
 
 PATCH  `/chamados/{id}` - Atualizar o status 
 
 DELETE  `/chamados/{id}` - Excluir 

O `{id}` deve ser substituído pelo número do chamado.

Exemplo de JSON para cadastrar:

```json
{
  "titulo": "Ar-condicionado com defeito",
  "descricao": "O equipamento liga, mas nao resfria a sala.",
  "local": "Sala 2"
}
```

Exemplo para atualizar o status:

```json
{
  "status": "concluido"
}
```

A API utiliza os códigos HTTP `200` para sucesso, `201` para cadastro, `400` para dados inválidos, `401` para falha de autenticação e `404` para chamado não encontrado.

## Segurança

As rotas de chamados exigem uma chave enviada no cabeçalho `X-API-Key`. Essa chave é configurada pela variável de ambiente `CHAVE_API` e fica fora do código. Apenas a rota inicial `/` pode ser acessada sem ela.

Também são utilizados:

- Validação dos campos e dos status.
- Limites de tamanho para os textos.
- Consultas SQL parametrizadas para evitar injeção de SQL.
- Modo de depuração desativado.
- `.gitignore` para não enviar o banco local e arquivos privados ao GitHub.

A chave é compartilhada, então o sistema ainda não possui usuários individuais ou diferentes permissões. Para este projeto, ela permite demonstrar um controle básico de acesso.

## Como executar

As instruções abaixo utilizam PowerShell no Windows, dentro da pasta do projeto.

### 1. Preparar o ambiente

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Iniciar o servidor no primeiro terminal

```powershell
$env:CHAVE_API = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
Set-Content -Path "$env:TEMP\controle_chamados-chave.txt" -Value $env:CHAVE_API -Encoding ASCII
.\.venv\Scripts\python.exe app.py
```

Esse bloco gera a chave, guarda uma cópia temporária para o teste e inicia a API.

### 3. Consultar no segundo terminal

```powershell
$chave = (Get-Content -Raw "$env:TEMP\controle_chamados-chave.txt").Trim()
$cabecalhos = @{ "X-API-Key" = $chave }

Invoke-RestMethod -Uri "http://127.0.0.1:5000/chamados" -Method Get -Headers $cabecalhos | Format-List

Remove-Item "$env:TEMP\controle_chamados-chave.txt"
```

Em uma instalação nova, a consulta retorna uma lista vazia. Para cadastrar, envie um POST com o JSON apresentado anteriormente, usando `Content-Type: application/json` e o cabeçalho `X-API-Key`.

Para parar o servidor, pressione `Ctrl + C` no primeiro terminal. Após alterar o código, é necessário salvar e reiniciar. Se esse terminal for fechado, a chave precisa ser configurada novamente.

## Testes realizados

Durante o desenvolvimento, foram testados o cadastro, a listagem, a atualização, a exclusão de um chamado temporário e os filtros por status.

Também foi confirmado que o sistema bloqueia acesso sem chave, rejeita título vazio e status inválido, e informa quando um ID não existe. Por fim, um chamado foi alterado para `concluido` e apareceu na consulta de concluídos.

## Considerações finais

O sistema atende à proposta de organizar os pedidos de manutenção e acompanhar sua situação. Foi mantido um escopo pequeno para facilitar o entendimento do código e a demonstração.

A execução é local e utiliza o servidor de desenvolvimento do Flask. Para uso na internet, seriam necessários ajustes de infraestrutura, HTTPS e revisão das medidas de segurança.
