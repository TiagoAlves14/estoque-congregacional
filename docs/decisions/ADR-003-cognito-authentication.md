# ADR-003 — Autenticação com Amazon Cognito

- **Status:** Proposto
- **Data:** 2026-09-11
- **Decisores:** a definir

## Contexto

O sistema exige usuários autorizados e dois papéis iniciais. A aplicação web não deve manipular senhas nem expor credenciais para a API.

## Decisão proposta

Usar Amazon Cognito User Pool com:

- Cognito Managed Login para coletar a credencial do usuário fora da SPA;
- app client do tipo público e sem `client_secret` (`GenerateSecret=false`);
- Authorization Code com Proof Key for Code Exchange (PKCE);
- grupos `ADMIN` e `OPERATOR` como baseline de autorização;
- tokens de acesso de curta duração;
- validação de emissor, audiência e expiração pelo autorizador JWT do API Gateway;
- nenhuma persistência de tokens em `localStorage`;
- aplicação de negócio autorizando a operação a partir de claims validadas, sem depender de detalhes internos do Cognito.

O frontend **não gera nem assina JWTs**. A SPA gera somente um `code_verifier` aleatório e seu `code_challenge` para a transação PKCE. Após o login, o Cognito devolve um código de autorização; a SPA apresenta o código e o verificador ao token endpoint, e o Cognito emite os tokens.

O `client_id`, a URL do User Pool, os escopos e as URLs de callback são configurações públicas. Nenhuma chave de acesso AWS ou segredo do app client pode fazer parte do bundle JavaScript.

Como a SPA precisa apresentar o access token à API, código JavaScript malicioso no mesmo contexto poderia roubá-lo. A baseline reduz esse risco com armazenamento somente em memória, Content Security Policy e vida curta do token. Se o negócio exigir sessão persistente ou proteção mais forte contra exposição do token no navegador, deve ser avaliado um Backend for Frontend (BFF), com tokens no servidor e cookie `HttpOnly`, `Secure` e `SameSite`.

## Alternativas consideradas

1. Autenticação própria: rejeitada como baseline pelo risco e custo de manter credenciais.
2. Outro provedor OpenID Connect: tecnicamente válido e preservado como alternativa se houver identidade já disponível.
3. Backend for Frontend com cookies HttpOnly: oferece melhor controle de sessão, mas adiciona um container e fluxo ainda não justificados para este escopo.

## Consequências

### Positivas

- Credenciais ficam sob serviço gerenciado.
- Integração direta com API Gateway.
- Fluxo adequado para cliente público usando PKCE.

### Negativas e riscos

- Dependência de fornecedor.
- Estratégia exata de renovação e encerramento de sessão precisa ser detalhada.
- Papéis e duração dos tokens ainda necessitam validação.
- Uma SPA continua exposta a roubo de token em caso de Cross-Site Scripting (XSS); PKCE não elimina esse risco.

## Critérios para aceite

- Papéis confirmados pelo responsável funcional.
- Política de sessão e recuperação de conta definida.
- Threat model revisado.
- Experiência de login validada.

## Referências

- [AWS — Tipos de app client do Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html)
- [AWS — OAuth 2.0 grants e PKCE no Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/federation-endpoints-oauth-grants.html)
- [AWS — Autorizador JWT do API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html)
