# ADR-002 — DynamoDB com single-table design

- **Status:** Proposto
- **Data:** 2026-09-11
- **Decisores:** a definir

## Contexto

Produtos, movimentações e respostas idempotentes possuem padrões de acesso previsíveis. A jornada crítica exige escrita condicional e transacional para impedir estoque negativo e histórico parcial.

## Decisão proposta

Usar uma tabela DynamoDB denominada logicamente `estoque-congregacional`, com chaves genéricas `PK` e `SK` para armazenar:

- produto e saldo atual;
- movimentações agrupadas pelo produto;
- registros de idempotência agrupados pelo usuário;
- índice secundário global para listar produtos por nome.

Os detalhes estão em [`docs/dynamodb/data-model.md`](../dynamodb/data-model.md).

## Alternativas consideradas

1. Banco relacional gerenciado: oferece transações e consultas flexíveis, mas mantém capacidade provisionada e operação maiores para uma carga pequena.
2. Múltiplas tabelas DynamoDB: leitura conceitualmente simples, porém dificulta alguns agrupamentos e aumenta a quantidade de recursos.
3. Armazenamento documental genérico: não oferece vantagem clara sobre os padrões de acesso já conhecidos.

## Consequências

### Positivas

- Baixa operação e integração direta com Lambda.
- Escrita condicional e transação para a jornada crítica.
- Histórico por produto obtido por consulta à mesma partição.

### Negativas e riscos

- Novos padrões de acesso podem exigir índices ou remodelagem.
- O modelo de chaves precisa ser rigorosamente documentado.
- Consultas analíticas e relatórios globais não são o objetivo desse armazenamento.
- A hipótese depende da confirmação de volume, custo e consultas necessárias.

## Critérios para aceite

- Padrões de acesso confirmados.
- Estimativa de volume e tamanho dos itens.
- Estratégia de backup, retenção e exportação definida.
- Teste de concorrência para saídas simultâneas.

