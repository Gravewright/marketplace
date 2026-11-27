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

[DnD 5e SRD 0.2.2](https://github.com/Gravewright/marketplace/releases/tag/gravewright.5e-srd-v0.2.2)
reúne os perfis **2014 / SRD 5.1** e **2024 / SRD 5.2.1** em um único sistema
assinado para o navegador. Como proprietário do host, atualize o catálogo do
Marketplace, abra **Sistemas** e instale ou atualize **DnD 5e SRD**. Em cada mesa
existente, selecione **0.2.2** em **Configurações → Extensões** e recarregue as
páginas abertas. Mantenha a versão anterior instalada se precisar selecioná-la
novamente para reverter a atualização.

O pacote funciona no **Gravewright VTT 0.2.3 publicado**, com SDK 1.x.
No **VTT 0.3.8**, usa lotes nativos de iniciativa e organiza os vinte e dois
pacotes de compêndio na pasta **DnD 5e SRD**, com uma subpasta por edição. Hosts
anteriores mantêm a recuperação sequencial da iniciativa e a lista plana de
compêndios.

A versão 0.2.2 corrige automações suportadas conferidas com o SRD oficial,
incluindo CA por Destreza, PV por Constituição, itens de proteção e o estilo
de luta Defesa. As coleções licenciadas contêm **2.535 entradas de itens**,
**317 monstros do SRD 5.1** e **330 monstros do SRD 5.2.1**. Jogadores podem copiar
itens legíveis dos compêndios para fichas editáveis, respeitando as permissões
de leitura do servidor. Importações para a biblioteca e Efeitos continuam
exclusivos do mestre. As coleções são parciais; regras sem automação declarativa
suportada continuam manuais.

O identificador estável é `gravewright.5e-srd` (`type: "system"`). Fichas,
modelos de itens, traduções, configurações, iniciativa e automações de turno
suportadas pertencem a esse único pacote. O mestre avança o combate pelo tracker
do sistema. Instalações novas dispensam extensão de servidor e ativação de
Python. Instalações anteriores podem revisar um complemento antigo em
**Personalizar**; o proprietário do host autoriza a desativação e a remoção após
conferir as mesas afetadas. Fichas, itens e configurações das mesas são preservados.

Inglês é o idioma padrão da interface. Ative o Translator oficial **0.1.2 ou
mais recente** para português ou espanhol; os textos dos compêndios SRD
permanecem em inglês. O catálogo descreve o requisito da aplicação, mas não
impõe versão mínima do VTT. A
[release de origem](https://github.com/Gravewright/dnd-srd-5e/releases/tag/v0.2.2)
oferece o mesmo ZIP para instalação local. Veja no repositório de origem as
licenças, automações suportadas e instruções de instalação.

## Savage Worlds Compatibility Package for Gravewright

A versão **0.1.4** compacta ainda mais as fichas e usa os tipos **Carta Selvagem** e **Extra**. O mestre escolhe o tipo na criação; o setup da ficha não oferece mais esse seletor. Os identificadores e dados existentes são preservados.

[Savage Worlds Compatibility Package for Gravewright](https://github.com/Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright)
0.1.4 oferece fichas SWADE editáveis, estruturas vazias de itens, iniciativa com
cartas nativas e automações pertencentes ao pacote. Não inclui conteúdo de jogo
ou compêndios. Funciona na versão publicada **Gravewright VTT 0.2.3**, com as APIs
públicas existentes, sem exigir uma nova release do VTT.

A versão 0.1.2 compacta as fichas, as janelas de rolagem e os treze editores de
itens, com texto de interface de pelo menos 12 px. As perícias e outras listas
de nomes aparecem em ordem alfabética no idioma de interface escolhido, sem
reordenar as coleções salvas. Cada perícia oferece um seletor de atributo
vinculado, mantendo seu próprio dado e modificador. Os ajustes de layout do
diretório nativo de itens e do navegador de compêndios pertencem ao VTT,
separadamente deste ZIP de sistema.

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
