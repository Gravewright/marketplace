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

A origem é `Gravewright/dnd-srd-5e`. Preserve o ID `gravewright.5e-srd` e o nome
**DnD 5e SRD**. Cada versão tem um único ZIP de sistema para o navegador, com
fichas, modelos de itens, compêndios SRD licenciados, traduções e automações
JavaScript. Não publique outro pacote de servidor.

Publique `v{versão}` no repositório de origem com
`gravewright-5e-srd-{versão}.zip` e seu checksum. Execute **`dnd5e`** uma vez,
com o SHA completo da origem. O workflow usa o commit público inalterado do
VTT 0.2.3 nos testes do SDK e da instalação nativa. Verifica JavaScript,
traduções e compêndios, gera o ZIP antes do teste de instalação e valida
arquivos exatos, CRC, SHA-256 e avisos de licença. Os compêndios compilados e
sua proveniência permanecem intactos; reconstruir as fontes licenciadas é uma
operação separada.

`scripts/release.py prepare` confere a tag, a release pública, os metadados do
download e cada arquivo e permissão contra o build testado. O ZIP público
imutável forma o único artefato enviado à aprovação e assinatura. Sistemas com
manifest Django ou fontes Python no runtime são rejeitados. O job de assinatura
recebe apenas o ZIP aprovado e não executa código do projeto de origem.

Após publicar e conferir o download do substituto, o mesmo commit do catálogo
acrescenta o novo registro `type: "system"` e retira todas as entradas
`gravewright.5e-srd-server`. Preserve os demais registros históricos, URLs e
assinaturas. Não retire o registro antigo antes de o sistema assinado estar
disponível. Confira todas as assinaturas e instale o ZIP público no VTT 0.2.3
original e isolado antes de atualizar os links. Não publique uma release do VTT
para esta alteração no pacote do sistema.

O catálogo aceita somente os campos documentados. Descreva o requisito de VTT
0.2.3 e o Translator oficial opcional; não invente campos de dependência ou
versão mínima. O SDK continua `>=1.0.0 <2.0.0`. Instalações antigas usam os
controles do sistema para autorizar a desativação do complemento pelo reinício
nativo; remover o arquivo exige outra confirmação após conferir as mesas
afetadas. Uma instalação nova precisa somente do ZIP do sistema. O mestre
conduz as automações de combate na mesa, sem ativar extensão Python.

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
