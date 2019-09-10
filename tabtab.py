"""Tabular output utilities."""
import numpy as np

def smart_str(item):
    """Convert to string, with smart handling for certain types."""
    if type(item) in [float, np.float64]:
        for decimals in [2, 3, 4, 5, 6, 7, 8]:
            s = ('{:.%df}' % decimals).format(item)
            item_ = float(s)
            if abs((item - item_) / item) < 0.00001:
                return s
    return str(item)

def format(rows, headers=None, spacing=2, indent=1):
    if not rows:
        return ''
    R = len(rows)
    C = max(len(row) for row in rows)

    rows = [[smart_str(item) for item in row] for row in rows]
    all_rows = [headers] + rows if headers else rows
    lengths = [[len(item) for item in row] for row in all_rows]
    col_lengths = list(zip(*lengths))
    col_widths = list(map(max, col_lengths))

    spacer = ' ' * spacing
    row_format = spacer.join("{:>%d}" % w for w in col_widths)

    lines = []
    if headers:
        lines.append(row_format.format(*headers))
        lines.append(spacer.join('-' * w for w in col_widths))
    for row in rows:
        lines.append(row_format.format(*row))

    indenter = ' ' * indent
    lines = [indenter + line for line in lines]
    return '\n'.join(lines)

def format_dataframe(df, **kwargs):
    df = df.reset_index()
    headers = list(df.columns)
    return format(df.to_numpy().tolist(), headers=headers, **kwargs)
