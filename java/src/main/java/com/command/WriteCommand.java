package com.command;

/** Escribe texto en una posición del editor. */
public class WriteCommand implements Command {

    private final TextEditor editor;
    private final int position;   // - position: int
    private final String text;    // - text: String

    public WriteCommand(TextEditor editor, int position, String text) {
        this.editor = editor;
        this.position = position;
        this.text = text;
    }

    @Override
    public void execute() {
        editor.write(position, text);
    }

    @Override
    public void undo() {
        editor.delete(position, text.length());
    }

    @Override
    public void redo() {
        execute();
    }

    @Override
    public String toString() {
        return String.format("Write(pos=%d, text='%s')", position, text);
    }
}
