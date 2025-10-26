# -*- coding: utf-8 -*-
#
#


import srt
import re
import wx
import wx.dataview as dv

# ---------------------------------------------------------------------
# Model: DataViewIndexListModel to hold subtitles and provide GetAttr
# ---------------------------------------------------------------------
class SubtitlesModel(dv.DataViewIndexListModel):
    """
    A DataViewIndexListModel where each row is a subtitle object
    and we implement GetAttr to provide per-cell coloring.
    """
    def __init__(self, subs):
        # number of rows initially
        super().__init__(len(subs))
        self.subs = subs
        
        # Build a mapping from sub.index to row
        self.index_map = {sub.index: i for i, sub in enumerate(subs)}
        
        self.changed_rows = set()

    # number of columns
    def GetColumnCount(self):
        return 5

    # number of rows
    def GetCount(self):
        return len(self.subs)
    
    def rebuild_index_map(self):
        self.index_map = {sub.index: i for i, sub in enumerate(self.subs)}

    # get value displayed for row, col
    def GetValue(self, row, col):
        # Some wx versions pass DataViewItem instead of int row
        if not isinstance(row, int):
            try:
                row = self.GetRow(row)  # Convert DataViewItem → int row index
            except Exception:
                return ""

        sub = self.subs[row]
        if col == 0:
            return str(sub.index)
        elif col == 1:
            return srt.timedelta_to_srt_timestamp(sub.start)
        elif col == 2:
            return srt.timedelta_to_srt_timestamp(sub.end)
        elif col == 3:
            cps = self.calculate_cps(sub.content, sub.start, sub.end)
            return str(cps)
        elif col == 4:
            return sub.content.replace("\n", " | ")
        return ""
        
    # set value (we'll use it when updating content via model)
    def SetValue(self, row, col, value):
        sub = self.subs[row]
        if col == 3:
            # CPS is calculated; ignore direct sets
            return False
        elif col == 4:
            # user is updating content via SetValue (if you wire to edit)
            sub.content = value.replace(" | ", "\n")
            # notify that row changed (for CPS recalculation)
            self.RowChanged(row)
            return True
        return False
    
    # provide per-cell attributes (coloring)
    # Note: signature for DataViewIndexListModel's GetAttr is (self, row, col, attr)
    def GetAttr(self, row, col, attr):
        # Handle DataViewItem vs int row mismatch
        if not isinstance(row, int):
            try:
                row = self.GetRow(row)
            except Exception:
                return False
    
        # Only color the CPS column (assuming col == 3)
        if col == 3:
            sub = self.subs[row]
            cps = self.calculate_cps(sub.content, sub.start, sub.end)
    
            if cps > 18:
                # Clamp cps between 18–25
                capped_cps = min(cps, 25)
                # Normalize to 0–1 range
                t = (capped_cps - 18) / (25 - 18)
                # Optional: nonlinear easing (makes higher cps more intense)
                t = t ** 1.3
    
                # Interpolate between light red (255,230,230) and dark red (255,120,120)
                r = 255
                g = int(230 - (110 * t))
                b = int(230 - (110 * t))
    
                attr.SetBackgroundColour(wx.Colour(r, g, b))
                attr.SetColour(wx.Colour(100, 0, 0))
                return True
        return False
    
    # helper to notify model that a single row changed (refresh view)
    def row_updated(self, row):
        # tell the view that row changed
        try:
            self.RowChanged(row)
        except Exception:
            # older/newer wx versions might use different methods,
            # attempt NotifyRowsChanged fallback
            try:
                self.RowsChanged(row, row)
            except Exception:
                pass
            
    @staticmethod
    def calculate_cps(text, start, end):
        """
        Calculate CPS (characters per second) ignoring spaces and punctuation,
        in Aegisub style.
        
        Args:
            text (str): subtitle text
            start (datetime.timedelta): start time
            end (datetime.timedelta): end time
        
        Returns:
            int: CPS rounded to nearest integer
        """
        duration = (end - start).total_seconds()
        if duration <= 0:
            return 0
        # remove spaces, punctuation, newlines, only keep letters and digits
        text_only = re.sub(r"[^A-Za-z0-9]", "", text)
        cps = round(len(text_only) / duration)
        return cps
