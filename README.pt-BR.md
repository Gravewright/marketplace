# Gravewright Marketplace

[English](README.md)

Catálogo oficial de módulos e receitas do [Gravewright](https://github.com/Gravewright).

O Gravewright consulta o arquivo [`gravewright.marketplace.json`](./gravewright.marketplace.json) deste repositório para descobrir módulos e receitas disponíveis.

## Publicar um projeto

Para divulgar um módulo ou uma receita no marketplace:

1. Publique seu projeto em um repositório público.
2. Crie uma release versionada.
3. Disponibilize um manifest HTTPS apontando para o ZIP da release.
4. Calcule e informe o SHA-256 do ZIP.
5. [Abra uma issue](https://github.com/Gravewright/marketplace/issues/new) solicitando a inclusão.

Inclua na issue:

- Nome do projeto
- Descrição curta
- Tipo: módulo ou receita
- Kind do módulo, quando aplicável
- URL do repositório
- URL do manifest ou da receita
- Versão atual
- Licença
- Nome do responsável

A inclusão não é automática. O projeto será revisado antes de entrar no catálogo.

## Requisitos para módulos

O manifest deve estar disponível por HTTPS e apontar para um ZIP imutável de uma release:

```json
{
  "name": "fog-of-war",
  "kind": "addon",
  "provider": "community",
  "version": "1.2.0",
  "entry": "./index.js",
  "exports": {
    "get": []
  },
  "download_url": "https://github.com/example/fog-of-war/releases/download/v1.2.0/fog-of-war.zip",
  "download_sha256": "sha256-do-arquivo-zip"
}
```

A URL cadastrada no marketplace deve apontar para um manifest estável, como:

```text
https://example.org/fog-of-war/latest.json
```

Esse manifest pode ser atualizado quando uma nova release for publicada. O ZIP indicado por ele deve permanecer versionado e imutável. O marketplace não instala código diretamente da branch `main`.

## Requisitos para receitas

Receitas agrupam módulos para montar um projeto Gravewright completo:

```json
{
  "schema_version": 1,
  "kind": "recipe",
  "name": "dark-fantasy-table",
  "title": "Dark Fantasy Table",
  "version": "1.0.0",
  "description": "Servidor e módulos para uma mesa dark fantasy.",
  "modules": [
    {
      "manifest_url": "https://example.org/server/latest.json",
      "version": "^1.0.0",
      "state": "active"
    },
    {
      "manifest_url": "https://example.org/fog-of-war/latest.json",
      "version": "~1.2.0",
      "state": "active"
    }
  ]
}
```

Uma receita:

- Não é um módulo executável.
- Não pode conter scripts.
- Deve produzir um projeto com exatamente um módulo `server` ativo.
- Pode usar versões exatas, `*`, `^` ou `~`.

## Segurança

Antes da instalação, o Gravewright:

- Aceita somente URLs HTTPS públicas.
- Bloqueia hosts privados e reservados.
- Valida redirects.
- Limita o tamanho dos downloads.
- Verifica o SHA-256 do ZIP.
- Rejeita path traversal e links simbólicos.
- Valida o manifest contido no pacote.
- Não sobrescreve módulos existentes.
- Prepara todos os módulos de uma receita antes do commit.

Uma entrada pode ser removida ou adicionada à lista de releases revogadas caso apresente riscos aos usuários.

## Catálogo

O arquivo [`gravewright.marketplace.json`](./gravewright.marketplace.json) segue esta estrutura:

```json
{
  "schema_version": 1,
  "packages": [],
  "revoked": []
}
```

Alterações no catálogo são feitas pelos mantenedores após a revisão das solicitações abertas nas issues.

## Remoção e revogação

Para solicitar a remoção de um projeto ou informar uma vulnerabilidade:

- Abra uma issue para problemas públicos e não sensíveis.
- Não publique detalhes exploráveis de vulnerabilidades em issues públicas.
- Para problemas de segurança, utilize o canal privado de segurança da organização.

## Licença

Os projetos listados continuam sujeitos às suas próprias licenças.

A presença no Gravewright Marketplace não transfere propriedade, responsabilidade ou direitos sobre módulos e receitas de terceiros.
