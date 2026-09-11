# Arquitetura do Estoque Congregacional

## Propósito

Esta visão descreve a baseline proposta para orientar a implementação futura. Ela separa requisitos confirmados de escolhas arquiteturais ainda pendentes de aceite.

## Drivers arquiteturais

- Operação por uma única igreja e uma equipe pequena.
- Baixo esforço operacional e custo proporcional ao uso.
- Impossibilidade de estoque negativo.
- Rastreabilidade de toda movimentação.
- Proteção contra duplicação causada por reenvio ou timeout.
- Controle de acesso com dois papéis iniciais.
- Evolução simples sem introduzir microsserviços prematuramente.

## Limites e responsabilidades

| Bloco | Responsabilidade | Não é responsabilidade |
| --- | --- | --- |
| Aplicação Web | Interface, validação de conveniência e obtenção da sessão | Aplicar regras finais de estoque |
| API Gateway | Terminação HTTPS, roteamento e validação do JWT | Executar regras de domínio |
| Aplicação de Estoque | Casos de uso, autorização por papel, validações e coordenação das transações | Hospedar interface ou emitir credenciais |
| DynamoDB | Persistir produtos, movimentos e idempotência | Decidir regras de negócio |
| Cognito | Autenticar usuários e emitir tokens | Autorizar operações de domínio isoladamente |
| CloudWatch | Centralizar logs, métricas e alarmes | Armazenar histórico funcional de estoque |

## Estilo arquitetural proposto

O backend será um **monólito modular serverless**: uma unidade implantável em AWS Lambda, separada internamente por módulos de produtos, movimentações, identidade e observabilidade. Essa escolha preserva limites lógicos sem pagar o custo operacional de microsserviços para um domínio pequeno.

O frontend será uma Single-Page Application (SPA). O acesso à API ocorrerá somente por HTTPS e exigirá JSON Web Token (JWT) emitido pelo Amazon Cognito.

## Fluxo de dados

1. O usuário acessa a SPA distribuída pelo CloudFront.
2. A SPA autentica o usuário no Cognito usando Authorization Code com Proof Key for Code Exchange (PKCE).
3. A SPA chama a HTTP API com JWT e identificador de correlação.
4. O API Gateway valida o token e encaminha a chamada à aplicação Lambda.
5. A aplicação valida o papel e executa o caso de uso.
6. Movimentações alteram saldo, criam histórico e registram idempotência em uma transação DynamoDB.
7. Logs e métricas técnicas são enviados ao CloudWatch sem tokens ou dados desnecessários do usuário.

## Autorização proposta

| Operação | ADMIN | OPERATOR |
| --- | :---: | :---: |
| Consultar produtos e histórico | Sim | Sim |
| Registrar entrada ou saída | Sim | Sim |
| Cadastrar produto | Sim | Não |
| Alterar produto ou estoque mínimo | Sim | Não |
| Inativar produto | Sim | Não |

Os papéis são uma inferência do modelo e precisam de validação com os responsáveis da igreja.

## Consistência

- Leituras de catálogo podem ser eventualmente consistentes.
- A leitura anterior à movimentação deve ser fortemente consistente.
- A gravação usa uma transação com condição sobre `version` e saldo.
- O histórico de movimentações é imutável.
- O cliente envia `Idempotency-Key` em toda movimentação.

## Disponibilidade e recuperação

A arquitetura utiliza serviços gerenciados e sem estado, mas objetivos numéricos de disponibilidade e recuperação ainda não foram definidos. Backup contínuo, retenção, região e alarmes estão registrados como perguntas abertas e não devem ser inventados na implementação.

## Visões relacionadas

- [Contexto](diagrams/context.mmd)
- [Containers](diagrams/containers.mmd)
- [Sequência de saída](diagrams/stock-exit-sequence.mmd)
- [Modelo DynamoDB](dynamodb/data-model.md)
- [Contrato OpenAPI](openapi.yaml)
- [Segurança e observabilidade](security/security-and-observability.md)

