def timestamp_to_seconds(ts):
    m, s = ts.split(":")
    s, ms = s.split(".")
    return int(m) * 60 + int(s) + int(ms) // 1000
