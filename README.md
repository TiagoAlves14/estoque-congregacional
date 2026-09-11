# Estoque Congregacional

> Base de documentação arquitetural de um sistema web para controle de estoque de uma igreja, produzida com a abordagem *diagrams as code*.

## Objetivo

Este repositório concentra o discovery e a especificação arquitetural do **Estoque Congregacional**. Os artefatos foram organizados para serem versionáveis, revisáveis e utilizáveis como contexto por futuros agentes de desenvolvimento.

O repositório documenta a arquitetura; ele **não contém uma aplicação implementada**. As tecnologias da baseline são propostas registradas em ADRs e precisam de aceite humano antes do início do desenvolvimento.

## Visão do sistema

O Estoque Congregacional apoiará uma única igreja no controle de produtos de limpeza, materiais de escritório, itens descartáveis e materiais usados em eventos. Usuários autorizados poderão cadastrar produtos, registrar entradas e saídas, consultar saldos, visualizar o histórico e identificar itens abaixo do estoque mínimo.

### Escopo

- Cadastro e consulta de produtos.
- Registro de entradas e saídas.
- Consulta do saldo atual.
- Histórico de movimentações por produto.
- Indicação visual de estoque mínimo.
- Autenticação e autorização de usuários.
- Auditoria mínima das operações.

### Fora do escopo

- Compras, pagamentos e emissão de notas fiscais.
- Integração com fornecedores ou ERP.
- Controle de validade, lote ou localização física.
- Funcionamento offline.
- Múltiplas igrejas na mesma instalação.
- Alertas por e-mail, SMS ou aplicativos de mensagens.

### Regras invariantes

1. O saldo de um produto nunca pode ficar negativo.
2. Toda entrada ou saída deve gerar uma movimentação imutável e rastreável.
3. Alteração de saldo, criação da movimentação e registro de idempotência devem ser atômicos.
4. Uma repetição com a mesma chave de idempotência e o mesmo conteúdo não pode duplicar o efeito.
5. Uma mesma chave de idempotência com conteúdo diferente deve ser rejeitada.

## Baseline arquitetural proposta

| Responsabilidade | Solução proposta | Situação |
| --- | --- | --- |
| Interface web | SPA React em Amazon S3 e CloudFront | Proposta no ADR-001 |
| Identidade | Amazon Cognito com Authorization Code e PKCE | Proposta no ADR-003 |
| Entrada HTTP | Amazon API Gateway HTTP API com autorizador JWT | Proposta no ADR-001 |
| Regras de negócio | Aplicação TypeScript em AWS Lambda, organizada como monólito modular | Proposta no ADR-001 |
| Persistência | Amazon DynamoDB com single-table design | Proposta no ADR-002 |
| Consistência de movimentações | Transação, condição de saldo e chave de idempotência | Proposta no ADR-004 |
| Observabilidade | Logs, métricas e alarmes no Amazon CloudWatch | Proposta no ADR-001 |

## Diagrama estrutural — visão de containers

O desenho mantém o nível de containers inspirado no C4. Serviços gerenciados externos ao limite lógico da aplicação são identificados como externos.

```mermaid
flowchart TB
    usuario["Responsável pelo estoque"]
    cognito["Amazon Cognito — externo"]

    subgraph sistema["Estoque Congregacional"]
        web["Aplicação Web — React SPA"]
        gateway["API HTTP — API Gateway"]
        backend["Aplicação de Estoque — AWS Lambda"]
        banco[("Tabela de Estoque — DynamoDB")]
        observabilidade["Observabilidade — CloudWatch"]
    end

    usuario -->|Usa via HTTPS| web
    web -->|Autentica com PKCE| cognito
    web -->|Envia JWT e JSON via HTTPS| gateway
    gateway -.->|Valida JWT| cognito
    gateway -->|Encaminha requisição autorizada| backend
    backend -->|Lê e grava dados| banco
    gateway -->|Publica métricas e logs| observabilidade
    backend -->|Publica métricas e logs| observabilidade
```

Fonte versionada: [`docs/diagrams/containers.mmd`](docs/diagrams/containers.mmd).

## Diagrama comportamental — registro de saída

A jornada crítica considera o usuário autenticado e apresenta repetição idempotente, sucesso, saldo insuficiente e conflito concorrente.

```mermaid
sequenceDiagram
    autonumber
    actor Usuario as Responsável pelo estoque
    participant Web as Aplicação Web
    participant API as API Gateway
    participant App as Aplicação de Estoque
    participant DB as DynamoDB

    Usuario->>Web: Informa produto, quantidade e motivo
    Web->>API: POST movimentação com JWT e Idempotency-Key
    API->>API: Valida JWT e autorização
    API->>App: Encaminha requisição autorizada
    App->>DB: Consulta chave de idempotência

    alt Requisição já processada com o mesmo conteúdo
        DB-->>App: Retorna resultado armazenado
        App-->>Web: Repete a resposta sem nova baixa
    else Nova requisição
        App->>DB: Lê produto com consistência forte
        DB-->>App: Retorna saldo e versão
        App->>DB: Transação: atualiza saldo, cria movimento e idempotência
        alt Saldo suficiente e versão atual
            DB-->>App: Confirma transação
            App-->>Web: 201 — saída registrada
            Web-->>Usuario: Exibe novo saldo
        else Saldo insuficiente
            DB-->>App: Cancela transação
            App-->>Web: 409 — saldo insuficiente
            Web-->>Usuario: Exibe erro sem alterar o estoque
        else Versão alterada por operação concorrente
            DB-->>App: Cancela transação
            App-->>Web: 409 — conflito de concorrência
            Web-->>Usuario: Solicita nova tentativa
        end
    end
```

Fonte versionada: [`docs/diagrams/stock-exit-sequence.mmd`](docs/diagrams/stock-exit-sequence.mmd).

## Evidência do uso de GenAI

A distinção entre fatos, inferências, decisões propostas, ajustes e lacunas está registrada em [`docs/discovery/inferences.md`](docs/discovery/inferences.md). Esse registro evita apresentar escolhas produzidas pelo modelo como se fossem requisitos fornecidos.

Em resumo:

- O modelo inferiu corretamente a separação entre interface, regras e persistência, a necessidade de autenticação e o risco de saldo insuficiente.
- A revisão limitou a solução a uma única API modular, retirou notificações externas e tornou explícita a atomicidade da movimentação.
- AWS, React, Cognito, Lambda, DynamoDB e idempotência foram convertidos em decisões propostas e documentados em ADRs, em vez de serem tratados como fatos.
- Ainda faltam validação de volume, objetivos de disponibilidade, orçamento, retenção e aceite formal dos ADRs.

## Organização do repositório

```text
.
├── .github/workflows/              # Validação automatizada dos artefatos
├── docs/
│   ├── decisions/                  # Architecture Decision Records (ADRs)
│   ├── diagrams/                   # Fontes Mermaid
│   ├── discovery/                  # Requisitos, lacunas e inferências
│   ├── dynamodb/                   # Modelo, acessos e transações
│   ├── mapping/                    # Rastreabilidade entre artefatos
│   ├── schemas/                    # Contratos JSON Schema
│   ├── security/                   # Segurança e observabilidade
│   ├── tests/                      # Cenários de aceitação arquitetural
│   ├── agent-context.md            # Regras para futuros agentes
│   ├── architecture.md             # Visão arquitetural consolidada
│   └── openapi.yaml                # Contrato HTTP OpenAPI 3.1
├── scripts/validate_architecture.py
└── README.md
```

## Índice dos artefatos

- [Descrição e arquitetura consolidada](docs/architecture.md)
- [Requisitos e regras de negócio](docs/discovery/requirements.md)
- [Inferências e ajustes da GenAI](docs/discovery/inferences.md)
- [Registro dos prompts](docs/discovery/prompt-log.md)
- [Lacunas e perguntas em aberto](docs/discovery/open-questions.md)
- [Contexto para agentes](docs/agent-context.md)
- [Contrato OpenAPI](docs/openapi.yaml)
- [Modelo DynamoDB](docs/dynamodb/data-model.md)
- [Padrões de acesso](docs/dynamodb/access-patterns.md)
- [Transação e idempotência](docs/dynamodb/transaction-spec.md)
- [Segurança e observabilidade](docs/security/security-and-observability.md)
- [Cenários de aceitação](docs/tests/acceptance-scenarios.md)
- [Matriz de rastreabilidade](docs/mapping/traceability.md)
- [ADRs propostos](docs/decisions/)

## Validação local

Com Python 3 e PyYAML instalados:

```bash
python -m pip install pyyaml
python scripts/validate_architecture.py
```

O mesmo validador é executado pelo GitHub Actions para conferir JSON, YAML, referências locais, links Markdown e sincronismo entre os diagramas exibidos neste README e seus arquivos `.mmd`.

## Status

**Arquitetura proposta — aguardando revisão e aceite humano antes da implementação.**
