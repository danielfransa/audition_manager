"""Small runtime translation catalog for the desktop interface."""

SUPPORTED_LANGUAGES = {"pt_BR", "en"}
_language = "pt_BR"

_EN = {
    "Idioma:": "Language:",
    "Português": "Portuguese",
    "Nenhuma DI selecionada": "No DI selected",
    "Abrir DI WAV": "Open DI WAV",
    "Selecionar pasta de IRs": "Select IR folder",
    "Selecionar pasta de capturas NAM": "Select NAM capture folder",
    "Captura NAM (opcional):": "NAM capture (optional):",
    "Opcional: selecione uma captura antes do IR": "Optional: select a capture before the IR",
    "Buscar captura por nome ou caminho…": "Search capture by name or path…",
    "Somente capturas favoritas": "Favorite captures only",
    "Captura favorita": "Favorite capture",
    "Notas sobre a captura selecionada…": "Notes about the selected capture…",
    "Salvar notas da captura": "Save capture notes",
    "Exportar favoritos…": "Export favorites…",
    "Cancelar scan": "Cancel scan",
    "Buscar IR por nome ou caminho…": "Search IR by name or path…",
    "Somente favoritos": "Favorites only",
    "Todas as avaliações": "All ratings",
    "{value}+ estrelas": "{value}+ stars",
    "Saída padrão do sistema": "System default output",
    "Ganho de saída: {value} dB": "Output gain: {value} dB",
    "Ganho NAM: {value:+d} dB": "NAM gain: {value:+d} dB",
    "Ganho após a captura NAM e antes do IR": "Gain after the NAM capture and before the IR",
    "A2 Full — maior qualidade": "A2 Full — higher quality",
    "A2 Lite — processamento mais rápido": "A2 Lite — faster processing",
    "Bypass IR (B)": "Bypass IR (B)",
    "Bypass captura NAM (N)": "Bypass NAM capture (N)",
    "Processar e reproduzir": "Process and play",
    "Stop": "Stop",
    "IR em reprodução: nenhum": "Playing IR: none",
    "Pico: sem áudio": "Peak: no audio",
    "Pico do áudio processado, antes do ganho de saída": "Processed-audio peak before output gain",
    "Favorito (F)": "Favorite (F)",
    "Avaliação:": "Rating:",
    "Notas sobre o IR selecionado…": "Notes about the selected IR…",
    "Salvar notas": "Save notes",
    "Abra uma DI e selecione um IR.": "Open a DI and select an IR.",
    "Pasta de IRs": "IR folder",
    "Pasta de capturas NAM": "NAM capture folder",
    "Escolher esta pasta": "Choose this folder",
    "Exportar favoritos": "Export favorites",
    "Nome da nova pasta:": "New folder name:",
    "Incluir favoritos de:": "Include favorites from:",
    "Capturas": "Captures",
    "IRs": "IRs",
    "Avaliação: {stars}": "Rating: {stars}",
    "Sem áudio": "No audio",
    "Parado": "Stopped",
    "Reproduzindo": "Playing",
    "Pausado": "Paused",
    "Finalizado": "Finished",
    "Pause": "Pause",
    "Play": "Play",
    "Reprodução parada.": "Playback stopped.",
    "Player pronto.": "Player ready.",
    "Pause mantém a posição; Stop volta ao início.": "Pause keeps the position; Stop returns to the beginning.",
    "Favorito atualizado.": "Favorite updated.",
    "Favorito da captura atualizado.": "Capture favorite updated.",
    "Notas salvas.": "Notes saved.",
    "Notas da captura salvas.": "Capture notes saved.",
    "Exportação concluída": "Export complete",
    "Marque ao menos um IR ou captura como favorito.": "Mark at least one IR or capture as favorite.",
    "As categorias escolhidas não possuem favoritos para exportar.": "The selected categories have no favorites to export.",
    "Cadeia ativa: {chain}{suffix}": "Active chain: {chain}{suffix}",
    " — Bypass ativo: {items}": " — Active bypass: {items}",
    "Pico: {value:.1f} dBFS": "Peak: {value:.1f} dBFS",
    "DI: {name}": "DI: {name}",
    "{count} capturas NAM encontradas{skipped}.": "{count} NAM captures found{skipped}.",
    "; {count} inválidas ignoradas": "; {count} invalid files skipped",
    "; {count} inválidos ignorados": "; {count} invalid files skipped",
    "Cancelando scan anterior para abrir a nova pasta…": "Canceling the previous scan before opening the new folder…",
    "Escaneando IRs em {root}…": "Scanning IRs in {root}…",
    "Analisando IRs: {current}/{total}": "Analyzing IRs: {current}/{total}",
    "{count} IRs válidos encontrados{skipped}; selecione um IR.": "{count} valid IRs found{skipped}; select an IR.",
    "Scan cancelado; a biblioteca anterior foi mantida.": "Scan canceled; the previous library was kept.",
    "Cancelando scan…": "Canceling scan…",
    "Não foi possível listar saídas de áudio: {error}": "Could not list audio outputs: {error}",
    "Saída: {device}.": "Output: {device}.",
    "Não foi possível salvar as preferências: {error}": "Could not save preferences: {error}",
    "Avaliação da captura definida como {rating}/5.": "Capture rating set to {rating}/5.",
    "Avaliação definida como {rating}/5.": "Rating set to {rating}/5.",
    "Processando {stages}…": "Processing {stages}…",
    "Não foi possível concluir a operação.": "The operation could not be completed.",
    "Aguarde o processamento terminar antes de fechar.": "Wait for processing to finish before closing.",
    "Cancelando scan antes de fechar…": "Canceling scan before closing…",
    "{count} favoritos exportados ({captures} {capture_word}, {irs} IRs) para {directory}": "{count} favorites exported ({captures} {capture_word}, {irs} IRs) to {directory}",
    "captura": "capture",
    "capturas": "captures",
}


def set_language(language: str) -> None:
    global _language
    _language = language if language in SUPPORTED_LANGUAGES else "pt_BR"


def get_language() -> str:
    return _language


def tr(message: str, **values: object) -> str:
    translated = _EN.get(message, message) if _language == "en" else message
    return translated.format(**values) if values else translated
