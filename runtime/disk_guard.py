import shutil


def classify_free_percent(free_percent):
    value = float(free_percent)
    if value < 5.0:
        return 'emergency'
    if value < 10.0:
        return 'reject'
    if value < 15.0:
        return 'warn'
    return 'ok'


def disk_status(path='/srv/blender-pro'):
    usage = shutil.disk_usage(path)
    free_percent = usage.free * 100.0 / usage.total
    return {
        'path': path,
        'free_bytes': usage.free,
        'total_bytes': usage.total,
        'free_percent': free_percent,
        'status': classify_free_percent(free_percent),
    }
