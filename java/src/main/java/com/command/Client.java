package com.command;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import javax.swing.border.TitledBorder;
import javax.swing.text.BadLocationException;
import javax.swing.text.DocumentFilter;
import javax.swing.text.AbstractDocument;
import java.awt.*;
import java.awt.event.KeyEvent;

/**
 * Patrón Command — Cliente (Interfaz Gráfica con Swing)
 * Client: copy, cut, delete, paste, write — tal cual el diagrama UML.
 */
public class Client {

    // ── colores (Catppuccin Mocha) ──────────────────────────────
    static final Color BG       = Color.decode("#1e1e2e");
    static final Color SURFACE  = Color.decode("#313244");
    static final Color OVERLAY  = Color.decode("#45475a");
    static final Color TEXT_CLR = Color.decode("#cdd6f4");
    static final Color SUBTEXT  = Color.decode("#a6adc8");
    static final Color BLUE     = Color.decode("#89b4fa");
    static final Color GREEN    = Color.decode("#a6e3a1");
    static final Color YELLOW   = Color.decode("#f9e2af");
    static final Color PINK     = Color.decode("#f5c2e7");
    static final Color TEAL     = Color.decode("#94e2d5");
    static final Color RED      = Color.decode("#f38ba8");
    static final Color MAUVE    = Color.decode("#cba6f7");

    private final TextEditor editor = new TextEditor();
    private final TextEditorInvoker invoker = new TextEditorInvoker();
    private boolean syncing = false;

    private JFrame frame;
    private JTextPane textPane;
    private JLabel clipLabel;
    private DefaultListModel<String> historyModel;
    private JList<String> historyList;
    private JLabel logLabel;
    private JLabel statusLabel;

    public Client() {
        buildUI();
        bindShortcuts();
    }

    // ═══════════════════════════════════════════════════════════
    //  UI
    // ═══════════════════════════════════════════════════════════

    private void buildUI() {
        frame = new JFrame("Patrón Command — Editor de Texto");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(900, 640);
        frame.setMinimumSize(new Dimension(750, 550));
        frame.getContentPane().setBackground(BG);
        frame.setLayout(new BorderLayout());

        // ── Header ──
        JPanel header = new JPanel(new FlowLayout(FlowLayout.LEFT, 16, 8));
        header.setBackground(BG);
        JLabel title = new JLabel("✏  Editor de Texto — Patrón Command");
        title.setFont(new Font("Segoe UI", Font.BOLD, 15));
        title.setForeground(TEXT_CLR);
        JLabel sub = new JLabel("Escribe · Selecciona · Usa botones o atajos");
        sub.setFont(new Font("Segoe UI", Font.PLAIN, 9));
        sub.setForeground(SUBTEXT);
        header.add(title);
        header.add(sub);

        // ── Toolbar ──
        JPanel toolbar = new JPanel(new FlowLayout(FlowLayout.LEFT, 4, 6));
        toolbar.setBackground(SURFACE);
        toolbar.add(button("📝 Write", BLUE, BG, e -> write()));
        toolbar.add(button("🗑 Delete (Del)", RED, Color.WHITE, e -> delete()));
        toolbar.add(button("📋 Copy (Ctrl+C)", MAUVE, BG, e -> copy()));
        toolbar.add(button("✂ Cut (Ctrl+X)", YELLOW, BG, e -> cut()));
        toolbar.add(button("📌 Paste (Ctrl+V)", GREEN, BG, e -> paste()));

        JPanel sep = new JPanel();
        sep.setPreferredSize(new Dimension(2, 28));
        sep.setBackground(OVERLAY);
        toolbar.add(sep);

        toolbar.add(button("⬅ Undo (Ctrl+Z)", YELLOW, BG, e -> onUndo()));
        toolbar.add(button("➡ Redo (Ctrl+Y)", TEAL, BG, e -> onRedo()));

        JPanel north = new JPanel(new BorderLayout());
        north.setBackground(BG);
        north.setBorder(new EmptyBorder(10, 20, 0, 20));
        north.add(header, BorderLayout.NORTH);
        north.add(toolbar, BorderLayout.SOUTH);
        frame.add(north, BorderLayout.NORTH);

        // ── Body (split) ──
        textPane = new JTextPane();
        textPane.setFont(new Font("Consolas", Font.PLAIN, 13));
        textPane.setBackground(SURFACE);
        textPane.setForeground(TEXT_CLR);
        textPane.setCaretColor(TEAL);
        textPane.setSelectionColor(BLUE);
        textPane.setSelectedTextColor(BG);
        textPane.setBorder(new EmptyBorder(10, 12, 10, 12));
        JScrollPane editorScroll = new JScrollPane(textPane);
        editorScroll.setBorder(titled(" Editor "));
        editorScroll.getViewport().setBackground(SURFACE);

        // Right panel
        JPanel right = new JPanel();
        right.setLayout(new BoxLayout(right, BoxLayout.Y_AXIS));
        right.setBackground(BG);

        // Clipboard
        clipLabel = new JLabel("(vacío)");
        clipLabel.setFont(new Font("Consolas", Font.PLAIN, 10));
        clipLabel.setForeground(PINK);
        clipLabel.setOpaque(true);
        clipLabel.setBackground(SURFACE);
        clipLabel.setBorder(new EmptyBorder(6, 8, 6, 8));
        JPanel clipFrame = wrap(clipLabel, " 📋 Clipboard ");
        clipFrame.setMaximumSize(new Dimension(Integer.MAX_VALUE, 70));

        // History
        historyModel = new DefaultListModel<>();
        historyList = new JList<>(historyModel);
        historyList.setFont(new Font("Consolas", Font.PLAIN, 11));
        historyList.setBackground(SURFACE);
        historyList.setForeground(GREEN);
        historyList.setSelectionBackground(OVERLAY);
        JScrollPane histScroll = new JScrollPane(historyList);
        histScroll.setBorder(titled(" 📜 Historial de Comandos "));
        histScroll.getViewport().setBackground(SURFACE);

        // Log
        logLabel = new JLabel("Listo. Escribe algo en el editor.");
        logLabel.setFont(new Font("Segoe UI", Font.PLAIN, 9));
        logLabel.setForeground(TEAL);
        logLabel.setOpaque(true);
        logLabel.setBackground(SURFACE);
        logLabel.setBorder(new EmptyBorder(6, 8, 6, 8));
        JPanel logFrame = wrap(logLabel, " 💬 Log ");
        logFrame.setMaximumSize(new Dimension(Integer.MAX_VALUE, 70));

        right.add(clipFrame);
        right.add(Box.createVerticalStrut(6));
        right.add(histScroll);
        right.add(Box.createVerticalStrut(6));
        right.add(logFrame);

        JSplitPane body = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, editorScroll, right);
        body.setDividerLocation(540);
        body.setResizeWeight(0.6);
        body.setBackground(OVERLAY);
        body.setBorder(new EmptyBorder(10, 20, 10, 20));
        frame.add(body, BorderLayout.CENTER);

        // Status bar
        statusLabel = new JLabel("Pos: 0  |  Sel: ninguna  |  Chars: 0");
        statusLabel.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        statusLabel.setForeground(SUBTEXT);
        statusLabel.setOpaque(true);
        statusLabel.setBackground(OVERLAY);
        statusLabel.setBorder(new EmptyBorder(3, 12, 3, 12));
        frame.add(statusLabel, BorderLayout.SOUTH);
    }

    private JButton button(String text, Color bg, Color fg, java.awt.event.ActionListener action) {
        JButton b = new JButton(text);
        b.setFont(new Font("Segoe UI", Font.BOLD, 11));
        b.setBackground(bg);
        b.setForeground(fg);
        b.setFocusPainted(false);
        b.setBorder(new EmptyBorder(7, 12, 7, 12));
        b.addActionListener(action);
        return b;
    }

    private JPanel wrap(JComponent inner, String title) {
        JPanel p = new JPanel(new BorderLayout());
        p.setBackground(BG);
        p.setBorder(titled(title));
        p.add(inner, BorderLayout.CENTER);
        return p;
    }

    private TitledBorder titled(String title) {
        TitledBorder tb = BorderFactory.createTitledBorder(
                new LineBorder(OVERLAY, 1), title);
        tb.setTitleFont(new Font("Segoe UI", Font.BOLD, 10));
        tb.setTitleColor(BLUE);
        return tb;
    }

    // ═══════════════════════════════════════════════════════════
    //  Shortcuts — interceptamos toda la edición vía DocumentFilter
    //  desactivado: editamos el modelo a mano y resincronizamos.
    // ═══════════════════════════════════════════════════════════

    private void bindShortcuts() {
        // Bloquea edición directa del JTextPane; toda mutación pasa por comandos.
        ((AbstractDocument) textPane.getDocument()).setDocumentFilter(new DocumentFilter() {
            @Override public void insertString(FilterBypass fb, int off, String s, javax.swing.text.AttributeSet a) {
                if (syncing) { try { fb.insertString(off, s, a); } catch (BadLocationException ignored) {} }
            }
            @Override public void replace(FilterBypass fb, int off, int len, String s, javax.swing.text.AttributeSet a) {
                if (syncing) { try { fb.replace(off, len, s, a); } catch (BadLocationException ignored) {} }
            }
            @Override public void remove(FilterBypass fb, int off, int len) {
                if (syncing) { try { fb.remove(off, len); } catch (BadLocationException ignored) {} }
            }
        });

        textPane.addKeyListener(new java.awt.event.KeyAdapter() {
            @Override public void keyPressed(KeyEvent e) { onKeyPressed(e); }
            @Override public void keyTyped(KeyEvent e) { onKeyTyped(e); }
        });

        textPane.addCaretListener(e -> updateStatus());
    }

    // ── Helpers ──────────────────────────────────────────────────

    /** Selección actual como [start, length], o null si no hay. */
    private int[] selectionRange() {
        int s = textPane.getSelectionStart();
        int e = textPane.getSelectionEnd();
        if (e > s) return new int[]{s, e - s};
        return null;
    }

    private int cursorPos() {
        return textPane.getCaretPosition();
    }

    private void log(String msg) {
        logLabel.setText(msg);
    }

    private void syncWidgetFromEditor() {
        syncing = true;
        int caret = textPane.getCaretPosition();
        textPane.setText(editor.getText());
        int len = editor.getText().length();
        textPane.setCaretPosition(Math.min(caret, len));
        syncing = false;
    }

    private void setCursorAt(int pos) {
        int len = editor.getText().length();
        textPane.setCaretPosition(Math.max(0, Math.min(pos, len)));
    }

    private void refreshPanels() {
        String clip = editor.getClipboard();
        clipLabel.setText(clip.isEmpty() ? "(vacío)" : clip);

        historyModel.clear();
        int i = 1;
        for (Command cmd : invoker.getHistory()) {
            historyModel.addElement(" " + (i++) + ". " + cmd);
        }
        if (!invoker.getRedoStack().isEmpty()) {
            historyModel.addElement(" ─── redo pendiente ───");
            for (Command cmd : invoker.getRedoStack()) {  // Deque itera desde el tope
                historyModel.addElement(" ↪ " + cmd);
            }
        }
        if (!historyModel.isEmpty()) {
            historyList.ensureIndexIsVisible(historyModel.size() - 1);
        }
        updateStatus();
    }

    private void updateStatus() {
        String content = editor.getText();
        int pos = cursorPos();
        int[] sel = selectionRange();
        String selText = (sel != null)
                ? String.format("Sel: [%d:%d] (%d chars)", sel[0], sel[0] + sel[1], sel[1])
                : "Sel: ninguna";
        statusLabel.setText(String.format(
                "Pos: %d  |  %s  |  Chars: %d  |  Undo: %d  Redo: %d",
                pos, selText, content.length(),
                invoker.getHistory().size(), invoker.getRedoStack().size()));
    }

    // ── Handlers de teclas ───────────────────────────────────────

    private void onKeyTyped(KeyEvent e) {
        if (syncing) return;
        if ((e.getModifiersEx() & KeyEvent.CTRL_DOWN_MASK) != 0) return;
        char ch = e.getKeyChar();
        if (ch == KeyEvent.CHAR_UNDEFINED || ch < 32 || ch == 127) return;

        int pos;
        int[] sel = selectionRange();
        if (sel != null) {
            invoker.executeCommand(new DeleteCommand(editor, sel[0], sel[1]));
            pos = sel[0];
        } else {
            pos = cursorPos();
        }
        invoker.executeCommand(new WriteCommand(editor, pos, String.valueOf(ch)));
        syncWidgetFromEditor();
        setCursorAt(pos + 1);
        refreshPanels();
        log("✅ Write: '" + ch + "' en pos " + pos);
        e.consume();
    }

    private void onKeyPressed(KeyEvent e) {
        if (syncing) return;
        int code = e.getKeyCode();
        boolean ctrl = (e.getModifiersEx() & KeyEvent.CTRL_DOWN_MASK) != 0;

        if (ctrl) {
            switch (code) {
                case KeyEvent.VK_C: copy();    e.consume(); return;
                case KeyEvent.VK_X: cut();     e.consume(); return;
                case KeyEvent.VK_V: paste();   e.consume(); return;
                case KeyEvent.VK_Z: onUndo();  e.consume(); return;
                case KeyEvent.VK_Y: onRedo();  e.consume(); return;
                default: return;
            }
        }
        if (code == KeyEvent.VK_BACK_SPACE) { onBackspace(); e.consume(); }
        else if (code == KeyEvent.VK_DELETE) { onDeleteKey(); e.consume(); }
    }

    private void onBackspace() {
        int start, length;
        int[] sel = selectionRange();
        if (sel != null) {
            start = sel[0]; length = sel[1];
        } else {
            int pos = cursorPos();
            if (pos == 0) return;
            start = pos - 1; length = 1;
        }
        invoker.executeCommand(new DeleteCommand(editor, start, length));
        syncWidgetFromEditor();
        setCursorAt(start);
        refreshPanels();
        log("🗑 Delete: " + length + " char(s) desde pos " + start);
    }

    private void onDeleteKey() {
        int start, length;
        int[] sel = selectionRange();
        if (sel != null) {
            start = sel[0]; length = sel[1];
        } else {
            int pos = cursorPos();
            if (pos >= editor.getText().length()) return;
            start = pos; length = 1;
        }
        invoker.executeCommand(new DeleteCommand(editor, start, length));
        syncWidgetFromEditor();
        setCursorAt(start);
        refreshPanels();
        log("🗑 Delete: " + length + " char(s) desde pos " + start);
    }

    // ═══════════════════════════════════════════════════════════
    //  Métodos públicos del Client (tal cual el diagrama)
    // ═══════════════════════════════════════════════════════════

    public void write() {
        refreshPanels();
        log("✅ Write: contenido sincronizado");
    }

    public void delete() {
        int[] sel = selectionRange();
        if (sel == null) {
            JOptionPane.showMessageDialog(frame, "Selecciona texto para borrar.", "Delete", JOptionPane.INFORMATION_MESSAGE);
            return;
        }
        invoker.executeCommand(new DeleteCommand(editor, sel[0], sel[1]));
        syncWidgetFromEditor();
        setCursorAt(sel[0]);
        refreshPanels();
        log("🗑 Delete: " + sel[1] + " chars desde pos " + sel[0]);
    }

    public void copy() {
        int[] sel = selectionRange();
        if (sel == null) { log("⚠ Selecciona texto para copiar"); return; }
        invoker.executeCommand(new CopyCommand(editor, sel[0], sel[1]));
        refreshPanels();
        log("📋 Copy: '" + editor.getClipboard() + "'");
    }

    public void cut() {
        int[] sel = selectionRange();
        if (sel == null) { log("⚠ Selecciona texto para cortar"); return; }
        invoker.executeCommand(new CutCommand(editor, sel[0], sel[1]));
        syncWidgetFromEditor();
        setCursorAt(sel[0]);
        refreshPanels();
        log("✂ Cut: '" + editor.getClipboard() + "'");
    }

    public void paste() {
        String clip = editor.getClipboard();
        if (clip.isEmpty()) { log("⚠ Clipboard vacío, nada que pegar"); return; }

        int pos;
        int[] sel = selectionRange();
        if (sel != null) {
            invoker.executeCommand(new DeleteCommand(editor, sel[0], sel[1]));
            pos = sel[0];
        } else {
            pos = cursorPos();
        }
        invoker.executeCommand(new PasteCommand(editor, pos));
        syncWidgetFromEditor();
        setCursorAt(pos + clip.length());
        refreshPanels();
        log("📌 Paste: '" + clip + "' en pos " + pos);
    }

    private void onUndo() {
        if (invoker.undoLastCommand()) {
            syncWidgetFromEditor();
            refreshPanels();
            log("⬅ Undo ejecutado");
        } else {
            log("⚠ No hay comandos para deshacer");
        }
    }

    private void onRedo() {
        if (invoker.redoLastCommand()) {
            syncWidgetFromEditor();
            refreshPanels();
            log("➡ Redo ejecutado");
        } else {
            log("⚠ No hay comandos para rehacer");
        }
    }

    // ═══════════════════════════════════════════════════════════
    //  Ejecución
    // ═══════════════════════════════════════════════════════════

    public void run() {
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
        textPane.requestFocusInWindow();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new Client().run());
    }
}
