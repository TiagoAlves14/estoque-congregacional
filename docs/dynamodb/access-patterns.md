# Padrões de acesso DynamoDB

| ID | Caso de uso | Operação | Chave ou índice | Consistência |
| --- | --- | --- | --- | --- |
| AP-01 | Obter produto por ID | `GetItem` | `PK=PRODUCT#{id}`, `SK=METADATA` | Eventual para consulta comum; forte antes de movimentar |
| AP-02 | Listar produtos por nome | `Query` | `GSI1PK=CATALOG`, `GSI1SK` ordenado por nome | Eventual |
| AP-03 | Buscar produtos por prefixo | `Query` com `begins_with` | `GSI1PK=CATALOG`, `GSI1SK=NAME#{prefixo}` | Eventual |
| AP-04 | Listar histórico do produto | `Query` com `begins_with` | `PK=PRODUCT#{id}`, `SK=MOVEMENT#` | Eventual |
| AP-05 | Verificar idempotência | `GetItem` | `PK=IDEMPOTENCY#{actorId}`, `SK=KEY#{key}` | Forte |
| AP-06 | Criar produto | `PutItem` condicional | Produto | Forte na escrita |
| AP-07 | Registrar movimentação | `TransactWriteItems` | Produto, movimento e idempotência | Transacional |

## Paginação

- A API recebe `cursor` opaco e `limit` entre 1 e 100.
- O cursor representa o `LastEvaluatedKey` serializado e assinado ou protegido contra adulteração.
- A implementação não deve expor chaves internas diretamente sem proteção.

## Padrões ainda não cobertos

- Histórico global por período.
- Relatórios agregados.
- Busca por código de barras.
- Produtos de várias igrejas.

Esses padrões não devem ser adicionados ao modelo sem confirmação de requisito e revisão do ADR-002.

