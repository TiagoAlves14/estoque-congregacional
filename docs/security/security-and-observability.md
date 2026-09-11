# Segurança e observabilidade

## Fronteiras de confiança

1. Navegador do usuário para CloudFront e Cognito.
2. Navegador para API Gateway pela internet.
3. API Gateway para aplicação Lambda dentro da conta AWS.
4. Lambda para DynamoDB e CloudWatch sob papéis Identity and Access Management (IAM).

## Controles propostos

| Risco | Controle arquitetural |
| --- | --- |
| Roubo de credenciais | Senhas não são tratadas pela aplicação; autenticação fica no provedor de identidade. |
| Interceptação | HTTPS obrigatório em todos os acessos externos. |
| Roubo de token por script | Authorization Code com PKCE e proibição de persistir token em `localStorage`; política final de sessão ainda deve ser validada. |
| Acesso indevido | JWT validado no gateway e autorização por papel repetida no caso de uso. |
| Reenvio de movimentação | `Idempotency-Key`, hash do conteúdo e resposta armazenada. |
| Saída concorrente | Versão do produto, condição de saldo e transação DynamoDB. |
| Injeção e payload excessivo | JSON Schema, limites de tamanho, listas permitidas e rejeição de propriedades desconhecidas. |
| Exposição em logs | Não registrar senha, token, e-mail, corpo completo ou resposta de autenticação. |
| Abuso e custo | Limites no API Gateway, orçamento e alarmes; valores aguardam definição. |
| Privilégio excessivo | Função Lambda acessa somente a tabela e os recursos de observabilidade necessários. |

## Claims mínimas esperadas

- `sub`: identificador estável do usuário.
- `iss`: emissor permitido.
- `aud` ou `client_id`: cliente esperado, conforme o tipo de token.
- `exp`: expiração.
- grupo ou papel validado para `ADMIN` e `OPERATOR`.

A aplicação não deve usar e-mail como identificador de autorização.

## Logs estruturados

Cada evento técnico deve conter, quando aplicável:

- timestamp em UTC;
- nível;
- `correlationId`;
- `operationId` do OpenAPI;
- `actorId` derivado de `sub`;
- `productId`;
- resultado funcional;
- duração em milissegundos.

Não registrar JWT, cabeçalhos de autenticação, chave de idempotência completa, senha ou dados pessoais desnecessários.

## Métricas candidatas

| Métrica | Objetivo |
| --- | --- |
| `ApiRequests` por operação e status | Identificar comportamento e erros da API. |
| `MovementCreated` por tipo | Acompanhar entradas e saídas. |
| `MovementRejected` por motivo | Detectar saldo insuficiente, produto inativo e conflitos. |
| `IdempotencyReplay` | Medir reenvios tratados com segurança. |
| `ConcurrentModification` | Detectar contenção anormal. |
| Duração da Lambda | Acompanhar degradação. |
| Erros e throttling de Lambda, API Gateway e DynamoDB | Detectar falhas técnicas ou limites. |

Os limiares dos alarmes não foram definidos e não devem ser inventados.

## Dados e retenção

O sistema armazena identificador técnico do usuário para auditoria. A necessidade de nome, e-mail ou outros dados pessoais não foi demonstrada. Retenção de movimentos, logs, backups e idempotência permanece em aberto.

