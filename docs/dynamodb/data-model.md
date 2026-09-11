# Modelo de dados DynamoDB

## Status

Especificação vinculada ao ADR-002, ainda com status `Proposto`.

## Tabela

- Nome lógico: `estoque-congregacional`
- Chave de partição: `PK` (`String`)
- Chave de ordenação: `SK` (`String`)
- Índice secundário global `GSI1`: `GSI1PK` + `GSI1SK`
- Time to Live (TTL): atributo numérico `expiresAt`, somente em registros temporários

## Entidades

### Produto

| Atributo | Exemplo | Observação |
| --- | --- | --- |
| `PK` | `PRODUCT#018f...` | Identificador do agregado. |
| `SK` | `METADATA` | Item atual do produto. |
| `entityType` | `PRODUCT` | Discriminador. |
| `id` | UUID | Identificador público. |
| `name` | `Copo descartável 200 ml` | Nome exibido. |
| `normalizedName` | `copo descartavel 200 ml` | Ordenação e busca por prefixo. |
| `category` | `DESCARTAVEIS` | Categoria funcional. |
| `unit` | `PACKAGE` | Unidade controlada. |
| `currentStock` | `12` | Saldo atual, inteiro não negativo. |
| `minimumStock` | `5` | Limite para indicação de estoque baixo. |
| `status` | `ACTIVE` | `ACTIVE` ou `INACTIVE`. |
| `version` | `7` | Controle otimista de concorrência. |
| `GSI1PK` | `CATALOG` | Agrupa produtos no catálogo. |
| `GSI1SK` | `NAME#copo descartavel 200 ml#018f...` | Ordena por nome e desempata por ID. |
| `createdAt` | ISO 8601 UTC | Data de criação. |
| `updatedAt` | ISO 8601 UTC | Última alteração. |

### Movimentação

| Atributo | Exemplo | Observação |
| --- | --- | --- |
| `PK` | `PRODUCT#018f...` | Agrupa o histórico do produto. |
| `SK` | `MOVEMENT#2026-09-11T03:00:00.000Z#0190...` | Ordenação cronológica. |
| `entityType` | `MOVEMENT` | Discriminador. |
| `id` | UUID | Identificador público. |
| `productId` | UUID | Referência ao produto. |
| `movementType` | `EXIT` | `ENTRY` ou `EXIT`. |
| `quantity` | `2` | Inteiro positivo. |
| `resultingStock` | `10` | Saldo após a operação. |
| `reason` | `Uso no evento mensal` | Justificativa informada. |
| `performedBy` | identificador do usuário | Claim `sub`, não o e-mail. |
| `idempotencyKey` | UUID fornecido pelo cliente | Rastreia reenvios. |
| `createdAt` | ISO 8601 UTC | Momento imutável da operação. |

### Idempotência

| Atributo | Exemplo | Observação |
| --- | --- | --- |
| `PK` | `IDEMPOTENCY#user-sub` | Escopo por usuário. |
| `SK` | `KEY#request-uuid` | Chave fornecida pelo cliente. |
| `entityType` | `IDEMPOTENCY` | Discriminador. |
| `requestHash` | SHA-256 em hexadecimal | Hash do conteúdo canônico. |
| `movementId` | UUID | Movimento criado. |
| `responseStatus` | `201` | Status a repetir. |
| `responseBody` | objeto | Resposta mínima serializável. |
| `createdAt` | ISO 8601 UTC | Criação do registro. |
| `expiresAt` | epoch seconds | TTL; duração ainda não definida. |

## Normalização do nome

A proposta é converter para minúsculas, remover espaços excedentes e diacríticos somente para ordenação e busca. O valor original permanece em `name`. A regra precisa ser implementada e testada de forma determinística.

## Estoque baixo

Na primeira versão, `lowStock` é derivado durante a listagem por `currentStock <= minimumStock`. Não há índice exclusivo para estoque baixo porque o volume ainda é desconhecido. Se a consulta paginada se mostrar insuficiente, um índice esparso deverá ser proposto em novo ADR.

## Exemplo

Consulte [`example-items.json`](example-items.json). Os identificadores e dados são fictícios.

