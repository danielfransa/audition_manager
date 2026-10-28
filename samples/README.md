# Áudios para o primeiro teste

Esta pasta acompanha pequenos arquivos de exemplo para abrir o Audition Manager
logo após o clone:

- `di/clean_guitar.wav`: DI limpa.
- `di/distorced_guitar.wav`: DI com distorção.
- `ir/`: quatro Impulse Responses mono a 44,1 kHz.
- `captures/`: local para capturas NAM A2 usadas junto com um IR.

Na aplicação, escolha uma DI com **Abrir DI WAV** e selecione a pasta `ir` com
**Selecionar pasta de IRs**. Clique em qualquer IR listado para iniciar o
processamento e a reprodução.

Para testar uma captura, compile antes o runtime NAM conforme o README, escolha
`captures`, selecione o amplificador e depois selecione um IR. A aplicação
processará `DI → NAM → IR`. Os bypasses independentes permitem comparar a
captura sem gabinete, somente o IR e a DI limpa.

Os áudios de exemplo são materiais de teste e não são cobertos automaticamente
pela licença MIT do código. Preserve os direitos e condições associados aos
arquivos de áudio ao redistribuí-los.
