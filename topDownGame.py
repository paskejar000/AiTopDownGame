import pygame  
import pygame.freetype  # To render text  
import math
import random

pygame.init()  
pygame.freetype.init()
font = pygame.freetype.Font(None, 50)  

# Game state variables  
START, PLAYING, GAME_OVER, VICTORY = 0, 1, 2, 3  
game_state = START  


FPS = 60
clock = pygame.time.Clock()

# Screen dimensions  
screen_width = 800  
screen_height = 600  
screen = pygame.display.set_mode((screen_width, screen_height))  
pygame.display.set_caption("Top-Down Game")  


# Function to draw text  
def draw_text(surface, text, pos, color=(255, 255, 255)):  
    # Render the text to get surface  
    text_surface = font.render(text, True, color)  
    text_rect = text_surface[1] 
  
    # Calculate centered position  
    text_rect.center = (pos[0], pos[1])  
      
    # Blit text surface to screen  
    font.render_to(surface,text_rect.topleft,text,color)
    
def tint_image(image, tint_color):  
    # Copy image to not modify the original  
    image = image.copy()  
    # Create a tint surface with the same size and alpha channel  
    tint = pygame.Surface(image.get_size()).convert_alpha()  
    # Fill with the tint color  
    tint.fill(tint_color)  
      
    # Blit the tint over the original image using the BLEND_RGBA_MULT blend mode  
    image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)  
    return image  

# Character class
class Character:  
    def __init__(self, x, y, speed:int, image_file_name, sprite_count, scale_factor=3, color_tint=(0, 255, 0)):  
        self.x = x  
        self.y = y  
        self.speed = speed
        self.scale_factor = scale_factor  # Adjust this to scale the sprite  
        self.images = [  
            pygame.transform.scale(pygame.image.load(f'{image_file_name}{i}.png'), (16 * self.scale_factor, 16 * self.scale_factor))  
            for i in range(1, sprite_count+1)    
        ]  
        # Apply color tint to all images  
        self.images = [tint_image(img, color_tint) for img in self.images]  
        self.current_frame = 0  
        self.animation_speed = 0.05  # Adjust for faster/slower animation  
        self.current_sprite = self.images[self.current_frame]
        self.frame_count = 0  
        self.rect = self.images[0].get_rect()  
        self.rect.topleft = (x, y)  
        self.moved = False
        self.angle = 0

    def update_animation(self):  
        if self.moved:
            self.frame_count += self.animation_speed
            if self.frame_count >= 1:
                self.current_frame = (self.current_frame + 1) % len(self.images)
                self.frame_count = 0
        else:
            self.frame_count = 0
            self.current_frame = 0
        self.current_sprite = self.images[self.current_frame]
    
    def draw(self, surface):
        surface.blit(self.current_sprite, self.rect)  
       
    def face_point(self, pos):
        if self.rect.center != pos:
            self.angle = math.degrees(math.atan2(pos[1] - self.rect.centery, pos[0] - self.rect.centerx))  
            
        rotated_image = pygame.transform.rotate(self.images[self.current_frame], -self.angle)  
        new_rect = rotated_image.get_rect(center=self.rect.center) 
            
        self.rect = new_rect
        self.current_sprite = rotated_image

class Player(Character):  
        
    def move(self, keys):  
        self.moved = False
        if keys[pygame.K_LEFT]:  
            self.rect.x -= self.speed  
            self.moved = True
        if keys[pygame.K_RIGHT]:  
            self.rect.x += self.speed  
            self.moved = True
        if keys[pygame.K_UP]:  
            self.rect.y -= self.speed  
            self.moved = True
        if keys[pygame.K_DOWN]:  
            self.rect.y += self.speed 
            self.moved = True
        self.update_animation()
            
    def face_cursor(self):
        mouse_pos = pygame.mouse.get_pos() 
        self.face_point(mouse_pos)
        
            
class Enemy(Character):  
    def on_move(self):  
        self.update_animation()
        
    def move_towards(self, pos):  
        
        target_x = pos[0]
        target_y = pos[1]
        # Calculate direction vector  
        direction_x = target_x - self.rect.centerx  
        direction_y = target_y - self.rect.centery  
  
        # Calculate distance to move  
        distance = math.hypot(direction_x, direction_y)  
          
        if distance > 0:  # Prevent division by zero  
            direction_x /= distance  
            direction_y /= distance  
  
            # Move the enemy  
            self.rect.x += direction_x * self.speed  
            self.rect.y += direction_y * self.speed 
            self.moved = True
        else:
            self.moved = False
        self.on_move()
        self.face_point(pos)
            
class Projectile:  
    def __init__(self, pos, target_pos, speed=10):  
        self.x = pos[0] 
        self.y = pos[1]
        target_x = target_pos[0]
        target_y = target_pos[1]
        self.speed = speed  
        self.radius = 5  
        self.color = (255, 255, 0)  # Yellow for visibility  
  
        # Calculate direction  
        direction_x = target_x - self.x  
        direction_y = target_y - self.y  
        distance = math.hypot(direction_x, direction_y)  
        self.velocity_x = (direction_x / distance) * speed  
        self.velocity_y = (direction_y / distance) * speed  
  
    def move(self):  
        self.x += self.velocity_x  
        self.y += self.velocity_y  
  
    def draw(self, surface):  
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)  
  
    def collide(self, enemy):  
        return enemy.rect.collidepoint(self.x, self.y)  


def check_collisions(player, enemies):  
    for enemy in enemies:  
        if player.rect.colliderect(enemy.rect):  
            return True  
    return False 

projectiles = []
enemies = [
    Enemy(screen_width - 48, 100, 3, "PlayerRobot",4,3,(255,0,0)),
    Enemy(screen_width - 48, 200, 3, "PlayerRobot",4,3,(255,0,0))
]

for y in range(100,300,100):
        for x in range(0,700,100):
            enemies.append(Enemy(48+x, y, random.randint(1,3), "PlayerRobot",4,3,(255,0,0)))
            
player = Player(screen_width/2 - 48, screen_height-96, 4, "PlayerRobot",4,3,(0,255,255)) 

drawable_objects = [player, enemies, projectiles]

def draw_objects(objects, screen):
    for obj in objects:
        if isinstance(obj, list):
            for instance in obj:
                if callable(getattr(instance,"draw", None)):
                    instance.draw(screen)
        elif callable(getattr(obj,"draw", None)):
            obj.draw(screen)
            
# Main loop  
running = True  
while running:  
    mouse_pos = pygame.mouse.get_pos() 
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            running = False  
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == START:  
                game_state = PLAYING  
            elif game_state == PLAYING:
                projectiles.append(Projectile(player.rect.center, mouse_pos))
    
    screen.fill((0, 0, 0))  # Fill the screen with black 
    keys = pygame.key.get_pressed()  
    
    if game_state == START:
        draw_text(screen, "Click to Start", (screen_width // 2, screen_height // 2))
    elif game_state == GAME_OVER:  
        draw_text(screen, "Game Over! Click the X to Exit", (screen_width // 2, screen_height // 2))  
    elif game_state == VICTORY:  
        draw_text(screen, "Victory! Click the X to Exit", (screen_width // 2, screen_height // 2))
        
    # MAIN PLAYING LOOP
    elif game_state == PLAYING:
        player.move(keys)  
        
        # Check for player collision with enemies  
        if check_collisions(player, enemies):  
            game_state = GAME_OVER
            print("Game Over!")  
        
        for projectile in projectiles[:]:  
            projectile.move()  
            for enemy in enemies[:]:  
                if projectile.collide(enemy):  
                    enemies.remove(enemy)  
                    projectiles.remove(projectile)  
                    break  
        
        if not enemies:  
            game_state = VICTORY  
        else:
            for enemy in enemies:  
                enemy.move_towards(player.rect.center)  
        
        player.face_cursor()
    
    # Draw all objects contained in drawable_objects
    draw_objects(drawable_objects,screen)

    pygame.display.flip()  
    clock.tick(FPS) # Framerate
pygame.quit()  