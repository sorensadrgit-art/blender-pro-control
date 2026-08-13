ALLOWED_ENGINES = {'CYCLES', 'BLENDER_EEVEE_NEXT'}


def parse_render_args(args):
    if len(args) != 5:
        raise ValueError('expected frame width height engine output')
    frame_raw, width_raw, height_raw, engine, output = args
    frame = int(frame_raw)
    width = int(width_raw)
    height = int(height_raw)
    if frame < 1 or frame > 10_000_000:
        raise ValueError('frame out of range')
    if width < 1 or width > 16384 or height < 1 or height > 16384:
        raise ValueError('resolution out of range')
    if engine not in ALLOWED_ENGINES:
        raise ValueError('unsupported engine')
    if not isinstance(output, str) or not output:
        raise ValueError('output is required')
    return {
        'frame': frame,
        'width': width,
        'height': height,
        'engine': engine,
        'output': output,
    }
