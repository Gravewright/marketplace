# Marketplace do Gravewright

A assinatura e a publicação dos pacotes agora são feitas pelo workflow
**Sign and publish package**, com aprovação no ambiente `release-signing`.
Consulte [publicação, responsáveis e recuperação de chaves](PUBLISHING.pt-BR.md).

Catálogo assinado de módulos e sistemas. Novos ZIPs são publicados nas Releases
do Marketplace; os endereços das versões anteriores são preservados.

Configure no ambiente do VTT:

```dotenv
GRAVEWRIGHT_MARKETPLACE_URL=https://raw.githubusercontent.com/Gravewright/marketplace/main/gravewright.marketplace.json
GRAVEWRIGHT_MARKETPLACE_KEYS_FILE=/caminho/absoluto/marketplace/trusted-keys.json
```

Reinicie o VTT após alterar o ambiente. O arquivo de chaves contém somente chaves públicas Ed25519; a chave privada de publicação fica fora dos repositórios.

O catálogo usa uma lista JSON de registros assinados. O formato antigo com `schema_version`, `packages` e `revoked` não é aceito pelo host atual. Cada registro assina a identificação, versão, requisitos do SDK, URL HTTPS da release e SHA-256 do ZIP. Nome e descrição opcionais também são assinados. Veja [README.md](README.md) para o formato completo.

## Translator

Instale [Translator v0.1.2](https://github.com/Gravewright/marketplace/releases/tag/gravewright.translator-v0.1.2) e, em **Módulos instalados**, ative os idiomas. O seletor aparece somente nas configurações internas da conta: inglês, português do Brasil e espanhol. A ativação é global; a preferência é individual.

Esta versão exige um host com suporte a `manifest.locales` e à ativação global. Inclui catálogos revisados e documentação para outros módulos usarem a API oficial de tradução. A cobertura e os limites estão documentados no [repositório Translator](https://github.com/Gravewright/translator).

## DnD 5e SRD

[DnD 5e SRD](https://github.com/Gravewright/dnd-srd-5e) 0.1.0 Alpha oferece os
perfis de regras de 2014 (SRD 5.1) e 2024 (SRD 5.2.1). Exige **Gravewright VTT
0.2.1 ou posterior**. Após a entrada das releases assinadas no catálogo, instale
o pacote do navegador em **Sistemas** e selecione-o ao criar a mesa. Instale
**DnD 5e SRD - Server Rules**, na mesma versão, em **Módulos**. Como proprietário
do host, ative essa extensão Django pelo Runner gerenciado; a ativação reinicia
o servidor e fornece as automações de combate do sistema. O core não contém
regras de D&D. Instale e ative o Translator 0.1.2 para a interface em português
ou espanhol; o conteúdo dos compêndios SRD permanece em inglês.

Os dois pacotes são assinados separadamente: `gravewright.5e-srd`
(`type: "system"`) e `gravewright.5e-srd-server` (`type: "django"`). O nome
exibido não altera os identificadores usados nas mesas salvas. Instalar e ativar
são operações distintas; o catálogo não resolve dependências automaticamente
nem impõe uma versão mínima da aplicação VTT. Veja no repositório do sistema as
licenças, automações disponíveis e limitações.

## Gravewright 3D Dice

Instale [Gravewright 3D Dice v0.1.1](https://github.com/Gravewright/marketplace/releases/tag/gravewright-3d-dice-v0.1.1) e ative-o em **Extensões** dentro de cada mesa. Esta versão corrige os avisos de materiais e sombras do Three.js. A aparência dos dados é configurada individualmente.

## Atualizar e remover

Use **Atualizar** nas listas de módulos instalados para instalar uma versão assinada mais recente, mantendo a ativação e as configurações salvas. **Remover** lista as mesas afetadas para confirmação e retira o pacote dessas mesas. Os arquivos e as assinaturas das versões anteriores permanecem inalterados.

Validação local: `python scripts/validate_catalog.py` em um ambiente com `cryptography`.

## Categorias definidas pelo criador

O registro pode incluir `"type": "module"`, `"system"` ou `"django"` e `"tags": ["Tradução", "Idiomas", "Interface"]`. A modal do VTT gera suas categorias a partir dessas tags, separadamente para sistemas e módulos. São aceitas até 24 tags únicas, não vazias, de até 64 caracteres, incluindo acentos. Pacotes Django precisam de ativação explícita pelo proprietário do host, via Runner gerenciado; instalar o ZIP não importa seu código Python automaticamente.

As tags fazem parte da assinatura. Alterá-las exige assinar novamente o registro; o ZIP e seu SHA-256 podem permanecer iguais se o pacote não mudou. Este formato exige o suporte a tags do host atualizado.
