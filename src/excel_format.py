"""Excel workbook styling for comparison export (openpyxl)."""

from __future__ import annotations

import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

# Readable headers for export (CSV keeps internal keys).
EXCEL_COLUMN_LABELS: dict[str, str] = {
    "Scenario": "Scenario",
    "rata_efectiva_taxe_procente": "Effective tax rate (%)",
    "venit_brut": "Gross income (RON)",
    "cheltuieli": "Deductible expenses (RON)",
    "venit_net_impozabil": "Net taxable income (RON)",
    "cas": "CAS (RON)",
    "cass": "CASS (RON)",
    "impozit": "Income tax (RON)",
    "total_taxe": "Total taxes (RON)",
    "venit_net": "Net income (RON)",
}


def prepare_export_dataframe_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with human-readable column titles for the sheet."""
    return df.rename(
        columns=lambda c: EXCEL_COLUMN_LABELS.get(
            c, c.replace("_", " ").title()
        )
    )


def format_comparison_worksheet(ws: Worksheet) -> None:
    """Bold header row, fill, wrap text, thin borders on all used cells, freeze panes."""
    max_row = ws.max_row
    max_col = ws.max_column
    if max_row < 1 or max_col < 1:
        return

    hair = Side(border_style="hair", color="FF9E9E9E")
    thin = Side(border_style="thin", color="FF7F7F7F")

    header_fill = PatternFill(fill_type="solid", fgColor="FF2F5597")
    header_font = Font(bold=True, color="FFFFFFFF", size=11)
    header_align = Alignment(
        horizontal="center", vertical="center", wrap_text=True
    )
    body_align = Alignment(vertical="center")

    for row_idx in range(1, max_row + 1):
        for col_idx in range(1, max_col + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            is_header = row_idx == 1
            top_edge = thin if row_idx == 1 else hair
            bottom_edge = thin if row_idx == max_row else hair
            left_edge = thin if col_idx == 1 else hair
            right_edge = thin if col_idx == max_col else hair
            cell.border = Border(
                left=left_edge,
                right=right_edge,
                top=top_edge,
                bottom=bottom_edge,
            )
            if is_header:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_align
            else:
                cell.alignment = body_align

    ws.row_dimensions[1].height = 36
    ws.freeze_panes = "A2"

    for col_idx in range(1, max_col + 1):
        letter = get_column_letter(col_idx)
        max_len = 10
        for row_idx in range(1, max_row + 1):
            val = ws.cell(row=row_idx, column=col_idx).value
            if val is not None:
                max_len = max(max_len, len(str(val)))
        ws.column_dimensions[letter].width = min(max_len + 2, 48)
