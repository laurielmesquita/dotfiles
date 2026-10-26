<h1 align="center">dotfiles</h1>

<p align="center">
  <a href="#-tecnologias">Tecnologias</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#-projeto">Projeto</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#-instalação">Instalação</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#-licença">Licença</a>
</p>

<p align="center">
  <a href="https://github.com/laurielmesquita">
    <img alt="Mantido por Lauriel Mesquita" src="https://img.shields.io/static/v1?label=maintained%20by&message=Lauriel%20Mesquita&color=bd93f9&labelColor=181818">
  </a>
  <img alt="Plataforma macOS" src="https://img.shields.io/static/v1?label=platform&message=macOS&color=8be9fd&labelColor=181818">
  <img alt="Tecnologias Python, Swift e Zsh" src="https://img.shields.io/static/v1?label=stack&message=Python%20%7C%20Swift%20%7C%20Zsh&color=ff79c6&labelColor=181818">
  <img alt="Temas Codex Light e Dark" src="https://img.shields.io/static/v1?label=themes&message=Codex%20Light%20%26%20Dark&color=339cff&labelColor=181818">
  <img alt="Uso privado" src="https://img.shields.io/static/v1?label=usage&message=private&color=50fa7b&labelColor=181818">
</p>

<p align="center">Configurações pessoais de desenvolvimento, com histórico, backup e restauração.</p>

<br><br><br>

## 🚀 Tecnologias

- [Git](https://git-scm.com/doc): histórico de alterações e versões recuperáveis.
- [Python 3](https://docs.python.org/3/): captura seletiva, validação, mesclagem, backup e restauração, usando apenas a biblioteca padrão.
- [Swift e Foundation](https://www.swift.org/documentation/): auxiliar que recebe notificações de aparência do macOS e sincroniza o tema do terminal do Wave.
- [Zsh](https://zsh.sourceforge.io/Doc/) e [Oh My Zsh](https://ohmyz.sh/): prompt `robbyrussell`, nome da pasta, branch e indicador de alterações do Git.
- [Wave Terminal](https://docs.waveterm.dev/customization): paletas ANSI Codex Light e Codex Dark.
- [Zed](https://zed.dev/docs/themes): temas completos para interface, edição de código e terminal integrado.
- [Fira Code](https://github.com/tonsky/FiraCode): fonte de programação, em tamanho 14; ligaduras habilitadas no Zed.
- JSON/JSONC e Property Lists: configurações dos aplicativos e definição do LaunchAgent do macOS.

## 💻 Projeto

Este repositório reúne as configurações pessoais de Lauriel Mesquita para reproduzir o ambiente de terminal e edição de código em outro Mac ou recuperar uma configuração anterior. Os temas partem das paletas do Codex instalado; adaptações completam os elementos específicos do Zed. Os arquivos ativos permanecem nos diretórios nativos dos aplicativos.

**Estado inicial: 26/10/2026.** Captura local com Wave 0.14.5, Zed 1.25.3 e Codex 26.1021.31345. Versões são registros do ambiente observado, não exigências de versões futuras nem garantia de compatibilidade universal.

```text
dotfiles/
├── zsh/                         # Prompt, plugins e realce de comandos
├── wave/                        # Preferências de aparência e duas paletas
├── zed/
│   ├── settings.json            # Preferências selecionadas do editor
│   ├── themes/codex.json        # Codex Light e Codex Dark completos
│   └── reference/               # Cores de origem extraídas do Codex
├── macos/wave-theme-sync/       # Swift e template do LaunchAgent
├── scripts/dotfiles.py          # CLI de captura, backup e restauração
├── tests/                       # Testes em HOME temporário
├── docs/VERIFICATION.md         # Evidências e limitações conhecidas
└── manifest.json                # Arquivos, destinos e campos permitidos
```

### Temas e comportamento

- **Zsh:** `➜ nome-da-pasta git:(main) ✗`; as informações de Git aparecem em repositórios. O trecho versionado conserva plugins adicionais já configurados pelo usuário.
- **Wave:** cursor em barra vertical (`term:cursor: bar`); cores originais, incluindo o azul `#339cff`; sem transparência; WebGL desativado como contorno para os retângulos pretos observados no tema claro. A eficácia visual desse contorno ainda precisa de confirmação.
- **Aparência automática no Wave:** um LaunchAgent local recebe `AppleInterfaceThemeChangedNotification` e altera somente `term:theme`. Não usa polling nem rede. A interface externa do Wave tem comportamento próprio; blocos com tema fixo precisam selecionar a opção padrão/herdada.
- **Zed:** temas claro e escuro completos, seguindo o sistema, com 130 propriedades e 72 categorias de sintaxe por variante. As principais cores de código correspondem aos arquivos de origem do Codex; menus, diagnósticos, Git e busca recebem adaptações da mesma paleta.
- **Ligaduras:** habilitadas no editor e no terminal do Zed. O Wave 0.14.5 não oferece a configuração equivalente verificada neste ambiente.

### O que entra no backup

O Git guarda os arquivos selecionados de aparência, os temas e o código-fonte. `backup` também preserva localmente os arquivos ativos completos que podem ser alterados pela instalação, incluindo `.zshrc` e o binário do auxiliar quando existente.

Credenciais, variáveis de ambiente do terminal, históricos, sessões, logs, executáveis e backups não são exportados para o repositório. A captura usa listas explícitas de campos em `manifest.json`; ela não copia indiscriminadamente `.config` ou diretórios de agentes.

Os backups integrais ficam em `~/.local/state/dotfiles/backups/`, com diretórios privados e arquivos de permissão `600`. Podem conter dados locais sensíveis; não são criptografados. Um Git apenas local e backups no mesmo SSD não protegem contra perda do equipamento. A cópia remota privada ainda precisa ser criada e verificada.

## ⚙️ Instalação

### Pré-requisitos

macOS com Git, Python 3.9 ou superior, Zsh, Oh My Zsh, os plugins listados em `zsh/prompt.zsh`, Wave, Zed e Fira Code. Para recompilar o auxiliar, é necessário `swiftc` do Xcode ou Command Line Tools. O instalador não baixa aplicativos, fontes, plugins ou pacotes.

### Conferir e fazer backup

```bash
# Acesse a cópia local
cd "$HOME/Tech Hub/03-Dev Workflows/dotfiles"

# Valide os arquivos versionados e execute os testes isolados
python3 scripts/dotfiles.py check
python3 -m unittest discover -s tests -v

# Salve uma cópia local integral dos arquivos gerenciados
python3 scripts/dotfiles.py backup

# Veja a prévia da instalação, sem gravar nada
python3 scripts/dotfiles.py install
```

### Aplicar em um Mac preparado

```bash
# Mescle as preferências e salve backup antes de escrever
python3 scripts/dotfiles.py install --apply

# Para instalar também o auxiliar automático do Wave:
python3 scripts/dotfiles.py install --apply --enable-sync
```

`--enable-sync` recompila o Swift, executa seu autoteste e carrega o LaunchAgent do usuário. Não usa `sudo`. A ativação é permitida somente no HOME real do usuário; ela não acontece em testes com `--home`.

Os arquivos JSON/JSONC existentes são mesclados por chave; preferências não gerenciadas são preservadas. Comentários e formatação desses JSONs são normalizados na instalação e ficam preservados byte a byte no backup. Temas completos com o mesmo nome são substituídos pela cópia versionada; outros temas do Wave permanecem.

O instalador adiciona ao `.zshrc` um bloco identificado antes do carregamento do Oh My Zsh. O arquivo não é substituído integralmente. Configurações de prompt posteriores a esse carregamento ainda podem prevalecer. Se já houver um `.zshrc` sem uma linha reconhecível de carregamento do Oh My Zsh, a operação para antes de escrever. Destinos com symlink também são recusados para evitar alterações fora do alvo.

Abra novos terminais após aplicar. No Zed, confira `Codex Light` e `Codex Dark` no seletor de temas e o modo `system`. No Wave, remova seleções manuais de tema dos blocos que devem acompanhar o sistema.

### Atualizar a cópia versionada

```bash
# Mostre os arquivos de preferências que serão capturados
python3 scripts/dotfiles.py capture

# Capture apenas os campos de aparência autorizados no manifesto
python3 scripts/dotfiles.py capture --apply

# Revise antes de criar uma nova versão
git diff
python3 scripts/dotfiles.py check
```

`capture` atualiza somente as preferências selecionadas de Wave e Zed. Alterações de temas, Zsh e Swift devem ser feitas nos arquivos correspondentes do repositório. Não é uma sincronização automática ou bidirecional.

### Restaurar

```bash
# Substitua o exemplo pelo diretório retornado pelo comando backup/install
python3 scripts/dotfiles.py restore --snapshot "$HOME/.local/state/dotfiles/backups/SEU-BACKUP"

# Depois de conferir a prévia, restaure e recarregue o serviço do Wave
python3 scripts/dotfiles.py restore --snapshot "$HOME/.local/state/dotfiles/backups/SEU-BACKUP" --apply --enable-sync
```

A restauração recupera bytes e permissões anteriores e remove somente os arquivos gerenciados que não existiam naquele backup. Antes disso, salva o estado atual em outro backup, permitindo desfazer a própria restauração. Sem `--enable-sync`, os arquivos são restaurados, mas o serviço existente não é reiniciado.

## 🤝 Como Contribuir

Este é um repositório pessoal. Mudanças devem preservar as configurações particulares e ser conferidas antes de aplicadas ao ambiente ativo.

1. Crie uma branch, por exemplo `codex/ajustar-temas`.
2. Edite os arquivos versionados e atualize `docs/VERIFICATION.md` quando mudar o comportamento.
3. Execute a validação e os testes; para código Swift, execute também seu autoteste.
4. Revise o diff, incluindo exclusão de credenciais e dados de sessão, e crie um commit.
5. Instale somente depois de conferir a prévia. Push e publicação dependem de um remoto privado configurado.

**Idealização e manutenção:** Lauriel Mesquita. **Template de documentação:** Space Square, adaptado do modelo interno `ss-engineering/readme-template`. Configuração e implementação preparadas com auxílio do Codex.

## 📝 Licença

Repositório destinado a uso pessoal e privado. Nenhuma licença de redistribuição foi definida nesta etapa; o selo MIT do template não foi reproduzido como autorização implícita. Oh My Zsh, Wave, Zed, Fira Code e os demais componentes mantêm suas próprias licenças. O repositório não redistribui aplicativos, fontes ou plugins.

---
<br>
<p align="center">
  <img alt="May the Code Review be with you" src=".gitimg/code_review.png" />
</p>
