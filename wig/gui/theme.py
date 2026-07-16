"""Colour palette and application-wide Qt stylesheet."""

from __future__ import annotations

# Cyber / dark palette shared by the GUI and the HTML report.
BG = "#0a0e14"
PANEL = "#111721"
CARD = "#161b22"
CARD_HI = "#1b222c"
BORDER = "#232b36"
BORDER_HI = "#2c3644"
TEXT = "#e6edf3"
MUTED = "#8b98a9"
ACCENT = "#28e0c8"       # teal
ACCENT2 = "#3d8bfd"      # electric blue

SEVERITY = {
    "Critical": "#ff4d5e",
    "High": "#ff8a3d",
    "Medium": "#ffd23d",
    "Low": "#4dc3ff",
    "Info": "#8b98a9",
    "Good": "#28e0c8",
}


def stylesheet() -> str:
    return f"""
    QWidget {{
        background: {BG};
        color: {TEXT};
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 13px;
    }}
    QLabel {{ background: transparent; }}

    /* ---- Sidebar ------------------------------------------------------- */
    #Sidebar {{ background: {PANEL}; border-right: 1px solid {BORDER}; }}
    #Brand {{ color: {TEXT}; font-size: 20px; font-weight: 800; }}
    #BrandAccent {{ color: {ACCENT}; }}
    #BrandSub {{ color: {MUTED}; font-size: 11px; letter-spacing: 1px; }}

    QPushButton#NavButton {{
        text-align: left; padding: 11px 16px; border: none;
        border-radius: 10px; color: {MUTED}; font-size: 13px; font-weight: 500;
        background: transparent;
    }}
    QPushButton#NavButton:hover {{ background: {CARD}; color: {TEXT}; }}
    QPushButton#NavButton:checked {{
        background: {CARD_HI}; color: {ACCENT}; font-weight: 700;
    }}

    /* ---- Top bar ------------------------------------------------------- */
    #TopBar {{ background: {BG}; border-bottom: 1px solid {BORDER}; }}
    #PageTitle {{ font-size: 20px; font-weight: 700; }}
    #PageSub {{ color: {MUTED}; font-size: 12px; }}

    QLineEdit#Search {{
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 9px;
        padding: 8px 12px; color: {TEXT}; selection-background-color: {ACCENT2};
    }}
    QLineEdit#Search:focus {{ border: 1px solid {ACCENT}; }}

    QPushButton#Action {{
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 9px;
        padding: 8px 16px; color: {TEXT}; font-weight: 600;
    }}
    QPushButton#Action:hover {{ border: 1px solid {ACCENT}; color: {ACCENT}; }}
    QPushButton#Primary {{
        background: {ACCENT}; border: none; border-radius: 9px;
        padding: 8px 18px; color: #05231e; font-weight: 700;
    }}
    QPushButton#Primary:hover {{ background: #43ecd6; }}
    QPushButton#Primary:disabled {{ background: {BORDER}; color: {MUTED}; }}

    /* ---- Cards --------------------------------------------------------- */
    #Card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}
    #CardTitle {{ color: {ACCENT2}; font-size: 11px; font-weight: 700;
                  letter-spacing: 1px; }}
    #CardNote {{ color: {MUTED}; font-size: 11px; font-style: italic; }}
    #KvKey {{ color: {MUTED}; }}
    #KvVal {{ color: {TEXT}; font-family: ui-monospace, Menlo, Consolas, monospace; }}

    /* ---- Stat tiles ---------------------------------------------------- */
    #Tile {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}
    #TileVal {{ font-size: 26px; font-weight: 800; color: {TEXT}; }}
    #TileLabel {{ color: {MUTED}; font-size: 11px; letter-spacing: .5px;
                  text-transform: uppercase; }}
    #TileIcon {{ font-size: 20px; }}

    /* ---- Tables -------------------------------------------------------- */
    QTableWidget {{
        background: {CARD}; border: none; gridline-color: transparent;
        selection-background-color: {CARD_HI}; selection-color: {ACCENT};
        font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px;
    }}
    QHeaderView::section {{
        background: {CARD}; color: {ACCENT}; border: none;
        border-bottom: 1px solid {BORDER}; padding: 8px 10px;
        font-size: 10px; font-weight: 700; text-transform: uppercase;
    }}
    QTableWidget::item {{ padding: 6px 10px; border-bottom: 1px solid #1c2430; }}

    /* ---- Findings ------------------------------------------------------ */
    #Finding {{ background: #12181f; border: 1px solid {BORDER}; border-radius: 9px; }}
    #FindingTitle {{ font-weight: 700; font-size: 13px; }}
    #FindingDetail {{ color: {MUTED}; }}
    #FindingRec {{ color: {ACCENT}; }}

    /* ---- Scrollbars ---------------------------------------------------- */
    QScrollArea {{ border: none; background: {BG}; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: {BORDER_HI}; border-radius: 5px;
                                   min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {MUTED}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
    QScrollBar::handle:horizontal {{ background: {BORDER_HI}; border-radius: 5px;
                                     min-width: 30px; }}

    /* ---- Status bar ---------------------------------------------------- */
    #StatusBar {{ background: {PANEL}; border-top: 1px solid {BORDER};
                  color: {MUTED}; font-size: 11px; }}
    #ModeLive {{ color: #39d98a; font-weight: 700; }}
    #ModeDemo {{ color: {ACCENT}; font-weight: 700; }}
    QProgressBar {{ background: {CARD}; border: none; border-radius: 3px;
                    height: 6px; text-align: center; }}
    QProgressBar::chunk {{ background: {ACCENT}; border-radius: 3px; }}
    """
