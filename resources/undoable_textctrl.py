import wx

class UndoableTextCtrl(wx.TextCtrl):
    """A TextCtrl with manual Undo/Redo stack for small text edits."""

    def __init__(self, parent, id=wx.ID_ANY, value="", style=0):
        super().__init__(parent, id, value=value,
                         style=style | wx.TE_MULTILINE|wx.TE_CENTER|wx.TE_NO_VSCROLL|wx.TE_NOHIDESEL|wx.TE_RICH2)
        self.undo_stack = []
        self.redo_stack = []
        self.Bind(wx.EVT_TEXT, self.on_text)

    def on_text(self, event):
        """Save the previous value to the undo stack whenever text changes."""
        if not hasattr(self, "_block"):
            value = self.GetValue()
            if not hasattr(self, "_last_value") or value != self._last_value:
                self.undo_stack.append(value)
                self._last_value = value
                self.redo_stack.clear()
        event.Skip()

    def undo(self):
        if len(self.undo_stack) > 1:
            self._block = True
            current = self.undo_stack.pop()
            self.redo_stack.append(current)
            prev = self.undo_stack[-1]
            self.ChangeValue(prev)
            del self._block
        else:
            wx.Bell()

    def redo(self):
        if self.redo_stack:
            self._block = True
            next_val = self.redo_stack.pop()
            self.undo_stack.append(next_val)
            self.ChangeValue(next_val)
            del self._block
        else:
            wx.Bell()