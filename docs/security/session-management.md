# Modelo de sessão do BFF

Este documento detalha a sessão proposta no ADR-003. Os tempos numéricos permanecem em aberto.

## Dados mínimos

| Campo lógico | Finalidade | Observação de segurança |
| --- | --- | --- |
| `sessionKeyHash` | Chave primária derivada do identificador opaco | O identificador original existe somente no cookie. |
| `subject` | Valor estável `sub` do usuário | Não usar e-mail para autorização. |
| `roles` | Papéis validados | Revalidar segundo política ainda a definir. |
| `csrfTokenHash` | Verificação do cabeçalho CSRF | Não registrar o token original. |
| `encryptedTokens` | Material OAuth necessário à renovação | Criptografia em repouso e acesso exclusivo do BFF. |
| `createdAt` | Auditoria de criação | ISO 8601 em UTC. |
| `lastSeenAt` | Controle de inatividade, se aprovado | Atualizações devem evitar escrita excessiva. |
| `absoluteExpiresAt` | Expiração aplicada pelo BFF | Sempre validar na leitura. |
| `ttl` | Remoção física posterior pelo DynamoDB | TTL não substitui a validação de expiração. |
| `revokedAt` | Encerramento explícito | Sessão revogada é rejeitada imediatamente. |

Transações de login (`state`, `nonce` e `code_verifier`) usam itens separados, de uso único e curta duração. Devem ser consumidas atomicamente no callback para impedir repetição.

## Ciclo de vida

1. `/auth/login` cria a transação OAuth e redireciona ao Cognito.
2. `/auth/callback` valida a transação, troca o código, valida os tokens e cria uma nova sessão.
3. `/auth/session` retorna apenas identidade mínima e um token CSRF; nunca retorna tokens OAuth.
4. Requisições de domínio validam cookie, expiração, revogação, CSRF quando aplicável e papel.
5. `/auth/logout` revoga a sessão no servidor e expira o cookie.

## Decisões ainda necessárias

- duração absoluta e tempo máximo ocioso;
- frequência de renovação dos tokens e revalidação de papéis;
- chave KMS e estratégia de criptografia de campos;
- limite de sessões simultâneas por usuário;
- comportamento de logout global e recuperação de conta;
- retenção técnica após expiração ou revogação.
