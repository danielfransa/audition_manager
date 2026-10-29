# Audition Manager — Windows portable package

## Português

Este pacote portátil não precisa de Python instalado.

1. Extraia **todo o ZIP** para uma pasta local.
2. Abra `AuditionManager.exe` dentro da pasta extraída.
3. Não mova apenas o `.exe`: as DLLs e `build/nam-runtime/nam-render.exe` precisam
   permanecer junto da aplicação.
4. A pasta `samples` incluída contém DIs, IRs e duas capturas NAM para o primeiro
   teste. Você também pode abrir seus próprios arquivos WAV e NAM.

O Windows pode exibir o SmartScreen porque este pacote de desenvolvimento ainda
não possui assinatura digital. Verifique a origem do download antes de executar.
Os dados locais ficam em `%LOCALAPPDATA%\Audition Manager\`.

Problemas encontrados nesta versão devem ser registrados com a versão do
Windows, dispositivo de áudio, mensagem apresentada e passos para reprodução.

## English

This portable package does not require an installed Python interpreter.

1. Extract the **complete ZIP** into a local directory.
2. Open `AuditionManager.exe` from the extracted directory.
3. Do not move the `.exe` alone: its DLLs and
   `build/nam-runtime/nam-render.exe` must remain beside the application.
4. The included `samples` directory contains DIs, IRs, and two NAM captures for
   the first test. You can also open your own WAV and NAM files.

Windows may display SmartScreen because this development package is not code
signed yet. Verify the download source before running it. Local data is stored
under `%LOCALAPPDATA%\Audition Manager\`.

When reporting a problem, include the Windows version, audio device, displayed
message, and reproduction steps.
