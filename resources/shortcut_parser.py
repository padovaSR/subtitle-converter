# -*- coding: utf-8 -*-

from settings import MAIN_SETTINGS

import wx

def parse_shortcut(shortcut_str, command_id):
    """Convert a shortcut string (e.g. 'Ctrl+9' or 'Alt+F4') into wx.AcceleratorEntry tuples."""
    if not shortcut_str:
        return []

    parts = shortcut_str.split('+')
    flags = 0
    key = None

    for part in parts:
        p = part.strip().lower()
        if p == "ctrl":
            flags |= wx.ACCEL_CTRL
        elif p == "alt":
            flags |= wx.ACCEL_ALT
        elif p == "shift":
            flags |= wx.ACCEL_SHIFT
        else:
            if len(p) == 1 and p.isalpha():
                key = ord(p.upper())
            elif len(p) == 1 and p.isdigit():
                key = ord(p)
            elif p.startswith('f') and p[1:].isdigit():
                key = getattr(wx, f'WXK_F{p[1:]}', None)
            else:
                key = getattr(wx, f'WXK_{p.upper()}', None)

    if not key:
        return []

    entries = [(flags, key, command_id)]

    # Add numpad variant for digits
    if len(parts[-1]) == 1 and parts[-1].isdigit():
        numpad_key = getattr(wx, f'WXK_NUMPAD{parts[-1]}', None)
        if numpad_key:
            entries.append((flags, numpad_key, command_id))

    return entries

def update_accelerators(self):
    """Rebuild accelerator table and update menu labels based on MAIN_SETTINGS."""
    sKey = MAIN_SETTINGS["FrameShortcuts"]

    # Map shortcut names to menu objects
    shortcut_map = {
        "Undo": self.undo_menu,
        "Redo": self.redo_menu,        
        "Accept": self.accept_menu,
        "Ignore": self.ignore_menu,
        "ReplaceAll": self.replaceall_menu,
        "IgnoreAll": self.ignoreall_menu,
        "Add": self.add_menu,
        "Ok": self.ok_menu,
        "Cancel": self.cancel_menu,
        "Translate": self.translate_menu,
        "Replace": self.replace_menu,
        "Skip": self.skip_menu,
        "Next": self.next_menu,
        "Lock focus": self.lock_menu,
    }

    accel_entries = []

    for name, menu_item in shortcut_map.items():
        shortcut = sKey.get(name)
        if not shortcut:
            continue

        # Parse shortcut and add accelerators
        accel_entries += parse_shortcut(shortcut, menu_item.GetId())

        # Update menu label to show the key (e.g. "Next\tCtrl+9")
        base_label = menu_item.GetItemLabelText()  # text before tab
        menu_item.SetItemLabel(f"{base_label}\t{shortcut}")

    # Apply accelerator table
    self.SetAcceleratorTable(wx.AcceleratorTable(accel_entries))