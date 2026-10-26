# Dotfiles

Repositório pessoal de configurações de Zsh, Wave e Zed para macOS.

- Preserve os temas claros e escuros e o azul original do Codex. Não ajuste contraste ou cores por iniciativa própria.
- Leia README.md, manifest.json e docs/VERIFICATION.md antes de alterar instalação ou restauração.
- Os comandos de instalação/restauração mostram uma prévia sem `--apply`. Valide em um HOME temporário antes de aplicá-los ao ambiente real.
- Não versione credenciais, histórico, sessões, backups, binários ou diretórios completos de aplicativos/agentes. O `.zshrc` integral fica apenas no backup local.
- Não instale pacotes, altere configurações ativas ou publique mudanças como efeito de editar uma cópia versionada.
- O auxiliar do Wave reage a notificações do macOS; preserve ausência de polling e acesso à rede.
- Valide com `python3 scripts/dotfiles.py check` e `python3 -m unittest discover -s tests -v`.
