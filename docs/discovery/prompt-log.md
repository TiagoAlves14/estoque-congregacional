# Registro dos prompts de discovery

Este arquivo registra os prompts consolidados usados para transformar a descrição inicial em artefatos revisáveis. A conversa ocorreu de forma iterativa; os textos abaixo preservam a intenção das etapas executadas.

## 1. Identificação de lacunas

```text
Atue como arquiteto de software sênior. Antes de gerar diagramas, analise a descrição
de um sistema web para controle de estoque de materiais de uma única igreja.

O sistema permite cadastrar produtos, registrar entradas e saídas, consultar saldo,
histórico e estoque mínimo. Somente usuários autorizados podem operar e o saldo não
pode ficar negativo.

Identifique escopo, limites, responsabilidades, integrações, restrições, lacunas e
suposições. Não escolha tecnologia sem marcar a escolha como inferência.
```

## 2. Diagrama estrutural

```text
Gere em Mermaid uma visão estrutural de containers inspirada no C4.
Mantenha apenas um nível, identifique integrações externas e não inclua classes,
endpoints ou componentes internos. Declare antes todas as suposições tecnológicas.
```

## 3. Diagrama comportamental

```text
Gere em Mermaid um diagrama de sequência para o registro de saída de estoque.
Inclua sucesso, saldo insuficiente, repetição idempotente e conflito concorrente.
Mostre onde a atomicidade é necessária e não invente tempos de resposta ou SLAs.
```

## 4. Revisão arquitetural

```text
Revise os artefatos gerados. Separe fatos fornecidos, inferências corretas, decisões
propostas, ajustes humanos e lacunas. Remova microsserviços e integrações sem
justificativa. Transforme escolhas relevantes em ADRs com status Proposto e indique
o que um agente de desenvolvimento ainda precisaria perguntar antes de implementar.
```

## Resultado da revisão

- A estrutura interface/API/persistência foi mantida.
- Microsserviços e notificações externas foram removidos.
- Atomicidade, concorrência e idempotência foram explicitadas.
- A baseline AWS foi registrada como proposta, não como fato.
- Perguntas sem resposta permaneceram visíveis em [`open-questions.md`](open-questions.md).

