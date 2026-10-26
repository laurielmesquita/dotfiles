# Verificação — 26/10/2026

## Origem e escopo

- Captura das configurações ativas de Wave e Zed e do código-fonte do auxiliar criado neste chat.
- Referência dos temas: assets locais `codex-dark-5fb95d1c65ca.js` e `codex-light-53d4e35e1869.js` do Codex 26.1021.31345.
- Versões observadas na captura deste repositório: Wave 0.14.5 e Zed 1.25.3. A configuração inicial do Zed foi preparada quando a versão observada era 1.25.2.
- O `.zshrc` integral não é versionado. `zsh/prompt.zsh` contém somente o tema, a lista de plugins e os estilos de realce pertinentes.
- Modelo de README: `Space Square/03-Internal Projects/ss-engineering/readme-template/README.md`; estrutura, navegação, badges e rodapé adaptados. Logo/hero genéricos e comandos npm não pertinentes foram removidos.

## Validação executada

Em 26/10/2026: nove testes Python passaram em HOME temporário; `dotfiles.py check` passou; o auxiliar Swift compilou com o compilador instalado e seu autoteste passou. A instalação no HOME real foi executada somente em prévia. Um backup local integral dos arquivos gerenciados foi criado. A revisão por padrões comuns de credenciais não encontrou correspondências; isso não é uma certificação de ausência de todo tipo possível de dado sensível.

- JSON das configurações e temas, sintaxe Zsh e template plist.
- Correspondência das 16 cores ANSI entre Wave e as duas variantes do Zed.
- Testes de mesclagem preservando preferências não gerenciadas, prévia sem escrita e instalação repetida sem duplicar o bloco do Zsh.
- Restauração de bytes e permissões originais, incluindo remoção de arquivos que não existiam antes.
- Recusa de JSON inválido, symlinks de destino e caminhos externos no manifesto de restauração.
- Captura de preferências sem tokens e sem variáveis de ambiente do terminal.
- Compilação e autoteste do auxiliar Swift em diretório temporário.
- Revisão dos arquivos versionados e diff do Git antes do commit inicial.

Os testes operam em HOME temporário. A criação deste repositório não reinstala nem aplica novamente as configurações ativas.

## Limites de evidência

- Controle de interface não estava autorizado; não houve revisão visual do Zed ou do Wave pelo agente.
- O usuário ainda não confirmou visualmente que desativar WebGL eliminou os retângulos pretos no tema claro do Wave.
- O auxiliar ativo foi conferido em execução, sem erros, com tema compatível com a aparência corrente. O autoteste exercita claro e escuro isoladamente; uma troca real de aparência do macOS não foi acionada.
- Temas manuais de blocos Wave prevalecem sobre o padrão global. O auxiliar controla o terminal, não toda a interface do Wave.
- O código usa cores de origem do Codex; superfícies exclusivas do Zed são adaptações. Linguagens/extensões podem acrescentar categorias ou recorrer a cores herdadas. Não há garantia de igualdade visual pixel a pixel em todos os contextos.
- Restauração validada em diretório temporário, não em um segundo Mac. Dependências não são instaladas pelo script.
- Backups completos são locais e não criptografados. A publicação inicial foi privada em 26/10/2026. A versão pública usa histórico com e-mail noreply e repositório independente do arquivo privado original. Apenas o conteúdo versionado é enviado; backups integrais permanecem privados e precisam de estratégia própria contra perda do equipamento.

## Fontes técnicas

- [Temas do Zed](https://zed.dev/docs/themes)
- [Terminal e contraste no Zed](https://zed.dev/docs/terminal)
- [Personalização do Wave](https://docs.waveterm.dev/customization)
- [Relato de fundos pretos no Wave 0.14.5](https://github.com/wavetermdev/waveterm/issues/3563) — indício usado para o contorno, não prova de resolução neste Mac.

## Ajuste de cursor — 26/10/2026

Cursor do Wave alterado de bloco para barra vertical (`term:cursor = bar`), conforme preferência do usuário. Configuração ativa e snapshot versionado foram atualizados; o campo foi incluído na lista de captura. Backup local criado antes da alteração. Conferência visual ainda depende do aplicativo.
