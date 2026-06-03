"""
Patrón Command - Editor de Texto
Receiver: TextEditor
"""


class TextEditor:
    """Receiver - El editor de texto que ejecuta las operaciones reales."""

    def __init__(self):
        self._text: list[str] = []  # Simula un StringBuilder
        self._clipboard: str = ""

    # ── Operaciones del editor ──────────────────────────────────

    def write(self, position: int, text: str) -> None:
        """Inserta texto en la posición indicada."""
        content = self.get_text()
        new_content = content[:position] + text + content[position:]
        self._text = list(new_content)

    def delete(self, start: int, length: int) -> str:
        """Elimina 'length' caracteres desde 'start'. Retorna el texto eliminado."""
        content = self.get_text()
        deleted = content[start:start + length]
        new_content = content[:start] + content[start + length:]
        self._text = list(new_content)
        return deleted

    def copy(self, start: int, length: int) -> None:
        """Copia 'length' caracteres desde 'start' al clipboard."""
        content = self.get_text()
        self._clipboard = content[start:start + length]

    def cut(self, start: int, length: int) -> str:
        """Corta 'length' caracteres desde 'start' al clipboard. Retorna el texto cortado."""
        content = self.get_text()
        self._clipboard = content[start:start + length]
        cut_text = self._clipboard
        new_content = content[:start] + content[start + length:]
        self._text = list(new_content)
        return cut_text

    def paste(self, position: int) -> None:
        """Pega el contenido del clipboard en la posición indicada."""
        if self._clipboard:
            self.write(position, self._clipboard)

    # ── Getters ─────────────────────────────────────────────────

    def get_text(self) -> str:
        return "".join(self._text)

    def get_clipboard(self) -> str:
        return self._clipboard

    def set_clipboard(self, text: str) -> None:
        self._clipboard = text
