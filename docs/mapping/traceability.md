# Matriz de rastreabilidade

| Requisito ou regra | Contrato | Modelo de dados | Diagrama | Cenário |
| --- | --- | --- | --- | --- |
| RF-01 — autenticação | `/auth/*` e `cookieAuth` | Store de sessões e `performedBy` | autenticação e containers | CA-10, CA-13, CA-14, CA-16 |
| RF-02 — cadastrar produto | `POST /api/products` | Produto | containers | CA-01, CA-02 |
| RF-03 — listar produtos | `GET /api/products` | GSI1 catálogo | containers | a detalhar |
| RF-04 — consultar produto | `GET /api/products/{productId}` | Produto | containers | a detalhar |
| RF-05 — alterar produto | `PATCH /api/products/{productId}` | Produto e `version` | containers | CA-02, CA-08 |
| RF-06 — registrar entrada | `POST /api/products/{productId}/movements` | Transação | sequência | CA-03 |
| RF-07 — registrar saída | `POST /api/products/{productId}/movements` | Transação condicional | sequência | CA-04, CA-05, CA-09 |
| RF-08 — consultar histórico | `GET /api/products/{productId}/movements` | Movimentação sob `PRODUCT#{id}` | containers | CA-12 |
| RF-09 — estoque mínimo | campo `lowStock` | Derivado de saldo e mínimo | containers | CA-11 |
| RF-10 — repetição segura | `Idempotency-Key` | Registro de idempotência | sequência | CA-06, CA-07 |
| RN-02 — saldo não negativo | erro 409 | condição `currentStock >= quantity` | sequência | CA-05, CA-09 |
| RN-07 — atomicidade | resposta 201 ou 409 | `TransactWriteItems` | sequência | CA-03, CA-04, CA-09 |
| RNF-07 — nenhum token no frontend | `cookieAuth` | Tokens no store de sessões | autenticação | CA-13, CA-14 |
| RNF-08 — sessão e CSRF | `X-CSRF-Token` | Hash CSRF na sessão | sequência | CA-15, CA-16 |
| RNF-09 — segredo no backend | endpoints `/auth/*` | Secrets Manager, fora do domínio | autenticação e implantação | CA-17 |

## Decisões relacionadas

- ADR-001 define a topologia serverless.
- ADR-002 define o modelo de persistência.
- ADR-003 define autenticação e identidade.
- ADR-004 define atomicidade, concorrência e idempotência.
- ADR-005 mantém runtime e linguagem do backend como decisão pendente.
