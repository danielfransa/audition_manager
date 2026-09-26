# 0003 — Ponte de áudio do WSLg

Data: 2026-09-26.

O erro `Error querying device -1` ocorreu ao abrir a saída padrão, depois da
convolução. O servidor PulseAudio do WSLg está acessível e tem saída RDPSink,
mas PortAudio não enumera dispositivos. No Arch faltam `alsa-plugins` e
`pulseaudio-alsa`, que permitem usar PulseAudio via ALSA.

Manter sounddevice/PortAudio e instalar a integração nativa do sistema, sem
trocar a biblioteca de reprodução. Não iniciar um segundo servidor PulseAudio
no WSL nem alterar configurações de áudio automaticamente pela aplicação.

O adaptador consulta a saída padrão antes de reproduzir e traduz falhas de
consulta em mensagem acionável. Falhas posteriores de abertura do stream
continuam distintas, pois podem envolver taxa, canais ou dispositivo ocupado.

Os exemplos fornecidos foram usados localmente para validar as oito combinações
DI/IR. Os testes automatizados continuam usando amostras sintéticas para não
depender da disponibilidade ou licença desses arquivos.

Referências:

- [ArchWiki: PulseAudio e integração ALSA](https://wiki.archlinux.org/title/PulseAudio)
- [WSLg: servidor de áudio integrado](https://github.com/microsoft/wslg)
