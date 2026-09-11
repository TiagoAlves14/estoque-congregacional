# ADR-003 — Autenticação com Amazon Cognito

- **Status:** Proposto
- **Data:** 2026-09-11
- **Decisores:** a definir

## Contexto

O sistema exige usuários autorizados e dois papéis iniciais. A aplicação web não deve manipular senhas nem expor credenciais para a API.

## Decisão proposta

Usar Amazon Cognito User Pool com:

- Authorization Code com Proof Key for Code Exchange (PKCE);
- grupos `ADMIN` e `OPERATOR` como baseline de autorização;
- tokens de acesso de curta duração;
- validação de emissor, audiência e expiração pelo autorizador JWT do API Gateway;
- nenhuma persistência de tokens em `localStorage`;
- aplicação de negócio autorizando a operação a partir de claims validadas, sem depender de detalhes internos do Cognito.

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

## Critérios para aceite

- Papéis confirmados pelo responsável funcional.
- Política de sessão e recuperação de conta definida.
- Threat model revisado.
- Experiência de login validada.

