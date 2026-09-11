# Especificação de transação e idempotência

## Objetivo

Garantir que cada movimentação produza exatamente um efeito observável no estoque, mesmo quando o cliente repete a chamada, e que saídas concorrentes não tornem o saldo negativo.

## Entrada relevante para idempotência

O hash canônico inclui:

- identificador do usuário autenticado;
- identificador do produto;
- tipo `ENTRY` ou `EXIT`;
- quantidade;
- motivo após normalização definida no contrato.

Campos de transporte, timestamps do servidor e identificadores de correlação não entram no hash.

## Algoritmo proposto

1. Validar sessão no BFF, proteção CSRF, papel, corpo e `Idempotency-Key`.
2. Fazer leitura forte do registro de idempotência.
3. Se existir com o mesmo `requestHash`, devolver `responseStatus` e `responseBody` armazenados.
4. Se existir com hash diferente, devolver `409 IDEMPOTENCY_KEY_REUSED`.
5. Fazer leitura forte do produto e calcular saldo resultante.
6. Executar uma transação com três ações:
   - atualizar o produto sob condição de `status = ACTIVE`, `version = expectedVersion` e, para saída, `currentStock >= quantity`;
   - inserir a movimentação com condição de inexistência;
   - inserir idempotência com condição de inexistência.
7. Em sucesso, devolver `201` e os dados da movimentação.

## Expressão conceitual de atualização

Para saída:

```text
ConditionExpression:
  #status = :active AND #version = :expectedVersion AND currentStock >= :quantity

UpdateExpression:
  SET currentStock = currentStock - :quantity,
      #version = #version + :one,
      updatedAt = :now
```

Para entrada, a condição de saldo é omitida e a operação soma a quantidade.

## Mapeamento de falhas

| Condição | Código HTTP | Código funcional | Efeito |
| --- | ---: | --- | --- |
| Chave repetida e hash igual | resposta original | `IDEMPOTENT_REPLAY` apenas em log/métrica | Nenhuma nova escrita |
| Chave repetida e hash diferente | 409 | `IDEMPOTENCY_KEY_REUSED` | Nenhuma escrita |
| Produto inexistente | 404 | `PRODUCT_NOT_FOUND` | Nenhuma escrita |
| Produto inativo | 409 | `PRODUCT_INACTIVE` | Nenhuma escrita |
| Saldo insuficiente | 409 | `INSUFFICIENT_STOCK` | Nenhuma escrita |
| Versão concorrente | 409 | `CONCURRENT_MODIFICATION` | Nenhuma escrita |
| Payload inválido | 400 | `INVALID_REQUEST` | Nenhuma escrita |

## Retenção

O atributo `expiresAt` permite Time to Live (TTL), mas a duração da janela de idempotência permanece em aberto. Nenhum agente deve escolher esse valor sem decisão humana.
