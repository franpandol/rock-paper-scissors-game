import pygame
import random
import math
import cv2
import numpy as np

# Initialize Pygame
pygame.init()

# Window dimensions
width, height = 1200, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Rock Paper Scissors Simulation")


BLACK, WHITE, RED, GREEN, BLUE = (
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
)


# Load images with transparency
def load_image(filename):
    image = pygame.image.load(filename)
    return image


# Load images
rock_img = load_image("resources/rock.png")
paper_img = load_image("resources/paper.png")
scissors_img = load_image("resources/scissors.png")

# Resize images to fit the SIZE
SIZE = 50  # Adjust this size if needed
rock_img = pygame.transform.scale(rock_img, (SIZE, SIZE))
paper_img = pygame.transform.scale(paper_img, (SIZE, SIZE))
scissors_img = pygame.transform.scale(scissors_img, (SIZE, SIZE))

# Object settings
NUM_OBJECTS, SPEED = 50, 250  # SPEED is now pixels per second
ROCK, PAPER, SCISSORS = 0, 1, 2
object_images = {ROCK: rock_img, PAPER: paper_img, SCISSORS: scissors_img}


class GameObject:
    def __init__(self):
        self.id = random.randint(0, 1000000)
        self.type = random.choice([ROCK, PAPER, SCISSORS])
        self.position = pygame.Vector2(
            random.randrange(0, width), random.randrange(0, height)
        )
        self.velocity = (
            pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize()
            * SPEED
        )

    def get_rect(self):
        # Returns a pygame.Rect representing the object's position and size
        return pygame.Rect(self.position.x, self.position.y, SIZE + 10, SIZE + 10)

    def move(self, dt):
        self.position += self.velocity * dt
        self.bounce_off_walls()

    def bounce_off_walls(self):
        if self.position.x < 0 or self.position.x > width - SIZE:
            self.velocity.x *= -1
        if self.position.y < 0 or self.position.y > height - SIZE:
            self.velocity.y *= -1
        self.position.x = max(0, min(self.position.x, width - SIZE))
        self.position.y = max(0, min(self.position.y, height - SIZE))

    def draw(self, screen):
        # Draw the image
        screen.blit(object_images[self.type], (self.position.x, self.position.y))

    def get_collision_circle(self):
        # Returns a tuple (center_x, center_y, radius) for the circle
        center_x = self.position.x + SIZE // 2
        center_y = self.position.y + SIZE // 2
        radius = SIZE // 2  # Approximate the image with a circle
        return center_x, center_y, radius

    # def collide(self, other):
    #     x1, y1, r1 = self.get_collision_circle()
    #     x2, y2, r2 = other.get_collision_circle()
    #     distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    #     return distance < (r1 + r2)  # True if circles overlap

    def get_collision_rect(self):
        # Adjust the collision rectangle to better match the visible part of the image
        # The adjustments here depend on the shape of your images
        # For example, if the images are centered and occupy 80% of the square:
        offset = SIZE * 0.1  # 10% offset from each side
        return pygame.Rect(
            self.position.x + offset,
            self.position.y + offset,
            SIZE - 2 * offset,
            SIZE - 2 * offset,
        )

    def repel(self, other):
        # Calculate direction vector from other object to this object
        direction = self.position - other.position
        if direction.length() != 0:
            direction = direction.normalize()

        # Apply repulsion force
        repel_strength = 5  # Adjust the strength of repulsion as needed
        self.position += direction * repel_strength
        other.position -= direction * repel_strength

        # Ensure objects stay within bounds after repulsion
        self.position.x = max(0, min(self.position.x, width - SIZE))
        self.position.y = max(0, min(self.position.y, height - SIZE))
        other.position.x = max(0, min(other.position.x, width - SIZE))
        other.position.y = max(0, min(other.position.y, height - SIZE))

    def collide(self, other):
        if self.get_collision_rect().colliderect(other.get_collision_rect()):
            self.repel(other)
            return True
        return False

    def convert(self, other):
        # Define the winning relationships
        wins_against = {ROCK: SCISSORS, SCISSORS: PAPER, PAPER: ROCK}

        # Check the interaction and determine the conversion
        if wins_against[self.type] == other.type:
            other.type = self.type
            return other
        elif wins_against[other.type] == self.type:
            self.type = other.type
            return self
        else:
            return None


# Initialize objects
objects = [GameObject() for _ in range(NUM_OBJECTS)]

# Set up the video writer
frame_rate = 30
frame_size = (width, height)
out = cv2.VideoWriter(
    "gameplay.avi", cv2.VideoWriter_fourcc(*"XVID"), frame_rate, frame_size
)

# Main game loop
running = True
clock = pygame.time.Clock()
done_recording = 0
while running:
    dt = clock.tick(60) / 1000  # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move and draw objects
    screen.fill(WHITE)
    all_one_type = False
    for obj in objects:
        obj.move(dt)
    new_objects = []
    # Check for collisions and convert
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            if objects[i].collide(objects[j]):
                new_object = objects[i].convert(objects[j])
                if new_object:
                    new_objects.append(new_object)
    for obj in new_objects:
        # replace the old object with the new one using the id to find it
        final_objects = [
            obj if obj.id == new_obj.id else new_obj for new_obj in objects
        ]

    for obj in final_objects:
        obj.draw(screen)

    # Save the frame
    frame = np.array(pygame.surfarray.array3d(screen))
    frame = cv2.transpose(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    out.write(frame)

    pygame.display.flip()
    clock.tick(60)

    # chck if all objects are of the same type
    all_one_type = all(obj.type == final_objects[0].type for obj in final_objects)
    if all_one_type:
        break

out.release()
pygame.quit()
