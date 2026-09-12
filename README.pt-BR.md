# Marketplace do Gravewright

Catálogo assinado de módulos e sistemas, com arquivos ZIP publicados nas releases dos respectivos repositórios.

Configure no ambiente do VTT:

```dotenv
GRAVEWRIGHT_MARKETPLACE_URL=https://raw.githubusercontent.com/Gravewright/marketplace/main/gravewright.marketplace.json
GRAVEWRIGHT_MARKETPLACE_KEYS_FILE=/caminho/absoluto/marketplace/trusted-keys.json
```

Reinicie o VTT após alterar o ambiente. O arquivo de chaves contém somente chaves públicas Ed25519; a chave privada de publicação fica fora dos repositórios.

O catálogo usa uma lista JSON de registros assinados. O formato antigo com `schema_version`, `packages` e `revoked` não é aceito pelo host atual. Cada registro assina a identificação, versão, requisitos do SDK, URL HTTPS da release e SHA-256 do ZIP. Nome e descrição opcionais também são assinados. Veja [README.md](README.md) para o formato completo.

## Translator

Instale [Translator v0.1.0](https://github.com/Gravewright/translator/releases/tag/v0.1.0) e, em **Módulos instalados**, ative os idiomas. O seletor aparece somente nas configurações internas da conta: inglês, português do Brasil e espanhol. A ativação é global; a preferência é individual. Não há ativação ou seletor de idioma na mesa.

Esta pré-release exige as alterações do host que suportam `manifest.locales` e a ativação global. Hosts anteriores não são compatíveis. A cobertura e os limites estão documentados no [repositório Translator](https://github.com/Gravewright/translator).

Validação local: `python scripts/validate_catalog.py` em um ambiente com `cryptography`.
