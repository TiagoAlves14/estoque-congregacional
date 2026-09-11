# ADR-001 — Arquitetura serverless na AWS

- **Status:** Proposto
- **Data:** 2026-09-11
- **Decisores:** a definir

## Contexto

O sistema atenderá inicialmente uma única igreja, com equipe pequena e volume ainda desconhecido. A solução deve ter baixo esforço operacional, custo proporcional ao uso e limites claros entre interface, entrada HTTP, negócio e persistência.

## Decisão proposta

Adotar:

- React SPA hospedada em Amazon S3 e distribuída pelo Amazon CloudFront;
- uma distribuição CloudFront com o mesmo domínio para arquivos estáticos, `/auth` e `/api`;
- Amazon API Gateway HTTP API como entrada e roteador, sem expor JWT ao navegador;
- um Backend for Frontend (BFF) e a aplicação de estoque na mesma unidade AWS Lambda, organizada como monólito modular;
- runtime do backend pendente entre Node.js com TypeScript e Python, conforme o ADR-005;
- Amazon DynamoDB para dados de estoque e um store isolado de sessões com Time to Live (TTL);
- AWS Secrets Manager para o `client_secret` do cliente confidencial do Cognito;
- Amazon CloudWatch para logs, métricas e alarmes;
- infraestrutura declarada futuramente como código.

A região AWS permanece em aberto. `sa-east-1` é apenas uma hipótese a avaliar.

## Alternativas consideradas

1. Aplicação monolítica em máquina virtual: simples conceitualmente, mas transfere manutenção de sistema operacional, escala e disponibilidade para a equipe.
2. Contêiner em serviço gerenciado: oferece portabilidade, porém acrescenta decisões operacionais sem necessidade comprovada.
3. Microsserviços serverless: permite evolução independente, mas cria complexidade de consistência, observabilidade e implantação desnecessária para o escopo atual.

## Consequências

### Positivas

- Menor carga operacional.
- Escala sob demanda.
- Cobrança proporcional ao uso em cargas pequenas.
- Uma unidade de backend simples de implantar e testar.
- Tokens OAuth permanecem no servidor, com uma fronteira de confiança clara para o navegador.

### Negativas e riscos

- Acoplamento a serviços AWS.
- Latência de inicialização da Lambda em alguns cenários.
- Custos podem crescer de forma não linear sem orçamento e métricas.
- O BFF passa a manter estado de sessão e exige proteção contra CSRF, rotação e revogação.
- Região, recuperação, limites de serviço e observabilidade ainda precisam ser definidos.

## Critérios para aceite

- Volume e orçamento estimados.
- Região escolhida.
- Objetivos de disponibilidade e recuperação definidos.
- Comparação de custo com pelo menos uma alternativa.
- Runtime do backend e política de sessão aprovados.
