# 0018 — Áudios de exemplo no repositório

O usuário solicitou que as DIs e IRs existentes acompanhassem o
repositório para permitir um primeiro teste logo após o clone.

- Duas DIs e quatro IRs WAV passam a ser versionados. O conjunto ocupa cerca de
  5 MiB e não exige download adicional.
- Os arquivos foram organizados na pasta padrão em inglês `samples/`, com DIs em
  `samples/di` e respostas de impulso em `samples/ir`.
- Arquivos `Zone.Identifier` são metadados de segurança do Windows, não áudio.
  Os padrões `*:Zone.Identifier` e `*Zone.Identifier` ficam no `.gitignore`.
- O README principal aponta diretamente para a DI limpa e a pasta de IRs. Um
  README dentro da pasta descreve todo o conjunto.
- A licença MIT cobre o código do Audition Manager. Áudios mantêm suas próprias
  condições e direitos, conforme já declarado na documentação do projeto.
