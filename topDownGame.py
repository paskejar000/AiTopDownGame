import pygame  
import math
pygame.init()  

FPS = 60
clock = pygame.time.Clock()

# Screen dimensions  
screen_width = 800  
screen_height = 600  
screen = pygame.display.set_mode((screen_width, screen_height))  
pygame.display.set_caption("Top-Down Game")  

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
    def __init__(self, x, y, image_file_name, sprite_count, scale_factor=3, color_tint=(0, 255, 0)):  
        self.x = x  
        self.y = y  
        self.speed = 2
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
        angle = math.degrees(math.atan2(pos[1] - self.rect.centery, pos[0] - self.rect.centerx))  
        rotated_image = pygame.transform.rotate(self.images[self.current_frame], -angle)  
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
    def move(self):  
        # Placeholder for enemy movement logic  
        self.moved = True
        self.update_animation()
    

enemies = [  
    Enemy(200, 150,"PlayerRobot",4,3,(255,0,0)),  
    Enemy(300, 250,"PlayerRobot",4,3,(255,0,0))  
]  
            
player = Player(100, 100,"PlayerRobot",4,3,(0,255,255)) 

# Main loop  
running = True  
while running:  
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            running = False  
            
    mouse_pos = pygame.mouse.get_pos() 
    keys = pygame.key.get_pressed()  
    player.move(keys)  
    
    screen.fill((0, 0, 0))  # Fill the screen with black  
    
    for enemy in enemies:  
        enemy.move()  
        enemy.face_point(player.rect.center)
    player.face_cursor()
    player.draw(screen)  
    for enemy in enemies:  
        enemy.draw(screen) 
    pygame.display.flip()  
    clock.tick(FPS) # Framerate
pygame.quit()  
