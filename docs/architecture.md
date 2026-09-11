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
- Nenhum JWT, `client_secret` ou credencial AWS no frontend.
- Evolução simples sem introduzir microsserviços prematuramente.

## Limites e responsabilidades

| Bloco | Responsabilidade | Não é responsabilidade |
| --- | --- | --- |
| Aplicação Web | Interface e validação de conveniência; envia automaticamente o cookie pelo navegador | Ler tokens, segredos ou aplicar regras finais de estoque |
| CloudFront e API Gateway | HTTPS, domínio único e roteamento de `/auth` e `/api` | Validar JWT ou executar regras de domínio |
| BFF e Aplicação de Estoque | Fluxo OAuth, sessão, autorização por papel, casos de uso e coordenação das transações | Expor tokens ao navegador ou coletar senha |
| Store de Sessões | Persistir sessão opaca, tokens protegidos, expiração e revogação | Armazenar dados funcionais de estoque |
| Banco de Estoque | Persistir produtos, movimentos e idempotência | Decidir regras de negócio |
| Cognito | Autenticar usuários e emitir tokens para o BFF | Autorizar operações de domínio isoladamente |
| Secrets Manager | Proteger o `client_secret` e entregá-lo ao papel IAM do BFF | Entregar segredos ao frontend |
| CloudWatch | Centralizar logs, métricas e alarmes | Armazenar histórico funcional de estoque |

## Estilo arquitetural proposto

O backend será um **monólito modular serverless**: uma unidade implantável em AWS Lambda, separada internamente por módulos de sessão, produtos, movimentações e observabilidade. Ela atua simultaneamente como BFF e API de domínio. Essa escolha evita um salto interno desnecessário entre dois backends para um domínio pequeno, mas preserva limites modulares.

O frontend será uma Single-Page Application (SPA), mas não será cliente direto da API OAuth. O navegador acessa SPA e BFF pelo mesmo domínio e recebe apenas um cookie de sessão opaco. O runtime da Lambda ainda não foi escolhido: Node.js com TypeScript e Python são alternativas registradas no ADR-005.

## Fluxo de dados

1. O usuário acessa pelo navegador a SPA distribuída pelo CloudFront.
2. Ao iniciar login, o navegador chama o BFF; o BFF obtém seu `client_secret` no Secrets Manager, cria `state`, `nonce` e PKCE e redireciona ao Managed Login do Cognito.
3. O usuário informa a senha somente ao Cognito. O código de autorização retorna ao callback do BFF por meio do navegador.
4. O BFF valida a transação, troca o código e recebe os JWTs do Cognito sem devolvê-los à SPA.
5. O BFF cria uma sessão no servidor e envia somente o cookie opaco `__Host-ec_session`, protegido por `Secure`, `HttpOnly` e `SameSite=Strict`.
6. A SPA chama `/api` no mesmo domínio. O navegador envia o cookie automaticamente; operações mutáveis também enviam `X-CSRF-Token`.
7. O BFF valida sessão, CSRF e papel e executa o caso de uso.
8. Movimentações alteram saldo, criam histórico e registram idempotência em uma transação DynamoDB.
9. Logs e métricas técnicas são enviados ao CloudWatch sem tokens, cookies ou dados desnecessários do usuário.

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

## Segurança da sessão

- O `client_id` é um identificador público; o `client_secret` é segredo e existe somente no Secrets Manager e na memória do BFF durante o uso.
- O frontend não acessa o Secrets Manager e não recebe tokens OAuth.
- O BFF armazena tokens e metadados de sessão no servidor, com expiração aplicada pela aplicação, revogação e TTL para remoção posterior.
- Cookies autenticados exigem defesa contra CSRF; `SameSite` é combinado com token CSRF e validação de origem.
- O API Gateway não usa autorizador JWT nesta baseline, porque a credencial apresentada pelo navegador é um cookie de sessão opaco.

## Disponibilidade e recuperação

A arquitetura utiliza serviços gerenciados e sem estado, mas objetivos numéricos de disponibilidade e recuperação ainda não foram definidos. Backup contínuo, retenção, região e alarmes estão registrados como perguntas abertas e não devem ser inventados na implementação.

## Visões relacionadas

- [Contexto](diagrams/context.mmd)
- [Containers](diagrams/containers.mmd)
- [Implantação AWS](diagrams/deployment.mmd)
- [Sequência de autenticação](diagrams/authentication-sequence.mmd)
- [Sequência de saída](diagrams/stock-exit-sequence.mmd)
- [Modelo DynamoDB](dynamodb/data-model.md)
- [Contrato OpenAPI](openapi.yaml)
- [Segurança e observabilidade](security/security-and-observability.md)
- [Modelo de sessão](security/session-management.md)
