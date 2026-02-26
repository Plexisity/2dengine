# Main processor for drawing on the screen
import pygame
import sys
import io
import cairosvg
from PIL import Image

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

#Ground level
GROUND_Y = 500
GROUND_HEIGHT = 100


# utility --------------------------------------------------
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


# Create display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Engine")
clock = pygame.time.Clock()

# Cube class
class Cube:
    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        # jump physics
        # we only need an instantaneous upward impulse and constant gravity
        self.jumping = False
        # initial jump impulse (negative = upwards)
        self.jump_speed = -15.0               # much stronger jump
        # gravity acceleration per frame
        self.gravity = 0.5                    # pull back down
    
    def handle_input(self, keys):
        """Handle keyboard input for cube movement"""
        self.velocity_x = 0
        # do not touch self.velocity_y; let physics handle vertical motion

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed

        # begin jump with a strong upward impulse if on the ground
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground():
            self.jumping = True
            self.velocity_y = self.jump_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            # simple manual down control (could be removed)
            self.velocity_y = self.speed
    
    def update(self):
        """Update cube position"""
        # horizontal movement
        self.x += self.velocity_x

        # we don't need a timer – the jump is a single impulse and gravity handles the rest

        # always apply gravity so the cube falls after jumping or walking off an edge
        self.velocity_y += self.gravity

        # vertical movement (only once)
        self.y += self.velocity_y

        # Keep cube within horizontal bounds
        if self.x < 0:
            self.x = 0
        if self.x + self.size > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.size

        # ground collision
        if self.y + self.size >= GROUND_Y:
            self.y = GROUND_Y - self.size
            self.velocity_y = 0
            self.jumping = False

    def on_ground(self):
        """Return True if cube is standing on the ground"""
        return self.y + self.size >= GROUND_Y
    
    def draw(self, surface):
        """Draw the cube"""
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.size, self.size))

# Create cube
cube = Cube(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 25)

# load ground sprite (make sure assets/ground.svg exists)
ground_image = svg_to_surface("assets/grass.svg",
                              width=SCREEN_WIDTH,
                              height=GROUND_HEIGHT,
                              scale_mode='fill')

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Get pressed keys
    keys = pygame.key.get_pressed()
    
    # Update
    cube.handle_input(keys)
    cube.update()
    
    # Draw
    screen.fill(BLACK)
    # draw ground sprite aligned to the bottom of the ground area
    ground_y_pos = GROUND_Y + GROUND_HEIGHT - ground_image.get_height()
    screen.blit(ground_image, (0, ground_y_pos))
    cube.draw(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()