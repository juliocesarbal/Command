package com.command;

/**
 * Patrón Command - Editor de Texto
 * Receiver: TextEditor
 */
public class TextEditor {

    private String clipboard = "";          // - clipboard: String
    private final StringBuilder text = new StringBuilder();  // - text: StringBuilder

    // ── Operaciones del editor (+ public) ───────────────────────

    /** Inserta texto en la posición indicada. */
    public void write(int position, String text) {
        this.text.insert(position, text);
    }

    /** Elimina 'length' caracteres desde 'start'. Retorna el texto eliminado. */
    public String delete(int start, int length) {
        String deleted = this.text.substring(start, start + length);
        this.text.delete(start, start + length);
        return deleted;
    }

    /** Copia 'length' caracteres desde 'start' al clipboard. */
    public void copy(int start, int length) {
        this.clipboard = this.text.substring(start, start + length);
    }

    /** Corta 'length' caracteres desde 'start' al clipboard. */
    public String cut(int start, int length) {
        this.clipboard = this.text.substring(start, start + length);
        String cutText = this.clipboard;
        this.text.delete(start, start + length);
        return cutText;
    }

    /** Pega el contenido del clipboard en la posición indicada. */
    public void paste(int position) {
        if (!this.clipboard.isEmpty()) {
            write(position, this.clipboard);
        }
    }

    public String getClipboard() {
        return this.clipboard;
    }

    public String getText() {
        return this.text.toString();
    }
}
