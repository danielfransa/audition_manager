# 0014 — NAM A2 primeiro, AM4DATA depois e pacote Windows

O usuário priorizou capturas NAM A2 disponíveis em catálogos como TONE3000 e
confirmou a necessidade futura de usar a M-VAVE BlackBox.

## Formatos e runtime

- A grafia adotada é **NAM A2**: segunda arquitetura do Neural Amp Modeler. O
  arquivo continua usando extensão `.nam`; a arquitetura e sua configuração
  são declaradas dentro do documento do modelo.
- A2 adiciona configurações que runtimes NAM antigos não compreendem, incluindo
  modelos `SlimmableContainer`. Aceitar a extensão `.nam` não basta para afirmar
  compatibilidade. Os testes usarão um modelo A2 conhecido e validarão a
  arquitetura antes do processamento.
- O runtime de referência escolhido para a próxima investigação é o
  `NeuralAmpModelerCore`, usado pelo plugin oficial e pelo plugin open source do
  TONE3000. Ele tem implementação C++ própria para inferência e exemplos A2.
- O pacote Python `neural-amp-modeler` é voltado principalmente a treinamento e
  traz PyTorch e outras dependências grandes. Ele não será adicionado ao app
  apenas para tocar capturas antes de medir uma integração menor com o Core.
- A M-VAVE documenta no changelog de seu software a conversão NAM para
  `AM4DATA`. Trataremos AM4DATA como formato do equipamento: inicialmente, o
  Audition Manager organiza/exporta o `.nam`, e o conversor oficial produz o
  arquivo da BlackBox. Não criaremos um encoder proprietário sem especificação.

## Distribuição Windows

- O primeiro artefato é um pacote portátil **one-folder** do PyInstaller. Ele
  inclui `AuditionManager.exe`, Python e DLLs na mesma pasta, compactada em ZIP.
  Esse modo facilita identificar DLLs ausentes e problemas de áudio.
- PyInstaller não faz cross-compilation oficial. O executável Windows deve ser
  construído com Python para Windows, em Windows. O WSL continua responsável
  pelos testes Linux, mas não produz o `.exe` final.
- `scripts/build-windows.ps1` cria uma venv exclusiva, instala dependências,
  executa os testes, gera o pacote e inclui README e licença. Não exige Python
  na máquina que apenas executará o ZIP.
- Um instalador e assinatura de código serão avaliados depois da validação do
  pacote portátil. Isso separa defeitos do programa de problemas do instalador.

## Fontes consultadas

- Neural Amp Modeler, especificação do arquivo `.nam`:
  <https://github.com/sdatkinson/neural-amp-modeler/blob/main/docs/source/model-file.rst>
- Releases do projeto de treinamento, incluindo a adoção de A2:
  <https://github.com/sdatkinson/neural-amp-modeler/releases>
- NeuralAmpModelerCore e seu modelo A2 de exemplo:
  <https://github.com/sdatkinson/NeuralAmpModelerCore/blob/main/example_models/A2.nam>
- Plugin open source TONE3000 e sua integração com NeuralAmpModelerCore:
  <https://github.com/tone-3000/tone3000-plugin>
- Downloads/changelog oficial da M-VAVE, com NAM para AM4DATA:
  <https://www.m-vave.com/download>
- Documentação do PyInstaller sobre builds por sistema e pacote one-folder:
  <https://pyinstaller.org/en/stable/operating-mode.html>
