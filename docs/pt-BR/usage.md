# Como usar — Português

## Primeiro teste

1. Inicie com `mise run run` ou `audition-manager`.
2. Escolha **Português** ou **English** no seletor de idioma.
3. Clique em **Abrir DI WAV** e abra `samples/di/clean_guitar.wav`.
4. Clique em **Selecionar pasta de capturas NAM** e escolha `samples/captures`.
5. Selecione `riffsmith-clean.nam` ou `riffsmith-distorted.nam`.
6. Clique em **Selecionar pasta de IRs** e escolha `samples/ir`.
7. Selecione um IR. O áudio será processado como `DI → NAM → IR`.

## Comparar sons

- Clique ou use `Ctrl+←/→` para trocar a captura.
- Clique ou use `←/→` para trocar o IR.
- Use **A2 Full** para maior fidelidade ou **A2 Lite** para maior velocidade.
- Ajuste o ganho NAM para comparar capturas em níveis próximos.
- Use `N` para ignorar a captura e `B` para ignorar o IR.
- O medidor mostra o pico antes do ganho geral de saída.

## Organizar a biblioteca

IRs e capturas possuem busca, filtro de favoritos, avaliação e notas próprios.
As informações ficam no banco local; os arquivos de áudio não são copiados para
o banco. A última DI, pastas, captura, dispositivo, ganhos, Loop e idioma são
restaurados quando ainda estão disponíveis.

## Exportar favoritos

1. Marque IRs e capturas como favoritos.
2. Clique em **Exportar favoritos…**.
3. Escolha o diretório onde a nova pasta será criada.
4. Informe o nome e marque **Capturas**, **IRs** ou ambos.

O resultado usa somente as categorias selecionadas:

```text
Nome escolhido/
├── Capturas/
└── IRs/
```

Pastas vazias não são criadas e um destino existente não é sobrescrito.

## Limites atuais

- Processamento offline; entrada de guitarra ao vivo ainda não está disponível.
- DI de até 5 minutos e IR de até 2 segundos.
- NAM A2 e arquiteturas legadas suportadas pelo runtime são aceitas, mas arquivos
  históricos incomuns podem ser recusados pelo NeuralAmpModelerCore.
- Transferência direta para pedaleiras ainda não está implementada.
