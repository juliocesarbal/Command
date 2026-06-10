package com.command;

/** Pega el contenido del clipboard en una posición. */
public class PasteCommand implements Command {

    private final TextEditor editor;
    private final int position;   // - position: int
    private int pastedLen = 0;    // auxiliar para undo

    public PasteCommand(TextEditor editor, int position) {
        this.editor = editor;
        this.position = position;
    }

    @Override
    public void execute() {
        this.pastedLen = editor.getClipboard().length();
        editor.paste(position);
    }

    @Override
    public void undo() {
        if (pastedLen > 0) {
            editor.delete(position, pastedLen);
        }
    }

    @Override
    public void redo() {
        execute();
    }

    @Override
    public String toString() {
        return String.format("Paste(pos=%d)", position);
    }
}
