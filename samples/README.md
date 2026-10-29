# Áudios para o primeiro teste

Esta pasta acompanha pequenos arquivos de exemplo para abrir o Audition Manager
logo após o clone:

- `di/clean_guitar.wav`: DI limpa.
- `di/distorced_guitar.wav`: DI com distorção.
- `ir/`: quatro Impulse Responses mono a 44,1 kHz.
- `captures/`: duas capturas NAM A2 de guitarra redistribuíveis para usar junto
  com um IR:
  - `riffsmith-clean.nam`
  - `riffsmith-distorted.nam`

Na aplicação, escolha uma DI com **Abrir DI WAV** e selecione a pasta `ir` com
**Selecionar pasta de IRs**. Clique em qualquer IR listado para iniciar o
processamento e a reprodução.

Para testar uma captura, compile antes o runtime NAM conforme o README, escolha
`captures`, selecione o amplificador e depois selecione um IR. A aplicação
processará `DI → NAM → IR`. Os bypasses independentes permitem comparar a
captura sem gabinete, somente o IR e a DI limpa.

Em capturas A2, escolha **Full** para maior fidelidade ou **Lite** para processar
mais rápido. O seletor não se aplica a capturas NAM legadas.

Os áudios de exemplo são materiais de teste e não são cobertos automaticamente
pela licença MIT do código. Preserve os direitos e condições associados aos
arquivos de áudio ao redistribuí-los.

As duas capturas RiffSmith foram treinadas por Matt Hartman e são distribuídas
sob licença MIT. A origem, o commit e a licença estão documentados em
[`captures/SOURCES.md`](captures/SOURCES.md). Capturas adicionadas localmente
mantêm suas próprias condições e não devem ser enviadas ao Git sem autorização.
