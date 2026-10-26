# Privacidade e publicação

## Conteúdo público

O repositório contém temas, preferências selecionadas, scripts, documentação e imagens. Os commits públicos usam o endereço noreply da conta GitHub. A configuração de e-mail foi alterada somente neste repositório, sem modificar a preferência global de outros projetos.

Os quatro commits originais foram reconstruídos preservando árvores de arquivos, mensagens, autores e datas, com substituição do e-mail pessoal nos campos de autor e committer. Os hashes mudaram. A sequência higienizada foi enviada para um repositório independente; o repositório original permanece privado, separado da publicação, porque apenas reescrever uma branch não garante a remoção de commits antigos dos caches do GitHub.

## Conteúdo que deve permanecer privado

- Credenciais, chaves, certificados e arquivos `.env`.
- Histórico do shell, sessões dos aplicativos, logs e arquivos de agentes.
- Backups integrais, bundles do Git e cópias da configuração local do Git.
- Variáveis de ambiente do terminal e configurações não incluídas na lista permitida em `manifest.json`.

O comando `capture` não exporta o `.zshrc` integral. O trecho Zsh versionado é mantido manualmente. Os backups de recuperação ficam fora deste repositório e podem conter dados pessoais; não devem ser publicados.

## Antes de enviar alterações

1. Confira `git diff --cached` e os arquivos que serão incluídos.
2. Confira que o e-mail retornado por `git config user.email` é o noreply desejado para este projeto.
3. Mantenha testes e verificações passando. O `.gitignore` não remove dados já commitados.
4. Não envie o histórico original, bundles ou backups para branches ou tags públicas.

A revisão de publicação procura formatos comuns de credenciais e o e-mail pessoal no conteúdo e no histórico alcançável. Essa revisão não certifica a ausência de todo tipo possível de segredo. Ferramentas, versões, preferências e identidade pública do mantenedor continuam visíveis por decisão de publicação.

## Referências

- [E-mail dos commits no GitHub](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)
- [Remoção de dados e limites de reescrita do histórico](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [Visibilidade de repositórios](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
