# Lacunas e perguntas em aberto

| ID | Pergunta | Por que importa | Bloqueia implementação? |
| --- | --- | --- | :---: |
| Q-01 | Os papéis `ADMIN` e `OPERATOR` representam a operação real? | Define autorização e grupos de identidade. | Sim |
| Q-02 | Quais campos de produto são obrigatórios além dos já propostos? | Altera schemas, telas e chaves de busca. | Sim |
| Q-03 | Qual o volume aproximado de produtos e movimentações por mês? | Valida DynamoDB, paginação, custos e estratégia de consulta. | Sim |
| Q-04 | A aplicação precisa operar apenas no Brasil? | Influencia região, latência e requisitos de residência de dados. | Sim |
| Q-05 | Qual é o orçamento mensal esperado? | Valida a baseline de infraestrutura e observabilidade. | Sim |
| Q-06 | Por quanto tempo devem ser mantidos movimentos e registros de auditoria? | Define retenção, exportação e custos. | Sim |
| Q-07 | Por quanto tempo uma chave de idempotência deve permanecer válida? | Define o Time to Live (TTL) do registro. | Sim |
| Q-08 | Quais objetivos de disponibilidade e recuperação são necessários? | Define backup, alarmes e estratégia de desastre. | Sim |
| Q-09 | O nome do produto precisa ser único? Haverá código interno ou código de barras? | Pode exigir item de unicidade e novos padrões de acesso. | Sim |
| Q-10 | É permitido corrigir uma movimentação por estorno lógico? | Define um novo tipo de movimento e regras de auditoria. | Sim |
| Q-11 | O histórico será consultado apenas por produto ou também globalmente por período? | Pode exigir um novo índice secundário global. | Não para o primeiro fluxo |
| Q-12 | Há necessidade de exportar relatórios? | Pode acrescentar geração assíncrona e armazenamento de arquivos. | Não |

Nenhum agente deve resolver essas lacunas silenciosamente. Caso uma escolha seja necessária, deve propor um ADR ou solicitar decisão humana.

