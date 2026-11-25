# Mapa de Apoios PE

Mapa interativo de Pernambuco com os 184 prefeitos (2025–2028), os 25 deputados federais eleitos em 2026, a votação de cada candidato por cidade, os apoios das prefeituras, as oportunidades de apoio e as emendas parlamentares pagas por município.

Abra o `index.html` no navegador. É uma página única, sem servidor nem instalação.

## O que tem no site

- **Partido do prefeito**: o mapa colorido pelo partido de cada prefeito.
- **Mais votados 2026**: o candidato a deputado federal mais votado em cada cidade, região imediata ou mesorregião.
- **Apoios registrados**: o deputado que cada prefeitura apoia.
- **Oportunidades**: cidades onde o mais votado não se elegeu.
- **Emendas**: valores pagos por cidade, autor e ano.
- **Votos por candidato**: digite um nome e veja onde ele foi votado e quantos votos teve em cada cidade.
- **Relatório**: tabela das 185 cidades, que pode ser baixada em CSV (há uma cópia em `relatorio_prefeitos_pe.csv`).

## Sobre os apoios e o Instagram

A versão principal do site fica no claude.ai, onde a equipe registra apoios e perfis de Instagram num banco compartilhado. O `index.html` deste repositório traz uma **cópia somente leitura** desses dados, feita em 25/11/2026. Para registrar novos apoios, use a versão do claude.ai.

## Fontes

- Prefeitos 2024 e votação de deputado federal 2026: TSE (dados abertos)
- Malha municipal e coordenadas das sedes: IBGE
- Emendas parlamentares (valores pagos): Portal da Transparência / CGU, atualizado em 24/11/2026
- Instagram dos prefeitos: Uchoa Mídia (seção Mapa político) e cadastros da equipe
- Levantamento de apoios de abr/2025: PE Notícias (preliminar)

## Como regenerar o site

Os dados processados estão em `fonte/dados/`. Para gerar a página de novo:

```bash
cd fonte
SNAPSHOT=dados/snapshot.json python3 build.py dados template.html ../index.html ../relatorio_prefeitos_pe.csv
```

- `template.html`: código do site (HTML, CSS e JavaScript)
- `build.py`: junta os dados ao template e gera o CSV
- `em_build.py`: processa o arquivo de emendas do Portal da Transparência
- `vc_build.py`: processa a votação por cidade do TSE
- `site/mapa-apoios-pe.html`: versão publicada no claude.ai, sem a cópia dos apoios
