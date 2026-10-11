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

Instale [Translator v0.1.1](https://github.com/Gravewright/marketplace/releases/tag/gravewright.translator-v0.1.1) e, em **Módulos instalados**, ative os idiomas. O seletor aparece somente nas configurações internas da conta: inglês, português do Brasil e espanhol. A ativação é global; a preferência é individual.

Esta versão exige um host com suporte a `manifest.locales` e à ativação global. Inclui os textos atuais de permissões, compartilhamento, referências, janelas e gerenciamento de pacotes. A cobertura e os limites estão documentados no [repositório Translator](https://github.com/Gravewright/translator).

## Gravewright 3D Dice

Instale [Gravewright 3D Dice v0.1.1](https://github.com/Gravewright/marketplace/releases/tag/gravewright-3d-dice-v0.1.1) e ative-o em **Extensões** dentro de cada mesa. Esta versão corrige os avisos de materiais e sombras do Three.js. A aparência dos dados é configurada individualmente.

## Atualizar e remover

Use **Atualizar** nas listas de módulos instalados para instalar uma versão assinada mais recente, mantendo a ativação e as configurações salvas. **Remover** lista as mesas afetadas para confirmação e retira o pacote dessas mesas. Os arquivos e as assinaturas das versões anteriores permanecem inalterados.

Validação local: `python scripts/validate_catalog.py` em um ambiente com `cryptography`.

## Categorias definidas pelo criador

O registro pode incluir `"type": "module"` (ou `"system"`) e `"tags": ["Tradução", "Idiomas", "Interface"]`. A modal do VTT gera suas categorias a partir dessas tags, separadamente para sistemas e módulos. São aceitas até 24 tags únicas, não vazias, de até 64 caracteres, incluindo acentos.

As tags fazem parte da assinatura. Alterá-las exige assinar novamente o registro; o ZIP e seu SHA-256 podem permanecer iguais se o pacote não mudou. Este formato exige o suporte a tags do host atualizado.
