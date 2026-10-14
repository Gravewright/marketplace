# Publicação e chaves de assinatura

O workflow **Sign and publish package** deste repositório gera os pacotes do
3D Dice, do Translator, do DnD 5e SRD e do Savage Worlds a partir de seus repositórios públicos. Os novos ZIPs,
checksums, registros assinados e a referência ao commit de origem são publicados
nas Releases do Marketplace. Versões anteriores mantêm seus endereços e assinaturas.

## Publicar uma versão

1. Atualize a versão no projeto de origem e envie seu commit. Não reutilize versões.
2. Em Actions → Sign and publish package → Run workflow, escolha o projeto e seu
   commit, tag ou branch. Execute o workflow da branch `main` do Marketplace.
3. O job `build` testa e gera o ZIP sem acesso à chave privada. Confira o commit
   resolvido e o SHA-256 no resumo da execução e o artefato disponível para download.
4. Um responsável configurado no ambiente `release-signing` aprova a publicação
   em **Review deployments**. A aprovação libera o job que assina e publica.
5. O workflow publica uma Release imutável por versão, baixa novamente o ZIP
   público e confere seu SHA-256 antes de acrescentar o registro
   assinado ao catálogo. Se o push do catálogo falhar, o registro fica em
   `catalog.json` na Release: revise e incorpore esse registro ao catálogo,
   executando `python scripts/validate_catalog.py`. Não substitua o ZIP publicado.

## Publicar DnD 5e SRD

O código de origem fica em `Gravewright/dnd-srd-5e`. Preserve os IDs técnicos
`gravewright.5e-srd` e `gravewright.5e-srd-server` para manter a compatibilidade
com as mesas existentes. Os nomes exibidos são **DnD 5e SRD** e
**DnD 5e SRD - Server Rules**. Os dois manifests precisam ter a mesma versão.

Publique primeiro a release pública `v{versão}` no repositório de origem, com
seus ZIPs versionados. Execute o workflow duas vezes, sequencialmente, com o
**mesmo SHA completo** da origem: primeiro `dnd5e-server`, depois `dnd5e`.
Cada execução testa e constrói a origem, confirma que a tag Git da release aponta
para esse commit e baixa o ZIP público correspondente. O tamanho e o SHA-256
precisam conferir com os metadados do GitHub. Todos os caminhos, permissões e
arquivos descompactados precisam ser idênticos ao build testado; entradas extras,
duplicadas ou adulteradas são rejeitadas. Os bytes originais da release pública
formam o único ZIP enviado para aprovação e assinatura. Assim, a mesma identidade
ID/versão preserva seu arquivo imutável mesmo quando zlib e zlib-ng produzem
compressões DEFLATE diferentes. A concorrência do workflow impede que duas
publicações disputem a atualização do catálogo. O primeiro registro disponibiliza
o complemento de servidor antes de oferecer o sistema que depende dele.

O build usa um checkout fixo do VTT 0.2.1 apenas para testes da API oficial e
do backend, com `GRAVEWRIGHT_TEST_HOST_ROOT`. As dependências do VTT vêm do
seu `uv.lock`; não entram nos ZIPs. Os testes JavaScript, catálogos de idiomas e
regras de servidor são verificados. O build usa os compêndios SRD já gerados e
validados. Após o build, `scripts/validate_package.py` verifica os dados gerados,
traduções, compêndios, proveniência, arquivos exatos dos ZIPs, CRC, SHA-256 e
avisos de licença. Reconstruir os compêndios a partir dos PDFs/YAMLs licenciados é uma
operação separada no projeto de origem, com suas fontes e hashes fixos.

`scripts/release.py prepare` confere IDs, nomes, tipos, versões, release pública
de origem, igualdade entre o manifest da origem e o do ZIP, caminhos seguros,
presença dos compêndios e todo o conteúdo do arquivo publicado contra o build.
`dnd5e` gera um registro `type: "system"`; `dnd5e-server`, `type: "django"`.
Nunca publique o complemento como módulo comum para evitar esconder que ele
contém código Python confiável. O job de assinatura recebe apenas o ZIP
aprovado; não faz checkout nem executa código do sistema.

O catálogo atual aceita somente os campos documentados no README. Requisitos
como **VTT 0.2.1**, a instalação do complemento na mesma versão e Translator
para idiomas adicionais devem estar na descrição e na documentação: não
acrescente campos `dependencies` ou `minimumHost`, pois o host os rejeita.
O SDK continua `>=1.0.0 <2.0.0`; esse intervalo não substitui o requisito de VTT.

Depois de ambas as publicações, confirme as assinaturas, baixe os ZIPs públicos
e teste sua instalação no VTT 0.2.1. Só então atualize os links de disponibilidade
da documentação. Pacotes, registros e assinaturas já publicados são imutáveis.

O ambiente aceita somente a branch `main`. A chave privada fica no Secret de
ambiente `SIGNING_PRIVATE_KEY`; seu identificador fica na variável de ambiente
`SIGNING_KEY_ID`. A etapa de assinatura usa o segredo em memória e não executa
código do pacote de origem. O `GITHUB_TOKEN` temporário escreve somente neste
repositório; não é necessário salvar um PAT para acessar outros repositórios.

## Publicar Savage Worlds Compatibility Package for Gravewright

O código está em [Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright](https://github.com/Gravewright/Savage-Worlds-Compatibility-Package-for-Gravewright).
Publique somente `gravewright.savage-worlds` (`system`). Seu único manifest reúne
interface, definição do sistema e automações JavaScript. Publique primeiro a release
de origem `v{versão}`, com um ZIP e seu checksum. Execute **`swade`** com o SHA
completo da origem. O workflow verifica tag, SHA-256 público e todo o conteúdo do
pacote testado antes da aprovação e assinatura. O código do pacote não é executado
com acesso à chave privada.

O arquivo `gravewright-savage-worlds-{versão}.zip` inclui imagens, interface,
traduções e todas as automações. Não inclua fontes Python no runtime. Preserve o aviso exato da
Pinnacle e o logo aprovado. Não inclua compêndios, conteúdo de jogo ou PDFs.
O workflow retira a entrada do complemento antigo ao publicar o registro assinado
do sistema unificado no catálogo. Arquivos e assinaturas históricos permanecem
inalterados; o workflow não oferece mais o build de servidor separado.

Usa o **VTT 0.2.3 publicado**, sem modificar o host, com APIs existentes como
`context.host` e `card.asset.upload`. O workflow usa a tag pública `v0.2.3` e verifica esses
contratos antes do build. O catálogo não impõe versão mínima da aplicação; hosts
anteriores precisam atualizar o core. Confira os hashes dos ZIPs públicos antes de
executar o workflow. O idioma padrão é inglês. Para português ou espanhol, instale e
ative o Translator oficial 0.1.2. Instale em **Sistemas** e selecione na mesa.
O mestre usa o tracker para os turnos e relógios, com retomada persistente de
operações. Instalações com a extensão antiga usam a migração no próprio sistema;
instalações novas usam somente o ZIP do sistema.

## Responsáveis e recuperação

Em Settings → Environments → release-signing, mantenha os responsáveis pela
aprovação. Adicione outros mantenedores ou uma equipe da organização; cada pessoa
usa a própria conta. Mantenha mais de um administrador confiável na organização.
A configuração inicial permite que o responsável aprove uma execução que iniciou.
Quando houver outros responsáveis, pode-se exigir que a revisão seja feita por
outra pessoa habilitando **Prevent self-review**.

Formatar um computador não apaga os Secrets do GitHub. Porém, o GitHub não permite
baixar o valor de um Secret existente. Mantenha uma cópia da chave privada em um
gerenciador de senhas com acesso controlado e uma cópia de recuperação separada.
O arquivo local criado na configuração é apenas uma cópia de recuperação inicial:
transfira-o para o cofre; não o coloque em Git, anexos de issues ou artefatos.

## Trocar a chave

1. Gere uma nova chave Ed25519 e escolha um novo identificador.
2. Acrescente apenas sua chave pública a `trusted-keys.json`, mantendo as antigas.
3. Atualize o hash fixado no instalador Gravewright e distribua o arquivo público
   atualizado às instalações existentes antes de oferecer novos pacotes.
4. Atualize o Secret e a variável do ambiente protegido. Teste uma assinatura
   contra a chave pública antes de publicar.
5. Guarde a nova chave no cofre e retire o acesso dos responsáveis que saíram.

A chave perdida `gravewright-2026` continua no arquivo público para verificar os
pacotes já publicados. Ela não será usada para novas assinaturas. Se uma chave
for comprometida, trate a revogação separadamente; remover a chave pública antiga
impede a verificação dos pacotes assinados por ela.
