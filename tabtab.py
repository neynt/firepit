"""Tabular output utilities."""
# >   >   tabtab

from prompt_toolkit import print_formatted_text, HTML
import pandas as pd

import lib

def format_row(col_widths, spacer, values):
    parts = []
    for col_width, (plain, formatted) in zip(col_widths, values):
        extra_space = col_width - len(plain)
        parts.append(' ' * extra_space + formatted)
    return spacer.join(parts)

def unformatted(items):
    return [(x, x) for x in items]

def print_table(rows, headers=None, spacing=2, indent=1):
    rows = [[lib.format_str(item) for item in row] for row in rows]
    headers = [(h, f'<bold>{h}</bold>') for h in headers]
    all_rows = [headers] + rows if headers else rows
    lengths = [[len(plain) for plain, _ in row] for row in all_rows]
    col_lengths = list(zip(*lengths))
    col_widths = list(map(max, col_lengths))

    indenter = ' ' * indent
    spacer = ' ' * spacing

    if headers:
        underlines = unformatted(['─' * w for w in col_widths])
        print_formatted_text(HTML(indenter + format_row(col_widths, spacer, headers)))
        print_formatted_text(HTML(indenter + format_row(col_widths, spacer, underlines)))

    for row in rows:
        print_formatted_text(HTML(indenter + format_row(col_widths, spacer, row)))

def print_dataframe(df, headers=None, drop_index=False, **kwargs):
    df = df.reset_index(drop=drop_index)
    headers = headers or list(df.columns)
    np_list = df.to_numpy().tolist()
    return print_table(np_list, headers=headers, **kwargs)
