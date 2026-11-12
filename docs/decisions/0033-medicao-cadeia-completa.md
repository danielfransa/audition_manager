# 0033 — Medir a cadeia completa para comparação justa

## Contexto

A compensação atual usa somente o loudness fornecido pelo NAM. Ela não mede o
efeito do IR nem o conteúdo da DI e, portanto, é uma estimativa útil, mas não a
comparação final mais justa.

## Decisão

Na próxima etapa, medir loudness integrado na saída completa selecionada, antes
da proteção final de pico, usando gating baseado em ITU-R BS.1770/EBU R128. O
alvo será -18 LUFS e a correção permanecerá limitada entre -24 e +12 dB.

Persistir o resultado por identidade da DI, NAM, IR, modo Full/Lite, versão do
algoritmo e alvo. Não usar pico como medida principal. Se a medição não for
válida, manter 0 dB e explicar o motivo; qualquer fallback deverá ser identificado.

## Consequências

- Combinações diferentes podem ter compensações diferentes.
- Alterações nos arquivos ou no algoritmo invalidam o cache.
- Será necessário separar processamento sem limite, medição, ganho e proteção
  final para não medir um sinal já limitado.
- O release seguinte terá um changelog próprio em
  `docs/releases/v0.2.0-alpha.md`, atualizado até a publicação.
