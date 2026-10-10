# Publicação e chaves de assinatura

O workflow **Sign and publish package** deste repositório gera os pacotes do
3D Dice e do Translator a partir de seus repositórios públicos. Os novos ZIPs,
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
5. O workflow publica uma Release imutável por versão e acrescenta o registro
   assinado ao catálogo. Se o push do catálogo falhar, o registro fica em
   `catalog.json` na Release: revise e incorpore esse registro ao catálogo,
   executando `python scripts/validate_catalog.py`. Não substitua o ZIP publicado.

O ambiente aceita somente a branch `main`. A chave privada fica no Secret de
ambiente `SIGNING_PRIVATE_KEY`; seu identificador fica na variável de ambiente
`SIGNING_KEY_ID`. A etapa de assinatura usa o segredo em memória e não executa
código do pacote de origem. O `GITHUB_TOKEN` temporário escreve somente neste
repositório; não é necessário salvar um PAT para acessar outros repositórios.

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
