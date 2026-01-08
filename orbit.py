import pygame
import math
import sys

# --- CONFIGURATION ---
WIDTH = 1000
HEIGHT = 700
FPS = 60

# COLORS
BLACK = (10, 10, 15)
WHITE = (220, 220, 220)
YELLOW = (255, 204, 0)
BLUE = (50, 150, 255)
RED = (255, 80, 80)
GREEN = (50, 255, 80)
GREY = (100, 100, 100)
DARK_GREY = (40, 40, 40)
PANEL_BG = (30, 30, 40)
ORANGE = (255, 165, 0)
BEIGE = (245, 245, 220)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)

# DEFAULT PHYSICS
DEFAULT_G = 0.4
DEFAULT_SPEED = 0.5

# GLOBAL STATE
STATE = {
    "G": DEFAULT_G,
    "timestep": DEFAULT_SPEED,
    "relativity": False,
    "show_trails": True,
    "zoom": 0.5,
    "offset_x": 0,
    "offset_y": 0,
    "planet_interactions": False,
    "selected_body": None,
    "sun_locked": True 
}

class Body:
    def __init__(self, x, y, mass, color, name, is_static=False):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.mass = mass
        self.color = color
        self.name = name
        self.is_static = is_static
        # Make the sun a bit smaller visually so we can see the wobble
        self.radius = 20 if name == "Sun" else max(5, int(math.log(mass) * 4))
        self.trail = []

    def apply_gravity(self, bodies):
        if self.is_static: return
        total_force = pygame.math.Vector2(0, 0)

        for other in bodies:
            if other == self: continue
            
            # STABILITY LOGIC
            if not STATE["planet_interactions"]:
                if self.name != "Sun" and other.name != "Sun":
                    continue

            diff = other.pos - self.pos
            dist = diff.length()
            if dist < 15: dist = 15 

            # Newton's Law
            force_mag = (STATE["G"] * self.mass * other.mass) / (dist**2)

            # Relativity
            if STATE["relativity"] and (other.name == "Sun" or self.name == "Sun"):
                c_speed = 40.0 
                force_mag += (STATE["G"] * self.mass * other.mass * 60000) / (dist**3 * c_speed**2)

            total_force += diff.normalize() * force_mag

        self.acc = total_force / self.mass

    def update(self):
        if self.is_static: return
        self.vel += self.acc * STATE["timestep"]
        self.pos += self.vel * STATE["timestep"]

        # Trail Logic
        if STATE["show_trails"]:
            if not self.trail or (self.pos - self.trail[-1]).length() > 5:
                self.trail.append(self.pos.copy())
            if len(self.trail) > 400:
                self.trail.pop(0)

    def draw(self, screen):
        cx = WIDTH // 2 + STATE["offset_x"]
        cy = HEIGHT // 2 + STATE["offset_y"] - 100
        
        screen_x = int((self.pos.x - WIDTH//2) * STATE["zoom"] + cx)
        screen_y = int((self.pos.y - HEIGHT//2) * STATE["zoom"] + cy)
        
        # Draw Trail
        if len(self.trail) > 2 and STATE["show_trails"]:
            pts = []
            for p in self.trail:
                px = (p.x - WIDTH//2) * STATE["zoom"] + cx
                py = (p.y - HEIGHT//2) * STATE["zoom"] + cy
                pts.append((px, py))
            pygame.draw.lines(screen, self.color, False, pts, 1)

        # Draw Body
        r = max(3, int(self.radius * STATE["zoom"]))
        
        if STATE["selected_body"] == self:
            pygame.draw.circle(screen, WHITE, (screen_x, screen_y), r + 2, 1)

        pygame.draw.circle(screen, self.color, (screen_x, screen_y), r)

        if self.name == "Saturn" and r > 3:
            pygame.draw.ellipse(screen, GREY, (screen_x - r*2.5, screen_y - r*0.5, r*5, r), 1)

    def is_clicked(self, mouse_pos):
        cx = WIDTH // 2 + STATE["offset_x"]
        cy = HEIGHT // 2 + STATE["offset_y"] - 100
        screen_x = (self.pos.x - WIDTH//2) * STATE["zoom"] + cx
        screen_y = (self.pos.y - HEIGHT//2) * STATE["zoom"] + cy
        dist = math.sqrt((screen_x - mouse_pos[0])**2 + (screen_y - mouse_pos[1])**2)
        return dist <= max(10, self.radius * STATE["zoom"])

# --- UI CLASSES ---
class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.hover = False

    def draw(self, screen, font):
        col = (70, 70, 90) if self.hover else (50, 50, 70)
        pygame.draw.rect(screen, col, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 1, border_radius=5)
        
        txt_surf = font.render(self.text, True, WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            self.callback()

class Slider:
    def __init__(self, x, y, w, min_val, max_val, key, label):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min = min_val
        self.max = max_val
        self.key = key
        self.label = label
        self.dragging = False

    def draw(self, screen, font):
        val = STATE[self.key]
        lbl = font.render(f"{self.label}: {val:.2f}", True, WHITE)
        screen.blit(lbl, (self.rect.x, self.rect.y - 20))
        pygame.draw.rect(screen, DARK_GREY, self.rect, border_radius=3)
        
        handle_x = self.rect.x + ((val - self.min) / (self.max - self.min)) * self.rect.width
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y - 5, 10, 30)
        pygame.draw.rect(screen, BLUE, handle_rect, border_radius=3)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        if self.dragging and event.type == pygame.MOUSEMOTION:
            rel_x = event.pos[0] - self.rect.x
            ratio = max(0, min(1, rel_x / self.rect.width))
            STATE[self.key] = self.min + (self.max - self.min) * ratio

# --- HELPER FUNCTIONS ---
def get_circular_velocity(body, sun, g_val):
    r_vec = sun.pos - body.pos
    r = r_vec.length()
    v = math.sqrt((g_val * sun.mass) / r)
    vec = pygame.math.Vector2(r_vec.y, -r_vec.x).normalize() * v
    return vec

def recalculate_orbits(bodies):
    sun = bodies[0]
    sun.vel = pygame.math.Vector2(0,0)
    sun.pos = pygame.math.Vector2(WIDTH//2, HEIGHT//2) # Reset Position
    
    # 1. Set Planet Velocities
    for b in bodies:
        if b.name == "Sun": continue
        b.vel = get_circular_velocity(b, sun, STATE["G"])
        if b.name == "Mercury" and STATE["relativity"]:
             b.vel *= 1.2 
        b.vel.y *= -1 
        b.trail = []
    
    # 2. IF UNLOCKED: BALANCE MOMENTUM (Wobble Mode) 
    if not STATE["sun_locked"]:
        total_momentum = pygame.math.Vector2(0,0)
        for b in bodies:
            if b.name == "Sun": continue
            total_momentum += b.vel * b.mass
        sun.vel = -(total_momentum / sun.mass)

def toggle_relativity():
    STATE["relativity"] = not STATE["relativity"]

def toggle_interactions():
    STATE["planet_interactions"] = not STATE["planet_interactions"]

def toggle_sun_lock(bodies):
    STATE["sun_locked"] = not STATE["sun_locked"]
    bodies[0].is_static = STATE["sun_locked"]
    recalculate_orbits(bodies)

def create_solar_system():
    bodies = []
    # Sun starts LOCKED (Static) to prevent breaking
    sun = Body(WIDTH//2, HEIGHT//2, 8000, YELLOW, "Sun", is_static=True)
    bodies.append(sun)
    
    planets = [
        ("Mercury", 100, 10, GREY),
        ("Venus", 160, 20, ORANGE),
        ("Earth", 220, 25, BLUE),
        ("Mars", 300, 15, RED),
        ("Jupiter", 500, 300, BEIGE),
        ("Saturn", 700, 250, BEIGE),
        ("Uranus", 900, 100, LIGHT_BLUE),
        ("Neptune", 1100, 110, DARK_BLUE)
    ]
    
    for name, dist, mass, col in planets:
        b = Body(WIDTH//2 - dist, HEIGHT//2, mass, col, name)
        bodies.append(b)
    
    recalculate_orbits(bodies)
    return bodies

# --- MAIN ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Solar System Calculator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 14)
    title_font = pygame.font.SysFont("Arial", 18, bold=True)

    bodies = create_solar_system()
    
    # UI Setup
    ui_height = 200
    ui_y_start = HEIGHT - ui_height
    ui_x_padding = 20
    
    sliders = [
        Slider(ui_x_padding, ui_y_start + 40, 150, 0.1, 2.0, "G", "Gravity (G)"),
        Slider(ui_x_padding, ui_y_start + 90, 150, 0.0, 1.0, "timestep", "Time Speed")
    ]
    
    # UPDATED BUTTONS
    buttons = [
        Button(ui_x_padding + 180, ui_y_start + 30, 140, 30, "Reset Orbits", lambda: recalculate_orbits(bodies)),
        Button(ui_x_padding + 180, ui_y_start + 70, 140, 30, "Toggle Relativity", toggle_relativity),
        Button(ui_x_padding + 180, ui_y_start + 110, 140, 30, "Lock/Unlock Sun", lambda: toggle_sun_lock(bodies))
    ]

    dragging_cam = False
    last_m = (0,0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            for s in sliders: s.handle_event(event)
            for b in buttons: b.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = False
                    for b in bodies:
                        if b.is_clicked(event.pos):
                            STATE["selected_body"] = b
                            clicked = True
                            break
                    if not clicked and event.pos[1] < ui_y_start:
                         dragging_cam = True
                         last_m = event.pos
                         STATE["selected_body"] = None 

            if event.type == pygame.MOUSEBUTTONUP: dragging_cam = False
            
            if event.type == pygame.MOUSEMOTION and dragging_cam:
                dx, dy = event.pos[0] - last_m[0], event.pos[1] - last_m[1]
                STATE["offset_x"] += dx
                STATE["offset_y"] += dy
                last_m = event.pos

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0: STATE["zoom"] *= 1.1
                else: STATE["zoom"] /= 1.1

        # Physics
        for _ in range(10):
            for b in bodies: b.apply_gravity(bodies)
            for b in bodies: b.update()

        # Drawing
        screen.fill(BLACK)
        for b in bodies: b.draw(screen)

        # UI Panel Background
        ui_rect = pygame.Rect(0, ui_y_start, WIDTH, ui_height)
        pygame.draw.rect(screen, PANEL_BG, ui_rect)
        pygame.draw.line(screen, WHITE, (0, ui_y_start), (WIDTH, ui_y_start), 2)

        # Draw Controls
        screen.blit(title_font.render("SETTINGS", True, YELLOW), (ui_x_padding, ui_y_start + 10))
        for s in sliders: s.draw(screen, font)
        for b in buttons: b.draw(screen, font)

        # Stats (Right Side)
        stats_x = WIDTH - 350
        screen.blit(title_font.render("LIVE DATA", True, YELLOW), (stats_x, ui_y_start + 10))
        
        status_text = [
            f"Relativity: {'ON' if STATE['relativity'] else 'OFF'}",
            f"Sun State: {'LOCKED' if STATE['sun_locked'] else 'UNLOCKED (Wobble)'}",
            f"Zoom: {STATE['zoom']:.2f}"
        ]
        for i, line in enumerate(status_text):
            screen.blit(font.render(line, True, WHITE), (stats_x, ui_y_start + 40 + i*20))

        if STATE["selected_body"]:
            sb = STATE["selected_body"]
            sun = bodies[0]
            dist = (sb.pos - sun.pos).length()
            speed = sb.vel.length()
            
            box_rect = pygame.Rect(stats_x + 150, ui_y_start + 35, 180, 110)
            pygame.draw.rect(screen, DARK_GREY, box_rect, border_radius=5)
            
            screen.blit(title_font.render(f"{sb.name}", True, sb.color), (box_rect.x + 10, box_rect.y + 10))
            screen.blit(font.render(f"Mass: {sb.mass}", True, WHITE), (box_rect.x + 10, box_rect.y + 35))
            screen.blit(font.render(f"Dist: {dist:.0f}", True, WHITE), (box_rect.x + 10, box_rect.y + 55))
            screen.blit(font.render(f"Vel: {speed:.2f}", True, WHITE), (box_rect.x + 10, box_rect.y + 75))
        else:
            screen.blit(font.render("Select Planet", True, GREY), (stats_x + 160, ui_y_start + 80))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()