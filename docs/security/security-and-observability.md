# Segurança e observabilidade

## Princípio adotado

O navegador é uma zona não confiável. Ele pode conter código JavaScript de terceiros, extensões ou uma falha de Cross-Site Scripting (XSS). Por isso, a baseline usa um Backend for Frontend (BFF): tokens OAuth, `client_secret` e credenciais AWS permanecem no backend; o navegador recebe somente um identificador opaco de sessão em cookie protegido.

Colocar um segredo no AWS Secrets Manager e depois entregá-lo ao frontend **não é uma proteção**. Assim que o valor chega ao navegador, qualquer usuário ou script naquele contexto pode extraí-lo.

## Fronteiras de confiança

1. Usuário e navegador para CloudFront, sempre por HTTPS.
2. Navegador para Cognito Managed Login durante a autenticação; a senha é informada somente nessa interface.
3. CloudFront e API Gateway para o BFF Lambda.
4. BFF para Cognito, Secrets Manager, store de sessões, banco de estoque e CloudWatch sob papéis IAM.
5. Store de sessões, que contém material sensível, separado logicamente dos dados funcionais de estoque.

## Requisitos de segurança da arquitetura

| ID | Requisito | Implementação arquitetural proposta |
| --- | --- | --- |
| SEC-01 | Nenhum segredo ou JWT no frontend | A SPA não recebe access, ID ou refresh token, `client_secret`, chave AWS ou credencial de banco. |
| SEC-02 | Segredo acessível somente pelo BFF | `client_secret` no Secrets Manager; leitura limitada ao ARN exato pelo papel IAM da Lambda, com auditoria, cache controlado e rotação. |
| SEC-03 | Sessão opaca e protegida | Cookie `__Host-ec_session` com valor aleatório de alta entropia, `Secure`, `HttpOnly`, `SameSite=Strict`, `Path=/` e sem `Domain`. |
| SEC-04 | Proteção contra CSRF | Operações mutáveis exigem `X-CSRF-Token` vinculado à sessão, validação de `Origin`/`Referer` e política de origem única. `SameSite` é defesa adicional, não a única. |
| SEC-05 | Integridade do login OAuth | BFF cria e valida `state`, `nonce`, `code_verifier` e `code_challenge`; a transação de login expira e é consumida uma única vez. |
| SEC-06 | Tokens somente no servidor | Tokens são armazenados no store de sessões com criptografia em repouso, TTL, expiração validada pela aplicação e possibilidade de revogação. |
| SEC-07 | Autorização no caso de uso | BFF resolve `actorId` e papéis da sessão e valida `ADMIN` ou `OPERATOR` em cada operação; API Gateway apenas roteia. |
| SEC-08 | Menor privilégio | Papéis diferentes e restritos para segredo, sessão, estoque, KMS e observabilidade; o frontend não possui IAM. |

## `client_id` não é `client_secret`

| Valor | É segredo? | Local permitido nesta baseline |
| --- | :---: | --- |
| `client_id` | Não | Configuração do BFF; sua exposição isolada não concede autenticação. |
| `client_secret` | Sim | Secrets Manager e memória do processo do BFF durante o uso. |
| Access, ID e refresh tokens | Sim | Store de sessões e memória do BFF; nunca na resposta à SPA. |
| Identificador opaco de sessão | Sim, por ser credencial de sessão | Cookie protegido; o JavaScript não consegue lê-lo por causa de `HttpOnly`. |
| Credenciais AWS | Sim | Fornecidas temporariamente à Lambda pelo papel IAM; nunca configuradas no frontend. |

## Uso do AWS Secrets Manager

- Armazenar apenas o segredo do app client, referenciado por ARN; `client_id` pode ser configuração não secreta.
- Conceder `secretsmanager:GetSecretValue` somente ao papel do BFF e somente para o segredo necessário.
- Se for usada uma chave KMS gerenciada pelo cliente, restringir também `kms:Decrypt` à chave e ao contexto necessários.
- Preferir a AWS Parameters and Secrets Lambda Extension ou cache equivalente para evitar uma chamada remota a cada login.
- Definir rotação e observar falhas sem registrar o valor do segredo.
- Falhar de forma fechada se o segredo não puder ser obtido; jamais usar fallback embutido no código ou variável exposta ao build da SPA.

## Sessão e proteção do navegador

- CloudFront apresenta um único domínio e encaminha `/auth` e `/api` ao API Gateway sem cache, preservando os cabeçalhos e cookies necessários.
- Após o callback OAuth, o BFF cria a sessão, armazena somente o hash do identificador como chave de busca e devolve o valor original apenas no cookie.
- O endpoint de sessão fornece à SPA um token CSRF vinculado à sessão; a SPA o mantém em memória e o envia no cabeçalho `X-CSRF-Token` em toda alteração de estado.
- O BFF rejeita sessão expirada mesmo antes de o TTL do DynamoDB remover fisicamente o item.
- Login renova o identificador da sessão; logout revoga a sessão no servidor e expira o cookie.
- A duração absoluta, o tempo ocioso, a política de renovação de token e o comportamento após mudança de papel ainda exigem decisão humana.

## Validação da identidade

Ao receber ou renovar tokens, o BFF valida pelo menos:

- assinatura com algoritmo permitido e chave do emissor;
- `iss` esperado;
- `aud` ou `client_id` esperado, conforme o token;
- `exp`, `iat` e tolerância de relógio definida;
- `nonce` no fluxo de login;
- grupo ou papel permitido para `ADMIN` e `OPERATOR`.

A aplicação usa `sub` como identificador estável do ator e não usa e-mail como chave de autorização.

## Demais controles

| Risco | Controle arquitetural |
| --- | --- |
| Interceptação | HTTPS obrigatório, HSTS e cookies `Secure`. |
| Cross-Site Scripting | Encoding de saída, CSP restritiva, dependências revisadas e ausência de tokens legíveis por JavaScript. |
| Reenvio de movimentação | `Idempotency-Key`, hash do conteúdo e resposta armazenada. |
| Saída concorrente | Versão do produto, condição de saldo e transação DynamoDB. |
| Injeção e payload excessivo | OpenAPI/JSON Schema, limites de tamanho, listas permitidas e rejeição de propriedades desconhecidas. |
| Exposição em logs | Não registrar senha, segredo, token, cookie, código OAuth, token CSRF, e-mail ou corpo completo. |
| Abuso e custo | Limites no API Gateway, orçamento e alarmes; valores aguardam definição. |

## Logs estruturados

Cada evento técnico deve conter, quando aplicável:

- timestamp em UTC;
- nível;
- `correlationId`;
- `operationId` do OpenAPI;
- `actorId` derivado da sessão;
- `productId`;
- resultado funcional;
- duração em milissegundos.

Identificadores de sessão, chave de idempotência e dados sensíveis devem ser omitidos ou representados por hash/truncamento não reversível adequado ao caso.

## Métricas candidatas

| Métrica | Objetivo |
| --- | --- |
| `AuthenticationSucceeded` e `AuthenticationFailed` | Detectar anomalias no login sem registrar credenciais. |
| `SessionRejected` por motivo | Acompanhar expiração, revogação e falha CSRF. |
| `SecretRetrievalFailed` | Detectar indisponibilidade ou permissão incorreta do segredo. |
| `ApiRequests` por operação e status | Identificar comportamento e erros da API. |
| `MovementCreated` por tipo | Acompanhar entradas e saídas. |
| `MovementRejected` por motivo | Detectar saldo insuficiente, produto inativo e conflitos. |
| `IdempotencyReplay` | Medir reenvios tratados com segurança. |
| `ConcurrentModification` | Detectar contenção anormal. |
| Erros e throttling de Lambda, API Gateway e DynamoDB | Detectar falhas técnicas ou limites. |

Os limiares dos alarmes não foram definidos e não devem ser inventados.

## Dados e retenção

O sistema armazena o identificador técnico do usuário para auditoria. A necessidade de nome, e-mail ou outros dados pessoais não foi demonstrada. Retenção de movimentos, logs, backups, idempotência e sessões permanece em aberto.

## Referências oficiais

- [IETF RFC 10017 — OAuth 2.0 for Browser-Based Applications, padrão BFF e cookies](https://datatracker.ietf.org/doc/rfc10017/)
- [AWS — Tipos de app client do Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html)
- [AWS — OAuth 2.0 grants e PKCE no Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/federation-endpoints-oauth-grants.html)
- [AWS — Recuperação e cache de segredos em Lambda](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html)
- [AWS — Práticas recomendadas do Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
