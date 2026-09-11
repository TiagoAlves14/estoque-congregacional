# ADR-003 — Autenticação com Cognito por meio de BFF

- **Status:** Proposto
- **Data:** 2026-09-11
- **Decisores:** a definir

## Contexto

O sistema exige usuários autorizados e dois papéis iniciais. A revisão de segurança definiu uma restrição mais forte do que a proposta inicial: nem tokens OAuth nem segredos podem ser entregues ao JavaScript executado no navegador.

Uma SPA é um cliente público e não consegue preservar um `client_secret`. O `client_id` identifica o cliente, mas não é segredo. Guardar um `client_secret` no bundle, em variável de ambiente incorporada no build ou buscá-lo do Secrets Manager e devolvê-lo ao navegador apenas deslocaria a exposição; não resolveria o risco.

## Decisão proposta

Usar Amazon Cognito User Pool atrás de um **Backend for Frontend (BFF)**:

- o Cognito Managed Login coleta a senha fora da SPA;
- o BFF atua como cliente OAuth confidencial e usa Authorization Code com PKCE;
- o `client_secret` fica no AWS Secrets Manager e só pode ser lido pelo papel IAM do BFF;
- `state`, `nonce`, `code_verifier` e a transação de login são gerados e validados pelo BFF;
- o Cognito emite os tokens ao BFF, que valida assinatura, emissor, audiência, expiração e `nonce`;
- access e refresh tokens ficam exclusivamente no servidor, associados a uma sessão com expiração e revogação;
- o navegador recebe apenas um identificador opaco e aleatório no cookie `__Host-ec_session`, com `Secure`, `HttpOnly`, `SameSite=Strict`, `Path=/` e sem atributo `Domain`;
- a SPA chama o BFF no mesmo domínio; requisições que alteram estado exigem proteção CSRF adicional, incluindo token vinculado à sessão e validação de origem;
- grupos `ADMIN` e `OPERATOR` permanecem uma baseline de autorização a validar;
- o BFF autoriza cada caso de uso com a identidade resolvida da sessão; o API Gateway apenas roteia a requisição.

O frontend **não gera, assina, armazena nem recebe JWTs**. Também não acessa o Secrets Manager. O BFF pode usar a extensão de cache do Secrets Manager para reduzir chamadas, mas deve respeitar rotação, menor privilégio e falha fechada.

## Alternativas consideradas

1. SPA como cliente público, sem segredo, usando Authorization Code com PKCE: é um fluxo válido, mas deixa tokens acessíveis ao contexto do navegador e não atende à restrição de segurança escolhida.
2. Autenticação própria: rejeitada como baseline pelo risco e custo de manter credenciais.
3. Outro provedor OpenID Connect: tecnicamente válido se já houver uma identidade corporativa disponível.

## Consequências

### Positivas

- Senhas ficam sob serviço gerenciado.
- Tokens e `client_secret` não ficam expostos ao JavaScript do navegador.
- A sessão pode ser revogada no servidor.
- O mesmo domínio reduz a superfície de CORS e permite cookies com atributos restritivos.

### Negativas e riscos

- Dependência de fornecedor.
- O BFF e o store de sessão aumentam a complexidade e o custo em comparação com uma SPA puramente estática.
- Estratégia exata de renovação, expiração e encerramento de sessão precisa ser detalhada.
- Autenticação por cookie exige defesa explícita contra Cross-Site Request Forgery (CSRF).
- Papéis e duração dos tokens ainda necessitam validação.
- Cross-Site Scripting (XSS) ainda pode executar ações em nome do usuário, embora não consiga ler o cookie `HttpOnly`; CSP e prevenção de injeção continuam necessárias.

## Critérios para aceite

- Papéis confirmados pelo responsável funcional.
- Tempos absoluto e ocioso da sessão, renovação e revogação definidos.
- Estratégia CSRF testada.
- Rotação do segredo e permissões IAM revisadas.
- Threat model revisado.
- Experiência de login validada.

## Referências

- [AWS — Tipos de app client do Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html)
- [AWS — OAuth 2.0 grants e PKCE no Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/federation-endpoints-oauth-grants.html)
- [AWS — Recuperação de segredos por funções Lambda](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html)
- [AWS — Práticas recomendadas do Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [IETF RFC 10017 — OAuth 2.0 for Browser-Based Applications](https://datatracker.ietf.org/doc/rfc10017/)
