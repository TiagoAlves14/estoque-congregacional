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
| I-05 | Usar Cognito com Authorization Code e PKCE por meio de BFF. | Atende à restrição posterior de não expor tokens ao navegador, mas o provedor não foi definido no discovery inicial. | ADR-003 permanece `Proposto`. |
| I-06 | Adotar os papéis `ADMIN` e `OPERATOR`. | Útil para iniciar a matriz de autorização, mas precisa de confirmação. | Marcada como proposta em requisitos e OpenAPI. |
| I-07 | Exigir idempotência em movimentações. | Necessária para proteger contra reenvios e timeouts. | ADR-004 permanece `Proposto`. |
| I-08 | Usar controle otimista por versão e transação atômica. | Resolve saídas concorrentes sem permitir saldo negativo. | Especificada no ADR-004. |
| I-09 | Usar CloudWatch para observabilidade. | Coerente com a baseline AWS. | Incluída no ADR-001, sem inventar limiares de alarmes. |
| I-10 | Usar a região `sa-east-1`. | Pode reduzir latência para usuários no Brasil, mas custo e residência precisam ser avaliados. | Mantida como pergunta aberta. |
| I-11 | Manter sessões opacas no DynamoDB e o `client_secret` no Secrets Manager. | Coerente com um BFF serverless, mas tempos, rotação e KMS precisam de aceite. | Segurança e modelo de sessão documentados como proposta. |
| I-12 | Implementar o backend em TypeScript. | Não havia evidência para escolher linguagem e TypeScript não é alternativa a Node.js. | Escolha retirada dos diagramas e movida para o ADR-005. |

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
| SPA trocar o código OAuth e guardar access token em memória. | BFF confidencial troca o código e mantém os tokens no servidor; a SPA recebe cookie opaco. | Atender à restrição de não disponibilizar JWT ao contexto do navegador. |
| Colocar “aplicação TypeScript” como container. | Rotular o backend por responsabilidade e deixar runtime a definir. | Um container C4 não deve depender de uma escolha tecnológica não confirmada. |
| Usar Secrets Manager como possível fonte para o frontend. | Restringir o Secrets Manager ao BFF com IAM mínimo. | Entregar o valor ao browser anularia a proteção do cofre. |

## Erros identificados na primeira geração

| ID | Erro | Por que estava incorreto | Correção aplicada |
| --- | --- | --- | --- |
| E-01 | A relação entre o responsável e a aplicação foi descrita como `Usa via HTTPS`. | Uma pessoa não interage com o protocolo diretamente. Ela usa a interface; a SPA executada no navegador realiza a comunicação HTTP. | A relação passou a ser `Usa pelo navegador`, e o HTTPS ficou na relação entre a SPA e a API. |
| E-02 | O diagrama deixou ambíguo se a SPA gerava o JWT e mantinha credenciais para isso. | O JWT é emitido e assinado pelo Cognito. Uma SPA não deve gerar tokens nem tentar proteger um `client_secret`. | Cognito ficou explícito como emissor; a correção final usa cliente confidencial no BFF e mantém tokens fora da SPA. |
| E-03 | A visão de containers misturava containers lógicos com API Gateway, Lambda e CloudWatch como detalhes de implantação. | Isso misturava níveis e reduzia a clareza do C4. | A visão de containers foi simplificada, e os serviços físicos passaram para um diagrama de implantação separado. |
| E-04 | A segunda versão ainda colocava o access token no navegador. | O fluxo de cliente público com PKCE é válido, mas não atendia à restrição mais forte definida na revisão: nenhum JWT disponível ao JavaScript. | A autenticação passou para um BFF, com tokens no servidor e cookie opaco `HttpOnly`. |
| E-05 | TypeScript foi apresentado como se fosse a plataforma de execução e como escolha já feita. | TypeScript é linguagem; Node.js é runtime. Python é outra alternativa de linguagem/runtime, e o discovery não escolheu nenhuma. | Os diagramas agora dizem `runtime a definir`, e o ADR-005 compara Node.js com TypeScript e Python. |
| E-06 | A ideia de usar Secrets Manager poderia sugerir que o frontend buscaria o segredo. | Um segredo entregue ao navegador deixa de estar protegido, independentemente de onde foi armazenado antes. | Somente o papel IAM do BFF lê o `client_secret`; a SPA não chama Secrets Manager. |

Esses erros permanecem observáveis no histórico Git: a primeira versão foi preservada no commit anterior e a correção foi feita em mudança posterior.

## O que um agente ainda não pode decidir sozinho

- Mudar um ADR de `Proposto` para `Aceito`.
- Escolher região, orçamento ou objetivos de disponibilidade.
- Escolher Node.js com TypeScript ou Python enquanto o ADR-005 estiver proposto.
- Alterar a matriz de papéis e permissões.
- Definir retenção de histórico, logs, idempotência ou backups.
- Definir duração, renovação, revogação de sessões, rotação de segredo ou chave KMS.
- Adicionar notificações, compras, fornecedores ou multi-tenancy.
- Escolher limites numéricos de paginação, timeout, retentativa e alarme além dos máximos documentados no contrato.

Esses pontos devem ser tratados como perguntas ao responsável, e não completados por inferência.
