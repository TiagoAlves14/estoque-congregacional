# Requisitos e regras de negócio

## Atores

| Ator | Objetivo |
| --- | --- |
| Administrador (`ADMIN`) | Manter o catálogo e também operar o estoque. |
| Operador (`OPERATOR`) | Consultar produtos e registrar movimentações. |

Os nomes e as permissões dos papéis são uma proposta a validar, não um requisito originalmente fornecido.

## Requisitos funcionais

| ID | Requisito | Prioridade |
| --- | --- | --- |
| RF-01 | Autenticar o usuário antes de permitir acesso às funções protegidas. | Obrigatório |
| RF-02 | Cadastrar produto com nome, categoria, unidade e estoque mínimo. | Obrigatório |
| RF-03 | Consultar e paginar produtos cadastrados. | Obrigatório |
| RF-04 | Consultar os dados e o saldo atual de um produto. | Obrigatório |
| RF-05 | Alterar dados cadastrais e inativar um produto. | Obrigatório |
| RF-06 | Registrar entrada de quantidade positiva em produto ativo. | Obrigatório |
| RF-07 | Registrar saída de quantidade positiva quando houver saldo. | Obrigatório |
| RF-08 | Consultar o histórico de movimentações de um produto. | Obrigatório |
| RF-09 | Identificar na listagem os produtos cujo saldo seja menor ou igual ao estoque mínimo. | Obrigatório |
| RF-10 | Repetir com segurança a resposta de uma movimentação já processada. | Obrigatório |

## Regras de negócio

| ID | Regra |
| --- | --- |
| RN-01 | Quantidades de entrada e saída devem ser números inteiros maiores que zero. |
| RN-02 | O saldo nunca pode ficar negativo. |
| RN-03 | O saldo inicial de um produto é zero; qualquer acréscimo deve ocorrer por uma entrada auditável. |
| RN-04 | Toda movimentação registra produto, tipo, quantidade, saldo resultante, motivo, autor e data. |
| RN-05 | Movimentações concluídas são imutáveis. Uma correção deve ser realizada por nova movimentação. |
| RN-06 | Produtos inativos podem ser consultados, mas não recebem novas movimentações. |
| RN-07 | Alteração do saldo e inclusão da movimentação ocorrem atomicamente. |
| RN-08 | A chave de idempotência é obrigatória para registrar movimentações. |
| RN-09 | Mesma chave e mesmo conteúdo retornam o resultado anterior sem repetir o efeito. |
| RN-10 | Mesma chave com conteúdo diferente gera conflito e não altera dados. |
| RN-11 | Estoque baixo é calculado quando `currentStock <= minimumStock`. |

## Requisitos não funcionais candidatos

Estes itens orientam a arquitetura, mas seus valores precisam de validação:

| ID | Categoria | Proposta |
| --- | --- | --- |
| RNF-01 | Segurança | Todo tráfego externo deve usar HTTPS e toda rota, exceto verificação técnica de saúde, deve exigir JWT válido. |
| RNF-02 | Auditoria | Logs técnicos não substituem o histórico funcional das movimentações. |
| RNF-03 | Privacidade | Não registrar JWT, senha, e-mail ou dados pessoais desnecessários em logs. |
| RNF-04 | Consistência | Uma saída concorrente não pode violar a regra de saldo não negativo. |
| RNF-05 | Portabilidade | Contratos HTTP e schemas devem permanecer independentes da implementação interna da Lambda. |
| RNF-06 | Operabilidade | Cada chamada deve possuir identificador de correlação e métricas de sucesso, erro e duração. |

Disponibilidade, latência, throughput, retenção e objetivos de recuperação não possuem valores definidos. Consulte [perguntas em aberto](open-questions.md).

## Critérios mínimos para início da implementação

- ADRs prioritários revisados e aceitos.
- Papéis e permissões confirmados.
- Campos de produto e movimentação confirmados.
- Política de retenção e backup definida.
- Volume esperado e orçamento aproximado informados.
- Contrato OpenAPI revisado pelo responsável funcional.

