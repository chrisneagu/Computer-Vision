from sklearn.datasets import load_game  # sklearning kit
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn.tree import export_text
import graphviz
import pygame
import pydotplus


import random
import math
from pygame import mixer

game = load_game()
decision_tree = DecisionTreeClassifier(criterion='entropy', splitter='best', max_depth=2)

# constructie arbore

decision_tree = decision_tree.fit(game.data, game.target)

# afisare arbore
r = export_text(decision_tree, feature_names=game['feature_names'])
print(r)

dot_data = tree.export_graphviz(decision_tree, out_file=None)
graph = graphviz.Source(dot_data)
graph.render("game")

dot_data = tree.export_graphviz(decision_tree, out_file=None,
                                feature_names=game.feature_names,
                                class_names=game.target_names,
                                filled=True, rounded=True,
                                special_characters=True)

graph = pydotplus.graph_from_dot_data(dot_data)
graph.write_pdf("game.pdf")
graph.write_png("game.png")

# initialize the game
pygame.mixer.init()
pygame.init()
# screen creation
screenX = 1920
screenY = 1080
screen = pygame.display.set_mode((screenX, screenY))
imgPx = 64
# Title & Icon
pygame.display.set_caption("Computer Vision - Escape Room")
icon = pygame.image.load('favicon.png')
pygame.display.set_icon(icon)

# background
background = pygame.image.load('background.png')
mixer.music.load("background.mp3")
mixer.music.set_volume(0.05)
mixer.music.play(-1)

game_over = pygame.mixer.Sound("over.wav")
game_over.set_volume(0.05)
# Player
playerImg = pygame.image.load('player.png')
playerX = 0  # + move right - move left
playerY = screenY / 2  # - move upside + move downside
movement = 1

# WayPoints
wayPointsX = [0, screenX / 2, screenX / 4, 3 * screenX / 4, screenX - imgPx]
wayPointsY = [0, screenY / 2, screenY / 4, 3 * screenY / 4, screenY - imgPx]

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyM = []
circleX = []
circleY = []
patrolX = []
patrolY = []
inSight = []
wasChasing = []
radius = []

enemyNb = 6  # random.randint(1, 6)
for i in range(enemyNb):
    enemyImg.append(pygame.image.load('enemy.png'))  # 64px
    enemyX.append(random.randint(imgPx, screenX - imgPx))  # + move right - move left
    enemyY.append(random.randint(0, screenY - imgPx))  # - move upside + move downside
    patrolX.append(wayPointsX[random.randint(0, len(wayPointsX) - 1)])
    patrolY.append(wayPointsY[random.randint(0, len(wayPointsX) - 1)])
    radius.append(random.randint(50, 200))
    inSight.append(False)
    wasChasing.append(False)
    enemyM.append(1)  # each enemy has movement 1 same as player but they can have alerted movement which increases
# class for enemy to add a random number of enemies


# door
doorImg = pygame.image.load('door.png')
doorX = screenX - imgPx
doorY = random.randint(0, screenY - imgPx)

# wall
wallImg = []
wallX = []
wallY = []
wallNb = 25

for i in range(wallNb):
    wallImg.append(pygame.image.load('wall.jpg'))  # 64px
    wallX.append(random.randint(200 + imgPx, screenX - 2 * imgPx))  # + move right - move left
    wallY.append(random.randint(0, screenY - imgPx))  # - move upside + move downside


def wall(x, y):
    screen.blit(wallImg[i], (x, y))


def door(x, y):
    screen.blit(doorImg, (x, y))


def player(x, y):
    screen.blit(playerImg, (x, y))  # draw image in coordinates X & Y


def enemy(x, y, raza):
    screen.blit(enemyImg[i], (x, y))  # draw image in coordinates X & Y
    pygame.draw.circle(screen, "red", (x + 32, y + 32), raza, 1)


def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + (math.pow(y1 - y2, 2)))


def iscollision(distance):
    if distance < 64:
        return True
    else:
        return False


# Game Loop

running = True
while running:
    # Background Image

    screen.blit(background, (0, 0))
    door(doorX, doorY)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # WASD input control system
    oldX = playerX
    oldY = playerY
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LSHIFT] | keys[pygame.K_RSHIFT]:
        movement = 2
    else:
        movement = 1
    if keys[pygame.K_w]:
        playerY -= movement
    elif keys[pygame.K_s]:
        playerY += movement
    if keys[pygame.K_a]:
        playerX -= movement
    elif keys[pygame.K_d]:
        playerX += movement

    if playerX <= 0:
        playerX = 0
    elif playerX >= screenX - imgPx:
        playerX = screenX - imgPx
    if playerY <= 0:
        playerY = 0
    elif playerY >= screenY - imgPx:
        playerY = screenY - imgPx

    if iscollision(dist(playerX, playerY, doorX, doorY)):
        screen.blit(pygame.image.load("win.jpg"), (screenX / 2 - 250, screenY / 2 - 166))

    for j in range(wallNb):
        wall(wallX[j], wallY[j])
        if iscollision(dist(playerX, playerY, wallX[j], wallY[j])):
            playerX = oldX
            playerY = oldY

    for i in range(enemyNb):

        if dist(playerX, playerY, enemyX[i], enemyY[i]) <= radius[i]:
            inSight[i] = True
            wasChasing[i] = True
        else:
            inSight[i] = False

        if inSight[i]:
            if playerX < enemyX[i]:  # left
                if playerY < enemyY[i]:  # up
                    enemyX[i] -= enemyM[i]
                    enemyY[i] -= enemyM[i]
                elif playerY == enemyY[i]:
                    enemyX[i] -= enemyM[i]
                else:
                    enemyX[i] -= enemyM[i]
                    enemyY[i] += enemyM[i]
            elif playerX == enemyX[i]:
                if playerY < enemyY[i]:
                    enemyY[i] -= enemyM[i]
                elif playerY > enemyY[i]:
                    enemyY[i] += enemyM[i]
                else:
                    game_over.play()
                    print("Game Over")

                    running = False
            else:
                if playerY < enemyY[i]:
                    enemyX[i] += enemyM[i]
                    enemyY[i] -= enemyM[i]
                elif playerY > enemyY[i]:
                    enemyY[i] += enemyM[i]
                    enemyX[i] += enemyM[i]
                else:
                    enemyX[i] += enemyM[i]
        else:
            if patrolX[i] < enemyX[i]:
                enemyX[i] -= enemyM[i]
            elif patrolX[i] > enemyX[i]:
                enemyX[i] += enemyM[i]
            if patrolY[i] < enemyY[i]:
                enemyY[i] -= enemyM[i]
            elif patrolY[i] > enemyY[i]:
                enemyY[i] += enemyM[i]
            if iscollision(dist(enemyX[i], enemyY[i], patrolX[i], patrolY[i])):  # patrolling
                patrolX[i] = wayPointsX[random.randint(0, len(wayPointsX) - 1)]
                patrolY[i] = wayPointsY[random.randint(0, len(wayPointsY) - 1)]

            if wasChasing[i]:
                for j in range(enemyNb):
                    if i != j:
                        enemyM[j] = 2
                wasChasing[i] = False

        enemy(enemyX[i], enemyY[i], radius[i])

    player(playerX, playerY)
    pygame.display.update()
