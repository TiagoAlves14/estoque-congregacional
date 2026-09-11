# Cenários de aceitação arquitetural

Os cenários abaixo orientam testes automatizados futuros. Eles validam principalmente regras que poderiam ser perdidas quando um agente transformar a arquitetura em código.

## CA-01 — Administrador cadastra produto

```gherkin
Dado que um usuário ADMIN está autenticado
Quando cadastrar um produto válido
Então o produto deve ser criado com saldo zero e versão 1
E nenhuma movimentação inicial deve ser criada implicitamente
```

## CA-02 — Operador não mantém catálogo

```gherkin
Dado que um usuário OPERATOR está autenticado
Quando tentar cadastrar ou alterar um produto
Então a API deve responder 403
E nenhum item deve ser gravado
```

## CA-03 — Entrada de estoque

```gherkin
Dado um produto ativo com saldo 5
Quando um usuário autorizado registrar entrada de 3 unidades
Então o saldo deve passar para 8
E uma movimentação ENTRY com saldo resultante 8 deve existir
E produto, movimento e idempotência devem ser persistidos atomicamente
```

## CA-04 — Saída com saldo suficiente

```gherkin
Dado um produto ativo com saldo 10
Quando um usuário autorizado registrar saída de 4 unidades
Então a API deve responder 201
E o saldo deve passar para 6
E uma movimentação EXIT com saldo resultante 6 deve existir
```

## CA-05 — Saída com saldo insuficiente

```gherkin
Dado um produto ativo com saldo 3
Quando um usuário autorizado solicitar saída de 4 unidades
Então a API deve responder 409 com código INSUFFICIENT_STOCK
E o saldo deve continuar 3
E nenhuma movimentação ou idempotência concluída deve ser criada
```

## CA-06 — Repetição idempotente

```gherkin
Dado que uma saída foi concluída com uma Idempotency-Key
Quando a mesma chave e o mesmo conteúdo forem enviados novamente pelo mesmo usuário
Então a resposta original deve ser devolvida
E o saldo não deve ser alterado novamente
E não deve existir uma segunda movimentação
```

## CA-07 — Chave reutilizada com outro conteúdo

```gherkin
Dado que uma Idempotency-Key já foi usada
Quando o mesmo usuário repetir a chave com quantidade ou produto diferente
Então a API deve responder 409 com código IDEMPOTENCY_KEY_REUSED
E nenhum dado deve ser alterado
```

## CA-08 — Produto inativo

```gherkin
Dado um produto inativo
Quando um usuário tentar registrar entrada ou saída
Então a API deve responder 409 com código PRODUCT_INACTIVE
E nenhum dado deve ser alterado
```

## CA-09 — Saídas concorrentes

```gherkin
Dado um produto ativo com saldo 5 e uma versão conhecida
Quando duas saídas concorrentes de 4 unidades forem processadas
Então somente uma transação deve ser concluída
E a outra deve falhar por saldo insuficiente ou conflito de versão
E o saldo final deve ser 1
E deve existir somente uma nova movimentação
```

## CA-10 — Usuário não autenticado

```gherkin
Dado que a requisição não possui uma sessão válida no BFF
Quando qualquer rota protegida for chamada
Então a API deve responder 401
E a aplicação de estoque não deve executar o caso de uso
```

## CA-11 — Indicação de estoque baixo

```gherkin
Dado um produto com estoque mínimo 5
Quando seu saldo atual for 5 ou menos
Então a representação do produto deve retornar lowStock igual a true
```

## CA-12 — Histórico imutável

```gherkin
Dado que uma movimentação foi concluída
Quando for necessário corrigir a operação
Então a movimentação original não deve ser alterada ou apagada
E a correção deve aguardar uma regra explícita para nova movimentação compensatória
```

## CA-13 — Tokens e segredo não chegam ao frontend

```gherkin
Dado que o usuário concluiu o login no Cognito
Quando o BFF processar o callback de autenticação
Então access, ID e refresh tokens devem permanecer somente no servidor
E o client_secret não deve aparecer no bundle, respostas HTTP, armazenamento ou logs do navegador
E o navegador deve receber apenas o identificador opaco da sessão em cookie HttpOnly
```

## CA-14 — Cookie de sessão protegido

```gherkin
Dado que o callback OAuth foi validado
Quando o BFF criar uma sessão
Então deve enviar o cookie __Host-ec_session com Secure, HttpOnly, SameSite=Strict e Path=/
E o cookie não deve possuir o atributo Domain
E uma nova autenticação deve substituir o identificador de sessão anterior
```

## CA-15 — Proteção contra CSRF

```gherkin
Dado que existe uma sessão válida no cookie
Quando uma operação que altera estado não possuir um X-CSRF-Token válido e origem permitida
Então a API deve responder 403
E nenhuma regra de negócio ou gravação deve ser executada
```

## CA-16 — Sessão expirada ou revogada

```gherkin
Dado que o item da sessão está expirado ou revogado
Quando o cookie correspondente for apresentado
Então o BFF deve responder 401 mesmo que o item ainda aguarde remoção pelo TTL
E não deve renovar tokens nem executar o caso de uso
```

## CA-17 — Segredo inacessível ao frontend

```gherkin
Dado que o BFF precisa autenticar o app client confidencial
Quando recuperar o client_secret
Então apenas o papel IAM do BFF pode ler o ARN configurado no Secrets Manager
E o valor não deve ser incluído em logs ou mensagens de erro
E uma falha de recuperação deve interromper o login de forma fechada
```
