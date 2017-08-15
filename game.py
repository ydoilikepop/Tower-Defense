import pygame, sys
from functions import *
from classes import *
from properties import *
from towers import *
from enemies import *
from bullets import * 

# Need to implement: 
#
# some way to create towers I'm thinking until I understand
# mouse movement I could have the player be a "builder" and he has to go 
# collect resources or something that could randomly appear on the map 
# in order to fill some sort of requirement to build a tower
#
# *DONE* enemy health
# *DONE* a path that's not a straight line for the enemies to move in
#
# a timer for build time 
#
# player resources 
#
# tower build time
#
# towet build cost
#
# some way for the game to end, ie if a certain number of enemies pass through 
#       Base HP: each enemy that breaks through reduces it
#
# variety of enemies
#
# enemies being able to kill the player and player has a death timer 
#
# *************************************************************
# Extra ideas:
# 
# *DONE* different towers
#
# Different types of towers (Fast shooting, slow shooting, splash damage, slow enemy)
#
# replace rects with sprites 
#
# a nicer background 
#
# sound
#
# highscores or something
#
# different levels 
#
# *************************************************************
# Notes:
#
# should I allow the player to help kill enemies?
# for the tower range, create an invisible rect around the tower
#       Circle is better * DONE

#*************************************************************
pygame.init() 

# Map settings
game_map = Map('map.txt')

# Grid dimensions
GRID_SIZE = game_map.grid_size

# Window size properties
WIDTH = game_map.cols * GRID_SIZE #1080
HEIGHT = game_map.rows * GRID_SIZE #720
SIZE = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(SIZE) 
clock = pygame.time.Clock()

# Player info
player = Player(pygame.Rect((10, 10), (GRID_SIZE, GRID_SIZE)), BLUE, WIDTH, HEIGHT, 
    TICK_SPEED / FRAME_RATE, TICK_SPEED / FRAME_RATE, gun_colour = YELLOW)
master_hp = HP_Bar(100, 0, HEIGHT - 15, WIDTH, 15)

# enemy stuff
enemy_list = [] 
enemy_start = game_map.starting_point()
counter = 0
spawn_time = 50
enemy_size = (GRID_SIZE, GRID_SIZE)
enemy_speed = RIGHT
enemy_initial_hp = 100 
enemy_max_hp = 100

# Bullet stuff 
bullet_list = [] 
tower_bullets = []
last_shot = 0
bullet_speed_x = 0
bullet_speed_y = 20
bullet_speed = (bullet_speed_x, bullet_speed_y)

# Tower stuff 
tower_list = [] 
last_upgrade = 0 

# testing stuff 
spawn_increase_time = 0 
spawn_decrease_time = 0
increase_enemy_health_time = 0 
myfont = pygame.font.SysFont("monospace", 15)
label = myfont.render("Health: %d SpawnRate: %d" % (enemy_initial_hp, spawn_time), 
    1, (255, 255, 255))
screen.blit(label, (100, 100))

# Main Gameloop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            pygame.quit()
            sys.exit()

        # keyboard press, no holding down
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_MINUS:
                master_hp.decrease_hp(10)
            if event.key == pygame.K_EQUALS:
                master_hp.increase_hp(10)
            if event.key == pygame.K_0:
                master_hp.increase_max_hp(10)
            if event.key == pygame.K_9:
                master_hp.decrease_max_hp(10)

    # Every clock update the counter will increment by one, when spawn_time
    # ticks have passed an enemy will spawn. 
    if counter % spawn_time == 0:
        rand = random.randint(0, 5)

        if rand == 5:
            enemy = Shield_Enemy(Enemy(pygame.Rect((enemy_start[0] - enemy_size[0], enemy_start[1]), enemy_size), ORANGE,
                                enemy_speed, WIDTH, HEIGHT, enemy_initial_hp, enemy_max_hp))
        else:
            enemy = Enemy(pygame.Rect((enemy_start[0] - enemy_size[0], enemy_start[1]), enemy_size), RED,
                                enemy_speed, WIDTH, HEIGHT, enemy_initial_hp, enemy_max_hp)
        enemy_list.append(enemy)

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]:
        player.update(y = -player.vertical_speed)
        player.direction = "U"
        bullet_speed = (bullet_speed_x, -bullet_speed_y)
    if pressed[pygame.K_DOWN]:
        player.update(y = player.vertical_speed)
        player.direction = "D"
        bullet_speed = (bullet_speed_x, bullet_speed_y)
    if pressed[pygame.K_LEFT]:
        player.update(x = -player.horizontal_speed)
        player.direction = "L"
        bullet_speed = (-bullet_speed_y, bullet_speed_x)
    if pressed[pygame.K_RIGHT]:
        player.update(x = player.horizontal_speed)
        player.direction = "R"
        bullet_speed = (bullet_speed_y, bullet_speed_x)

    if pressed[pygame.K_w]:
        for enemy in enemy_list:
            enemy.turn('U')
    if pressed[pygame.K_s]:
        for enemy in enemy_list:
            enemy.turn('D')
    if pressed[pygame.K_a]:
        for enemy in enemy_list:
            enemy.turn('L')
    if pressed[pygame.K_d]:
        for enemy in enemy_list:
            enemy.turn('R')

    if pressed[pygame.K_SPACE]:
        now = pygame.time.get_ticks()
        if now - last_shot >= SHOT_DELAY:
            pygame.mixer.Sound.play(player_gun)
            if player.direction == "U" or player.direction == "D":
                w = SHOT_WIDTH
                h = SHOT_HEIGHT
            else:
                w = SHOT_HEIGHT
                h = SHOT_WIDTH
            bullet_list.append(Bullet(bullet_speed, 
                coord_add(player.body.center, (
                    -w/2, -h/2)), YELLOW, HEIGHT, WIDTH, w, h))
            last_shot = now

    if pressed[pygame.K_t]:
        rand = random.randint(0,3)
        if rand == 0:
            temp = Rifle_Tower((player.body.x, player.body.y))
        elif rand == 1:
            temp = Sniper_Tower((player.body.x, player.body.y))
        elif rand == 2:
            temp = MachineGun_Tower((player.body.x, player.body.y))
        elif rand == 3:
            temp = HeavyGun_Tower((player.body.x, player.body.y))

        placeable = True
        if game_map.on_path(player.body):
            placeable = False
        for tower in tower_list:
            if distance(temp.body.center, tower.body.center) <= space_between: 
                placeable = False
                break
        if placeable:
            tower_list.append(temp)

    if pressed[pygame.K_g]:
        for tower in tower_list:
            if player.body.colliderect(tower.body):
                tower_list.remove(tower)
                break

    if pressed[pygame.K_u]:
        now = pygame.time.get_ticks()
        if now - last_upgrade >= UPGRADE_DELAY: 
            for tower in tower_list:
                if player.body.colliderect(tower.body):
                    if tower.level < tower_max_level:
                        tower.upgrade()
                        last_upgrade = now 
                    break

# ***************** TESTING COMMANDS ********************************

    # increases spawn rate for testing purposes
    if pressed[pygame.K_p]:
        now = pygame.time.get_ticks()
        if now - spawn_increase_time >= 100 and spawn_time > 15:
            spawn_time = spawn_time - 5
            spawn_increase_time = now

    # decreases spawn rate
    if pressed[pygame.K_o]:
        now = pygame.time.get_ticks()
        if now - spawn_decrease_time >= 100 and spawn_time < 200:
            spawn_time = spawn_time + 5
            spawn_decrease_time = now

    # increase enemy health 
    if pressed[pygame.K_h]:
        now = pygame.time.get_ticks()
        if now - increase_enemy_health_time >= 100 and enemy_initial_hp <= 500:
            enemy_initial_hp = enemy_initial_hp + 5
            enemy_max_hp = enemy_max_hp + 5
            for enemy in enemy_list:
                enemy.hp = enemy_initial_hp 
            increase_enemy_health_time = now

    # decrease enemy health 
    if pressed[pygame.K_j]:
        now = pygame.time.get_ticks()
        if now - increase_enemy_health_time >= 100 and enemy_initial_hp >= 10:
            enemy_initial_hp = enemy_initial_hp - 5 
            for enemy in enemy_list:
                enemy.hp = enemy_initial_hp 
            increase_enemy_health_time = now

    label = myfont.render("Health: %d Spawn Time: %d" % (enemy_initial_hp, spawn_time), 
        1, (255, 255, 255))

# ***************** TESTING COMMANDS ********************************


    screen.fill(BLACK) 
    screen.blit(label, (10, 10))
    

    # Draws path
    game_map.draw(screen, GRAY)

    for tower in tower_list:
        pygame.draw.rect(screen, tower.type, tower.body)
        
        # view range only when player is in range
        if distance(tower.body.center, player.body.center) <= 40:
            pygame.draw.circle(screen, GREEN, tower.body.center, tower.max_range, 1)

        # Tower range
        for enemy in enemy_list:
            if distance(tower.body.center, enemy.body.center) <= tower.max_range:
                # draws line to indicate hit for now
                #pygame.draw.lines(screen, RED, False, [tower.body.center, enemy.body.center], 2)
                bullet = tower.shoot(enemy, HEIGHT, WIDTH)
                if bullet is not None:  
                    tower_bullets.append(bullet)
                             
                # now based on the tower damage specified in the properties file 
                #enemy.hp = enemy.hp - tower.damage
                break
        tower.time += 1

    for bullet in tower_bullets:
        if bullet.check_destroy():
            tower_bullets.remove(bullet)

    for bullet in tower_bullets:
        pygame.draw.rect(screen, bullet.colour, bullet.body)
        bullet.update()
    # If the bullet leaves the screen then stop drawing the current bullet
    # and allow the player to make a new shot
    for bullet in bullet_list:
        if bullet.check_destroy():
            bullet_list.remove(bullet)

     # If the bullet is still on screen, draw it
    for bullet in bullet_list:
        pygame.draw.rect(screen, bullet.colour, bullet.body)
        bullet.update()
    player.draw(screen)
    

    # Draw each enemy and move it
    # If the enemy gets to the end of the screen remove it
    # Put draw and remove in different loops
    for enemy in enemy_list:
        for bullet in bullet_list:
            if enemy.check_hit(bullet):
                enemy.damage(bullet)
                bullet_list.remove(bullet) 
        for bullet in tower_bullets:
            if enemy.check_hit(bullet):
                # AOE weapon
                if type(bullet) is Heavy_Bullet: # bullet hit, then explodes because it's aoe bullet 
                    pygame.mixer.Sound.play(explode_sound)
                    pygame.draw.circle(screen, RED, bullet.body.center, 60, 1)
                    for enemy in enemy_list:
                        enemy.damage(bullet) 
                    tower_bullets.remove(bullet) 
                elif type(bullet) is Sniper_Bullet: # sniper bullets penetrate 
                    enemy.damage(bullet)
                    bullet.hits_left -= 1 

                    if bullet.hits_left == 0:
                        tower_bullets.remove(bullet) 
                else:
                    enemy.damage(bullet)
                    tower_bullets.remove(bullet)

        if enemy.breach():
            master_hp.decrease_hp(10)
            enemy_list.remove(enemy)
        elif enemy.check_destroy():
            enemy_list.remove(enemy)

    # Draw enemy if still alive at the end of the frame
    for enemy in enemy_list:
        corner_check = game_map.on_corner(enemy.body)
        if corner_check:
            enemy.turn(game_map.turn_direction(corner_check))
        pygame.draw.rect(screen, enemy.colour, enemy.body)


        # Enemy info
        # screen.blit(myfont.render("HP: %d/%d" % (enemy.hp, enemy.max_hp), 
        #     1, (255, 255, 255)), enemy.body.bottomleft)

        # HP Bar
        color = BLACK
        if enemy.hp > 0:
            if enemy.hp > 50:
                colour = GREEN
            elif enemy.hp > 30:
                colour = ORANGE
            else:
                colour = RED

        if type(enemy) is Shield_Enemy:
            pygame.draw.rect(screen, BLACK, [enemy.body.x, enemy.body.y + enemy.body.height - 5, enemy.body.width, 5])
            
            pygame.draw.rect(screen, colour, 
                [enemy.body.x, enemy.body.y + enemy.body.height - 5, enemy.body.width * enemy.hp / enemy.max_hp, 5])

            if enemy.shield_hp > 0:
                #pygame.draw.rect(screen, BLACK, [enemy.body.x, enemy.body.y + enemy.body.height - 10, enemy.body.width, 5])
                pygame.draw.rect(screen, WHITE,
                    [enemy.body.x, enemy.body.y + enemy.body.height - 10, enemy.body.width * enemy.shield_hp / enemy.max_shield, 5])
        else:
            pygame.draw.rect(screen, BLACK, [enemy.body.x, enemy.body.y + enemy.body.height - 5, enemy.body.width, 5])
            pygame.draw.rect(screen, colour, 
                [enemy.body.x, enemy.body.y + enemy.body.height - 5, enemy.body.width * enemy.hp / enemy.max_hp, 5])

        enemy.update()

    master_hp.draw(screen)
    pygame.display.update()
    clock.tick(FRAME_RATE)
    counter = counter + 1 
