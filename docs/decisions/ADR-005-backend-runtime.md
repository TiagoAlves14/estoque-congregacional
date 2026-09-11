# ADR-005 — Runtime e linguagem do backend

- **Status:** Proposto
- **Data:** 2026-09-11
- **Decisores:** a definir

## Contexto

A primeira geração do diagrama rotulou a aplicação de negócio como “TypeScript” sem que o discovery tivesse definido linguagem. Isso também criou uma falsa comparação: **TypeScript é uma linguagem**, enquanto **Node.js é um runtime** que executa JavaScript. Uma alternativa equivalente deve comparar, por exemplo, “Node.js com TypeScript” e “Python”.

A arquitetura depende dos contratos, regras de domínio, transações, controles de segurança e observabilidade; ela não depende necessariamente de uma das duas linguagens.

## Decisão proposta

Manter o runtime do BFF e da API **a definir** até validação pela equipe. As duas candidatas iniciais são:

| Candidata | Pontos favoráveis | Custos e riscos a avaliar |
| --- | --- | --- |
| Node.js com TypeScript | Tipagem estática, compartilhamento de conhecimento com o frontend e bom ecossistema para OpenAPI e Lambda. | Etapa de compilação, configuração do toolchain e disciplina para não acoplar tipos internos ao contrato. |
| Python | Sintaxe direta, ecossistema maduro para APIs, validação de dados e automação. | Tipagem pode depender de disciplina e ferramentas; compartilhamento de código com o frontend é menor. |

Qualquer escolha deve preservar o mesmo OpenAPI, schemas, cenários de aceitação, formato de logs e fronteiras de segurança. Não é permitido escolher apenas porque a GenAI gerou o primeiro exemplo nessa linguagem.

## Consequências

### Positivas

- Evita transformar uma inferência do modelo em decisão arquitetural.
- Permite que experiência da equipe e prova técnica orientem a escolha.
- Mantém agentes de implementação presos aos contratos, não a uma preferência implícita.

### Negativas e riscos

- A implementação não deve começar antes dessa decisão.
- Infraestrutura, empacotamento, dependências e pipeline ainda não podem ser fechados.

## Critérios para aceite

- Experiência real da equipe em cada alternativa.
- Teste mínimo do fluxo BFF, acesso ao Secrets Manager e transação DynamoDB.
- Tamanho do pacote, tempo de inicialização e suporte das bibliotecas necessárias.
- Estratégia de testes, análise estática, atualização de dependências e observabilidade.
- Registro da alternativa escolhida e dos motivos neste ADR.

## Referências

- [AWS Lambda — Runtimes compatíveis](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html)
- [TypeScript — documentação oficial](https://www.typescriptlang.org/docs/)
- [Node.js — documentação oficial](https://nodejs.org/docs/latest/api/)
- [Python — documentação oficial](https://docs.python.org/3/)
