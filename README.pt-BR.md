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

[DnD 5e SRD](https://github.com/Gravewright/dnd-srd-5e) **0.1.2** reúne os perfis
2014 (SRD 5.1) e 2024 (SRD 5.2.1) em um único pacote de sistema para o
**Gravewright VTT 0.2.3 já publicado**. Instale em **Sistemas** e selecione essa
versão para a mesa. Fichas, modelos de itens, compêndios SRD licenciados,
iniciativa e automações de efeitos pertencem ao pacote. O mestre avança o combate
pelo tracker do sistema. O core e a release do VTT permanecem inalterados.

A versão 0.1.2 compacta as fichas de personagem e monstro, as janelas de rolagem
e os onze editores de itens, com texto de interface de pelo menos 12 px. As
perícias aparecem em ordem alfabética no idioma de interface escolhido. Cada
perícia mantém o atributo selecionado; a janela de rolagem também permite uma
troca temporária. Os ajustes de layout do diretório nativo de itens e do navegador
de compêndios pertencem ao VTT, separadamente deste ZIP de sistema.

O pacote atual usa somente `gravewright.5e-srd` (`type: "system"`), sem extensão
de servidor nem ativação de Python. Instalações anteriores podem revisar o
complemento antigo em **Personalizar** no próprio sistema; o proprietário do
host autoriza a desativação e a remoção após conferir as mesas afetadas. Fichas,
itens, opções da mesa e assinaturas de versões históricas são preservados.

Inglês é o idioma padrão. Ative o Translator oficial 0.1.2 para a interface em
português ou espanhol; os textos dos compêndios SRD permanecem em inglês.
O catálogo descreve o requisito da aplicação, mas não impõe versão mínima do
VTT. Veja no repositório de origem as licenças e as automações disponíveis.

## Savage Worlds Compatibility Package for Gravewright

[Savage Worlds Compatibility Package for Gravewright](https://github.com/Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright)
0.1.1 oferece fichas SWADE editáveis, estruturas vazias de itens, iniciativa com
cartas nativas e automações pertencentes ao pacote. Não inclui conteúdo de jogo
ou compêndios. Funciona na versão publicada **Gravewright VTT 0.2.3**, com as APIs
públicas existentes, sem exigir uma nova release do VTT.

Instale o único pacote `gravewright.savage-worlds` (`type: "system"`) em
**Sistemas** e selecione-o na mesa. Fichas, imagens e regras Savage Worlds ficam
nesse sistema JavaScript. O mestre avança os turnos e os relógios pelo tracker.
Operações persistidas retomam atualizações interrompidas sem repetir etapas já
concluídas. Instalações novas usam somente esse ZIP. Se a extensão antiga ainda
estiver ativa, use a migração no próprio sistema para desativá-la e removê-la,
preservando personagens, itens e configurações da mesa.

O idioma padrão é inglês. Ative o Translator oficial 0.1.2 para português do
Brasil ou espanhol e escolha seu idioma nas configurações da conta. Em
**Extensões → Personalizar** da mesa, escolha um dos três baralhos de ação
originais e crie-o no gerenciador nativo, ou selecione um baralho existente.
As cartas vêm do baralho configurado. Veja o [workflow de publicação assinada](PUBLISHING.pt-BR.md#publicar-savage-worlds-compatibility-package-for-gravewright)
e o repositório de origem para instalação, permissões e automações disponíveis.

## Gravewright 3D Dice

Instale [Gravewright 3D Dice v0.1.1](https://github.com/Gravewright/marketplace/releases/tag/gravewright-3d-dice-v0.1.1) e ative-o em **Extensões** dentro de cada mesa. Esta versão corrige os avisos de materiais e sombras do Three.js. A aparência dos dados é configurada individualmente.

## Atualizar e remover

Use **Atualizar** nas listas de módulos instalados para instalar uma versão assinada mais recente, mantendo a ativação e as configurações salvas. **Remover** lista as mesas afetadas para confirmação e retira o pacote dessas mesas. Os arquivos e as assinaturas das versões anteriores permanecem inalterados.

Validação local: `python scripts/validate_catalog.py` em um ambiente com `cryptography`.

## Categorias definidas pelo criador

O registro pode incluir `"type": "module"`, `"system"` ou `"django"` e `"tags": ["Tradução", "Idiomas", "Interface"]`. A modal do VTT gera suas categorias a partir dessas tags, separadamente para sistemas e módulos. São aceitas até 24 tags únicas, não vazias, de até 64 caracteres, incluindo acentos. Pacotes Django precisam de ativação explícita pelo proprietário do host, via Runner gerenciado; instalar o ZIP não importa seu código Python automaticamente.

As tags fazem parte da assinatura. Alterá-las exige assinar novamente o registro; o ZIP e seu SHA-256 podem permanecer iguais se o pacote não mudou. Este formato exige o suporte a tags do host atualizado.
