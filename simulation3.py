### This is the FAST version since it doesn't calculate AVERAGE CONTACT per PERSON per day
### This is called from Dash_Pygame_007

import random
import pygame
import simpy
import sys
import pandas as pd
#import matplotlib.pyplot as plt

# Retrieve the command-line arguments
args = sys.argv[1:]

# Check if all the required arguments are provided
if len(args) != 8:
    print("Error: Invalid number of arguments.")
    print("Usage: python simulation.py NUM_PEOPLE NUM_INFECTED INFECTION_PROBABILITY RECOVERY_TIME DEATH_PROBABILITY INFECTION_RADIUS MAX_SPEED")
    sys.exit(1)

# Parse the arguments
NUM_PEOPLE = int(args[0])
NUM_INFECTED = int(args[1])
INFECTION_PROBABILITY = float(args[2])
RECOVERY_TIME = int(args[3])
DEATH_PROBABILITY = float(args[4])
INFECTION_RADIUS = float(args[5])
MAX_SPEED = float(args[6])
NUM_DAYS = float(args[7])

# Define simulation parameters
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

daycounter = 1
infectedcounter = [NUM_INFECTED]
healthycounter = [NUM_PEOPLE - NUM_INFECTED]
removedcounter = [0]
#

# Define colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)


# Define person class
class Person:
    def __init__(self, env, id, infected=False):
        self.env = env
        self.id = id
        self.infected = infected
        self.recovered = False
        self.time_infected = 0
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.target_x = random.randint(0, SCREEN_WIDTH)
        self.target_y = random.randint(0, SCREEN_HEIGHT)
        self.contacts = 0

        # Start the person process
        self.process = env.process(self.update())

    def move(self):
        # Initialize velocity if it doesn't exist yet
        if not hasattr(self, 'vx') or not hasattr(self, 'vy'):
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)

        # Add small random displacement to the velocity vector
        self.vx += random.uniform(-0.1, 0.1)
        self.vy += random.uniform(-0.1, 0.1)

        # Limit the maximum speed of the velocity vector
        max_speed = MAX_SPEED
        speed = (self.vx ** 2 + self.vy ** 2) ** 0.5
        if speed > max_speed:
            self.vx *= max_speed / speed
            self.vy *= max_speed / speed

        # Move according to the velocity
        new_x = self.x + self.vx
        new_y = self.y + self.vy

        # Check if the new position is outside the screen boundaries
        if new_x < 0 or new_x > SCREEN_WIDTH:
            self.vx *= -1  # Reverse the x component of the velocity
        if new_y < 0 or new_y > SCREEN_HEIGHT:
            self.vy *= -1  # Reverse the y component of the velocity

        # Update the position with the adjusted velocity
        self.x += self.vx
        self.y += self.vy

    def update(self):
        while True:
            # Update person's position and behavior
            self.move()

            # Update target positions periodically
            if random.random() < 0.1:  # Change target positions 10% of the time
                self.update_targets()

            if self.infected and not self.recovered:
                self.time_infected += 1

                if self.time_infected >= RECOVERY_TIME:
                    # Determine if infected person recovers or dies
                    if random.random() < DEATH_PROBABILITY:
                        self.recovered = False
                        self.infected = False
                        people.remove(self)  # Remove the person from the list when they die
                        stats['deaths'] += 1
                    else:
                        self.recovered = True
                        stats['recovered'] += 1

            # Check for infection spread
            if self.infected and not self.recovered:
                for person in people:
                    if (
                            person.id != self.id
                            and not person.infected
                            and not person.recovered
                    ):
                        distance = ((person.x - self.x) ** 2 + (person.y - self.y) ** 2) ** 0.5
                        if distance <= INFECTION_RADIUS:
                            if random.random() < INFECTION_PROBABILITY:
                                person.infected = True
                                stats['infected'] += 1
                                stats['healthy'] -= 1

            # Wait for a longer period before the next update
            yield self.env.timeout(1.0)  # Increase the time step to 0.5 seconds

    def update_targets(self):
        # Randomly select new target positions
        self.target_x = random.randint(0, SCREEN_WIDTH)
        self.target_y = random.randint(0, SCREEN_HEIGHT)

    def draw(self):
        if self.infected and not self.recovered:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), INFECTION_RADIUS, 1)

        if self.infected and not self.recovered:
            color = RED
        elif self.recovered:
            color = GRAY
        else:
            color = GREEN

        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 5)


# Create simulation environment
env = simpy.Environment()

# Create people
people = []
for i in range(NUM_PEOPLE):
    infected = i < NUM_INFECTED
    person = Person(env, i, infected=infected)
    people.append(person)

# Define statistics dictionary
stats = {
    'deaths': 0,
    'recovered': 0,
    'infected': NUM_INFECTED,
    'healthy': NUM_PEOPLE - NUM_INFECTED,
}

# Simulation loop
running = True
for simulation_days in range(int(NUM_DAYS)):
    screen.fill((255, 255, 255))

    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Exit the simulation loop when the window is closed

    # Run the simulation for a small time step
    env.run(until=env.now + 1.0)  # Run the simulation for 0.5 seconds

    # Draw people
    for person in people:
        person.draw()

    # Check if simulation should stop
    #if stats['healthy'] == 0 or len(people) == 0:
    #    running = False

    # Display statistics
    text_surface = font.render(
        f"Days:{daycounter} | Infected: {stats['infected']}   Recovered: {stats['recovered']}   Healthy: {stats['healthy']}   Deaths: {stats['deaths']}",
        True, BLACK)
    screen.blit(text_surface, (10, 10))

    ######
    daycounter += 1
    infectedcounter.append(NUM_PEOPLE - stats['recovered'] - stats['healthy'] - stats['deaths'])
    healthycounter.append(stats['healthy'])
    removedcounter.append(stats['deaths'] + stats['recovered'])
    #######

    pygame.display.flip()
    clock.tick(30)  # Adjust the frame rate as needed

# Calculate total death rate
total_deaths = stats['deaths']
total_population = NUM_PEOPLE
total_death_rate = total_deaths / total_population

final_results = pd.DataFrame({'deaths': [total_deaths],
                              'recovered': [stats['recovered']],
                              'infected': [stats['infected']],
                              'healthy': [stats['healthy']]})

final_results.to_csv("final_results.csv")

days = list(range(1, daycounter + 1))

# Create a DataFrame from the data
data = pd.DataFrame({'Days': days,
                     'Healthy': healthycounter,
                     'Infected': infectedcounter,
                     'Removed': removedcounter})

data.to_csv("proportion_results.csv")

#sys.exit()
pygame.quit()
