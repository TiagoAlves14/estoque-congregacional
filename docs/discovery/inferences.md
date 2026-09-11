# Registro de inferências e ajustes da GenAI

## Como ler este documento

Este registro distingue o que foi informado no discovery do que foi sugerido pelo modelo. Uma inferência somente se torna decisão quando é revisada e seu Architecture Decision Record (ADR) muda de `Proposto` para `Aceito`.

## Fatos fornecidos ou confirmados no discovery

| ID | Fato | Evidência no repositório |
| --- | --- | --- |
| F-01 | O sistema controla materiais de uma igreja. | README e descrição do sistema. |
| F-02 | A primeira versão atende uma única igreja. | Escopo do README. |
| F-03 | Existem cadastro, entrada, saída, saldo, histórico e estoque mínimo. | RF-02 a RF-09. |
| F-04 | Apenas usuários autorizados operam o sistema. | RF-01. |
| F-05 | O saldo não pode ficar negativo. | RN-02. |
| F-06 | Toda entrada ou saída deve ser rastreável. | RN-04 e RN-05. |
| F-07 | O objetivo atual é uma arquitetura completa, não a implementação da aplicação. | Objetivo do README. |

## Inferências produzidas pelo modelo

| ID | Inferência | Avaliação após revisão | Tratamento |
| --- | --- | --- | --- |
| I-01 | Separar interface, API, regras de negócio e persistência. | Coerente com as responsabilidades descritas. | Mantida nos diagramas. |
| I-02 | Usar uma única aplicação de backend em vez de microsserviços. | Adequado ao domínio pequeno e reduz complexidade. | Registrada no ADR-001. |
| I-03 | Hospedar a solução em arquitetura serverless na AWS. | Plausível, mas não foi requisito fornecido. | ADR-001 permanece `Proposto`. |
| I-04 | Usar DynamoDB com single-table design. | Compatível com os padrões de acesso, mas exige validação do time. | ADR-002 permanece `Proposto`. |
| I-05 | Usar Cognito com Authorization Code e PKCE. | Coerente com uma SPA, mas o provedor não foi definido pelo discovery. | ADR-003 permanece `Proposto`. |
| I-06 | Adotar os papéis `ADMIN` e `OPERATOR`. | Útil para iniciar a matriz de autorização, mas precisa de confirmação. | Marcada como proposta em requisitos e OpenAPI. |
| I-07 | Exigir idempotência em movimentações. | Necessária para proteger contra reenvios e timeouts. | ADR-004 permanece `Proposto`. |
| I-08 | Usar controle otimista por versão e transação atômica. | Resolve saídas concorrentes sem permitir saldo negativo. | Especificada no ADR-004. |
| I-09 | Usar CloudWatch para observabilidade. | Coerente com a baseline AWS. | Incluída no ADR-001, sem inventar limiares de alarmes. |
| I-10 | Usar a região `sa-east-1`. | Pode reduzir latência para usuários no Brasil, mas custo e residência precisam ser avaliados. | Mantida como pergunta aberta. |

## Ajustes feitos durante a revisão

| Proposta inicial do modelo | Ajuste aplicado | Motivo |
| --- | --- | --- |
| Separar produtos, estoque e notificações em serviços distintos. | Manter uma única aplicação Lambda modular. | Evitar complexidade distribuída sem escala ou times independentes que a justifiquem. |
| Enviar alerta externo quando o estoque atingir o mínimo. | Exibir apenas indicação visual na aplicação. | E-mail, SMS e mensageria estão fora do escopo. |
| Escolher tecnologias diretamente no diagrama. | Registrar cada escolha relevante como ADR `Proposto`. | Distinguir inferência de decisão aceita. |
| Atualizar o saldo e depois criar o histórico. | Executar saldo, movimento e idempotência em uma transação. | Evitar atualização parcial e perda de rastreabilidade. |
| Aceitar nova tentativa como uma nova operação. | Exigir `Idempotency-Key` e hash do conteúdo. | Impedir efeitos duplicados sem mascarar requisições diferentes. |
| Detalhar funções e classes no desenho estrutural. | Manter somente containers. | Não misturar níveis do modelo C4. |
| Considerar múltiplas igrejas como evolução automática. | Manter single-tenant nesta fase. | Multi-tenancy foi declarado fora do escopo. |

## O que um agente ainda não pode decidir sozinho

- Mudar um ADR de `Proposto` para `Aceito`.
- Escolher região, orçamento ou objetivos de disponibilidade.
- Alterar a matriz de papéis e permissões.
- Definir retenção de histórico, logs, idempotência ou backups.
- Adicionar notificações, compras, fornecedores ou multi-tenancy.
- Escolher limites numéricos de paginação, timeout, retentativa e alarme além dos máximos documentados no contrato.

Esses pontos devem ser tratados como perguntas ao responsável, e não completados por inferência.

