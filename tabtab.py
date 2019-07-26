def format(rows, headers=None, spacing=2, indent=1):
    if not rows: return
    R = len(rows)
    C = max(len(row) for row in rows)

    all_rows = [headers] + rows if headers else rows
    lengths = [[len(str(item)) for item in row] for row in all_rows]
    col_lengths = list(zip(*lengths))
    col_widths = list(map(max, col_lengths))

    spacer = ' ' * spacing
    row_format = spacer.join("{:>%d}" % w for w in col_widths)

    lines = []
    if headers:
        lines.append(row_format.format(*headers))
        lines.append(spacer.join('-' * w for w in col_widths))
    for row in rows:
        lines.append(row_format.format(*map(str, row)))

    indenter = ' ' * indent
    lines = [indenter + line for line in lines]
    return '\n'.join(lines)
