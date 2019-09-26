from datetime import datetime, timedelta

def linear(duration):
    def f(payment_start):
        payment_end = payment_start + duration
        def total(interval_start, interval_end):
            overlap_start = max(payment_start, interval_start)
            overlap_end = min(payment_end, interval_end)
            overlap_amt = overlap_end - overlap_start
            return max(0.0, overlap_amt / duration)
        return total
    return f

def point(payment_start):
    def total(interval_start, interval_end):
        if interval_start <= payment_start <= interval_end:
            return 1.0
        else:
            return 0.0

def of_string(s):
    if s == 'point':
        return point
    parts = s.split()
    if s[0] == 'linear':
        duration = timedelta(**{unit: int(qty) for qty, unit in zip(parts[1::2], parts[2::2])})
        return linear(duration)
