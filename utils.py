import io
import cairosvg
from PIL import Image
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y, GROUND_HEIGHT


def svg_to_surface(svg_path, width=None, height=None, scale_mode='contain'):
    """Render an SVG file to a Pygame Surface while preserving aspect ratio.

    If `width` and/or `height` are provided this function will scale the SVG
    so it fits inside the requested box while keeping its aspect ratio.
    """
    # Try to read intrinsic SVG size from viewBox or width/height attributes
    def _intrinsic_size(path):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(path)
            root = tree.getroot()
        except Exception:
            return None

        viewbox = root.get('viewBox') or root.get('viewbox')
        if viewbox:
            parts = viewbox.strip().split()
            if len(parts) == 4:
                try:
                    w = float(parts[2])
                    h = float(parts[3])
                    return w, h
                except Exception:
                    pass

        w_attr = root.get('width')
        h_attr = root.get('height')
        def _parse_dim(val):
            if not val:
                return None
            import re
            m = re.match(r'([0-9.+-eE]+)', val)
            if m:
                try:
                    return float(m.group(1))
                except Exception:
                    return None
            return None

        w = _parse_dim(w_attr)
        h = _parse_dim(h_attr)
        if w and h:
            return w, h
        return None

    intrinsic = _intrinsic_size(svg_path)
    out_w, out_h = None, None
    if intrinsic:
        iw, ih = intrinsic
        if width and height:
            if scale_mode == 'contain':
                # scale to fit inside box
                scale = min(width / iw, height / ih)
            elif scale_mode == 'cover':
                # scale to cover the box (may overflow), we'll crop after rasterising
                scale = max(width / iw, height / ih)
            else:
                # 'fill' or unknown: stretch to exact dimensions
                scale = None

            if scale is None:
                out_w = width
                out_h = height
            else:
                out_w = int(round(iw * scale))
                out_h = int(round(ih * scale))
        elif width:
            scale = width / iw
            out_w = int(round(iw * scale))
            out_h = int(round(ih * scale))
        elif height:
            scale = height / ih
            out_w = int(round(iw * scale))
            out_h = int(round(ih * scale))
    else:
        out_w = width
        out_h = height

    png_bytes = cairosvg.svg2png(url=svg_path,
                                output_width=out_w,
                                output_height=out_h)

    # Write a debug PNG to disk so we can inspect the rasterisation result
    try:
        with open('assets/grass_debug.png', 'wb') as f:
            f.write(png_bytes)
    except Exception:
        pass

    # Load PNG bytes with Pillow and convert to a pygame Surface.
    buf = io.BytesIO(png_bytes)
    buf.seek(0)
    img = Image.open(buf).convert("RGBA")
    # If we rasterised larger than the requested box and scale_mode requests
    # covering, crop the image to the requested size. For ground we prefer
    # bottom alignment so the crop keeps the lower portion of the image.
    if width and height and scale_mode == 'cover':
        iw, ih = img.size
        crop_left = 0
        crop_top = 0
        crop_right = iw
        crop_bottom = ih
        if iw > width:
            # center horizontally
            crop_left = (iw - width) // 2
            crop_right = crop_left + width
        if ih > height:
            # bottom-align vertically
            crop_top = ih - height
            crop_bottom = ih
        if (crop_left, crop_top, crop_right, crop_bottom) != (0, 0, iw, ih):
            img = img.crop((crop_left, crop_top, crop_right, crop_bottom))
    data = img.tobytes()
    size = img.size
    surface = pygame.image.frombuffer(data, size, 'RGBA')
    return surface.convert_alpha()
