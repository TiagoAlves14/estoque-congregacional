# Contexto para futuros agentes de desenvolvimento

## Ordem obrigatória de leitura

1. [`README.md`](../README.md)
2. [`docs/discovery/requirements.md`](discovery/requirements.md)
3. [`docs/discovery/inferences.md`](discovery/inferences.md)
4. [`docs/discovery/open-questions.md`](discovery/open-questions.md)
5. [`docs/architecture.md`](architecture.md)
6. [`docs/decisions/`](decisions/)
7. [`docs/openapi.yaml`](openapi.yaml)
8. [`docs/dynamodb/`](dynamodb/)
9. [`docs/security/session-management.md`](security/session-management.md)
10. [`docs/tests/acceptance-scenarios.md`](tests/acceptance-scenarios.md)

## Regras que não podem ser violadas

- Não permitir saldo negativo, inclusive sob concorrência.
- Não alterar saldo sem criar uma movimentação imutável na mesma transação.
- Não duplicar efeitos quando uma requisição idempotente for repetida.
- Não entregar ou registrar credenciais, JWT, `client_secret`, cookie de sessão ou dados pessoais desnecessários.
- Não permitir que a SPA acesse o Secrets Manager ou leia a sessão; o cookie deve permanecer `HttpOnly`.
- Não aceitar operação mutável autenticada por cookie sem defesa CSRF.
- Não permitir que `OPERATOR` mantenha o cadastro de produtos.
- Não adicionar multi-tenancy ou integrações fora do escopo.
- Não misturar regras de domínio com detalhes do provedor de identidade.

## Tratamento das decisões

- ADR com status `Proposto` não é decisão definitiva.
- Node.js com TypeScript e Python continuam alternativas; nenhum agente pode escolher o runtime enquanto o ADR-005 estiver `Proposto`.
- Se a implementação depender de uma pergunta aberta, pare e solicite esclarecimento.
- Mudanças de contrato começam no OpenAPI e nos schemas, seguidas dos testes e do código.
- Mudanças estruturais exigem atualização dos diagramas Mermaid.
- Toda nova decisão relevante deve ser registrada em ADR.

## Critérios mínimos para uma implementação aderente

- Operações e respostas compatíveis com o OpenAPI.
- Objetos persistidos compatíveis com os JSON Schemas e o modelo DynamoDB.
- Todos os cenários de aceitação automatizados.
- Autorização testada por papel.
- Fluxo BFF testado sem exposição de tokens ao navegador, com sessão revogável e proteção CSRF.
- Segredo obtido somente no backend com permissão IAM de menor privilégio.
- Escritas de movimentação condicionais, transacionais e idempotentes.
- Logs estruturados com correlação e sem segredos.
- Diagramas e matriz de rastreabilidade atualizados no mesmo pull request.
