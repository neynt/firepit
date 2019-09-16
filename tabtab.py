"""Tabular output utilities."""
import numpy as np
from prompt_toolkit import print_formatted_text, HTML

def smart_str(item):
    """Convert to string, with smart handling for certain types."""
    plain = str(item)
    formatted = str(item)
    if type(item) in [float, np.float64]:
        for decimals in [0, 2, 3, 4, 5, 6, 7, 8]:
            s = ('{:.%df}' % decimals).format(item)
            item_ = float(s)
            if abs((item - item_) / item) < 0.00001:
                plain = s
                break

        if item < 0:
            formatted = f'<ansired>{plain}</ansired>'
        elif item > 0:
            formatted = f'<ansigreen>{plain}</ansigreen>'
    return plain, formatted

def format_row(col_widths, spacer, values):
    parts = []
    for col_width, (plain, formatted) in zip(col_widths, values):
        extra_space = col_width - len(plain)
        parts.append(' ' * extra_space + formatted)
    return spacer.join(parts)

def unformatted(items):
    return [(x, x) for x in items]

def print_table(rows, headers=None, spacing=2, indent=1):
    if not rows:
        return ''
    R = len(rows)
    C = max(len(row) for row in rows)

    rows = [[smart_str(item) for item in row] for row in rows]
    headers = [(h, f'<bold>{h}</bold>') for h in headers]
    all_rows = [headers] + rows if headers else rows
    lengths = [[len(plain) for plain, _ in row] for row in all_rows]
    col_lengths = list(zip(*lengths))
    col_widths = list(map(max, col_lengths))

    indenter = ' ' * indent
    spacer = ' ' * spacing
    row_format = spacer.join("{:>%d}" % w for w in col_widths)

    lines = []
    if headers:
        print_formatted_text(HTML(indenter + format_row(col_widths, spacer, headers)))
        print_formatted_text(HTML(indenter + format_row(col_widths, spacer, unformatted(['─' * w for w in col_widths]))))

    for row in rows:
        print_formatted_text(HTML(indenter + format_row(col_widths, spacer, row)))

def print_dataframe(df, headers=None, **kwargs):
    df = df.reset_index()
    headers = headers or list(df.columns)
    np_list = df.to_numpy().tolist()
    return print_table(np_list, headers=headers, **kwargs)
