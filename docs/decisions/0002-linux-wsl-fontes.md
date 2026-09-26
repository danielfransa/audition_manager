# 0002 — Linux, WSL e legibilidade das fontes

Data: 2026-09-26.

O usuário ampliou o escopo para Windows e Linux, incluindo execução da GUI e
testes rápidos no WSL. Esta decisão substitui a restrição inicial que tratava
WSL apenas como ambiente de desenvolvimento. O prompt original foi preservado.
Cada plataforma precisa de validação própria, especialmente saída de áudio.

## Diagnóstico

Na imagem enviada, todos os textos, inclusive os seletores de arquivos, aparecem
como quadrados. No ambiente, `fc-list` retornou vazio e o Qt listou apenas
Monospace, Sans Serif e Serif, sem uma fonte real capaz de desenhar os textos.
Isso indica falta de fontes no Linux, não um problema de codificação dos textos.

## Correção

- Instalar uma fonte do sistema: `ttf-dejavu` no Arch, atualizar o cache com
  `fc-cache -f` e reiniciar a aplicação.
- Preservar a fonte padrão quando ela tem os caracteres necessários; buscar
  uma alternativa instalada quando não tem. A configuração é aplicada antes
  de criar os widgets, sem fixar um tema ou uma fonte exclusiva de um sistema.
- Se não existir fonte legível, encerrar com uma instrução no terminal. Um
  diálogo gráfico também seria ilegível nessa situação.
- Documentar fontes, bibliotecas Qt e PortAudio para Linux; usar WSLg para GUI
  e ponte de áudio, sem prometer latência equivalente ao Windows nativo.

Não distribuímos arquivos de fontes nem criamos dependência Python adicional.
Ainda não há instalador: dependências nativas devem ser preparadas conforme o
README. O fluxo funcional da primeira fatia permanece o mesmo.

## Fontes consultadas

- [Pacote DejaVu do Arch](https://archlinux.org/packages/extra/any/ttf-dejavu/)
- [Qt: banco de fontes do sistema](https://doc.qt.io/qt-6/qfontdatabase.html)
