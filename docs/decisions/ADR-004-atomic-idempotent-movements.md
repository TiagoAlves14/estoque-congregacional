# ADR-004 — Movimentações atômicas e idempotentes

- **Status:** Proposto
- **Data:** 2026-09-11
- **Decisores:** a definir

## Contexto

Reenvios por timeout e saídas concorrentes podem duplicar movimentações ou tornar o saldo negativo. Atualizar saldo e criar histórico em operações separadas também pode produzir estado parcial.

## Decisão proposta

Toda requisição de entrada ou saída deverá:

1. receber `Idempotency-Key` e calcular um hash canônico do conteúdo relevante;
2. retornar a resposta anterior quando a chave já existir com o mesmo hash;
3. rejeitar com conflito quando a chave existir com outro hash;
4. ler o produto com consistência forte e obter sua versão;
5. executar `TransactWriteItems` contendo atualização condicional do produto, criação da movimentação e criação do registro de idempotência;
6. condicionar a saída a saldo suficiente, produto ativo e versão ainda atual.

Não haverá retentativa cega após conflito de versão. O cliente receberá conflito e deverá recarregar o saldo antes de tentar novamente com uma nova chave.

## Alternativas consideradas

1. Aceitar duplicação e fazer reconciliação posterior: incompatível com o controle de estoque.
2. Usar somente chave de idempotência em memória: não funciona entre instâncias ou após reinício.
3. Atualizar saldo e histórico separadamente: cria risco de estado parcial.
4. Usar fila para toda movimentação: acrescenta consistência eventual e não é necessária para a primeira versão.

## Consequências

### Positivas

- Impede efeito duplicado em reenvios.
- Protege o saldo sob concorrência.
- Garante consistência entre saldo e histórico.

### Negativas e riscos

- Exige armazenamento e expiração de chaves.
- Conflitos concorrentes precisam de tratamento explícito na interface.
- Transações DynamoDB têm custo e limites próprios.

## Critérios para aceite

- Tempo de retenção da chave definido.
- Formato do hash e campos relevantes aprovados.
- Cenários concorrentes automatizados.
- Códigos de erro validados no contrato OpenAPI.

