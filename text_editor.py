"""
Patrón Command - Editor de Texto
Receiver: TextEditor
"""


class TextEditor:
    """Receiver - El editor de texto que ejecuta las operaciones reales."""

    def __init__(self):
        self.clipboard: str = ""          # - clipboard: String
        self.text: list[str] = []         # - text: StringBuilder (list simula StringBuilder)

    # ── Operaciones del editor (+ public) ───────────────────────

    def write(self, position: int, text: str) -> None:
        """Inserta texto en la posición indicada."""
        content = self.getText()
        newContent = content[:position] + text + content[position:]
        self.text = list(newContent)

    def delete(self, start: int, length: int) -> str:
        """Elimina 'length' caracteres desde 'start'. Retorna el texto eliminado."""
        content = self.getText()
        deleted = content[start:start + length]
        newContent = content[:start] + content[start + length:]
        self.text = list(newContent)
        return deleted

    def copy(self, start: int, length: int) -> None:
        """Copia 'length' caracteres desde 'start' al clipboard."""
        content = self.getText()
        self.clipboard = content[start:start + length]

    def cut(self, start: int, length: int) -> str:
        """Corta 'length' caracteres desde 'start' al clipboard."""
        content = self.getText()
        self.clipboard = content[start:start + length]
        cutText = self.clipboard
        newContent = content[:start] + content[start + length:]
        self.text = list(newContent)
        return cutText

    def paste(self, position: int) -> None:
        """Pega el contenido del clipboard en la posición indicada."""
        if self.clipboard:
            self.write(position, self.clipboard)

    def getClipboard(self) -> str:
        return self.clipboard

    def getText(self) -> str:
        return "".join(self.text)
