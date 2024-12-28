import turtle 
import time
import random
from functools import partial

'''
Attention:
Number 1 to 5 are binded to a function add_food()
which simply increases the size of the snake.--> for cheating ^_^

'''
g_screen = None
g_snake = None     # snake's head
snake_cors = [0, 0]
g_snake_sz = 5     # size of the snake's tail
tail_cors = []
direct = None
last_direct = direct

monsters = []
monster_cors = []

foods = []
food_cors = []

g_intro = None
g_status = None

TIME = 0
CONTACT = 0
STATE = True
DIFFICULTY = 0.75 # from 0 to 1 the difficulty of the game will increase #

COLOR_BODY = ("blue", "black")
COLOR_HEAD = "red"
COLOR_MONSTER = "purple"

FONT_INTRO = ("Arial",12,"normal")
FONT_STATUS = ("Arial",16,"bold")
FONT_FOOD = ("Arial",10,"bold")

TIMER_SNAKE = 500   # refresh rate for snake

SZ_SQUARE = 20      # square size in pixels
DIM_PLAY_AREA = 500
DIM_STAT_AREA = 60 # !!! multiple of 40
DIM_MARGIN = 30
FOOD_NUMS = 5

KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SPACE = \
       "Up", "Down", "Left", "Right", "space"
HEADING_BY_KEY = {KEY_UP:90, KEY_DOWN:270, KEY_LEFT:180, KEY_RIGHT:0}

def create_turtle(x, y, color="red", border="black"):
    t = turtle.Turtle("square")
    t.color(border, color)
    t.up()
    t.goto(x,y)
    return t

def configure_play_area():
    # motion border
    m = create_turtle(0,0,"","black")
    sz = DIM_PLAY_AREA//SZ_SQUARE + 0.1 # 25.1
    m.shapesize(sz, sz, 3)
    m.goto(0,-DIM_STAT_AREA//2 + SZ_SQUARE/2)  # shift down half the status

    # status bars
    s = create_turtle(0,0,"","black")
    sz_w, sz_h = DIM_STAT_AREA//SZ_SQUARE, DIM_PLAY_AREA//SZ_SQUARE
    s.shapesize(sz_w, sz_h + 0.1, 3)
    s.goto(0, DIM_PLAY_AREA//2 + SZ_SQUARE/2 + 0.1)  # shift up half the motion
           
    # turtle to write introduction
    intro = create_turtle(-140,50)
    intro.hideturtle()
    intro.write("Click anywhere to start the game. Have fun! \n\n", font= FONT_INTRO)

    # turtle to write status
    status = create_turtle(0,0,"","black")
    status.hideturtle()
    status.goto(-200,s.ycor()-10)

    return intro, status

def configure_screen():
    # Configure the game screen #
    s = turtle.Screen() 
    s.tracer(0)
    s.title("Snake")
    w = DIM_PLAY_AREA + DIM_MARGIN*2
    h = DIM_PLAY_AREA + DIM_MARGIN*2 + DIM_STAT_AREA
    s.setup(1.05*w, 1.05*h)
    s.mode("standard")
    return s

def update_status():
    # Update the status on the status bar #
    g_status.clear()
    status = f'Contact: {CONTACT}    Time: {TIME}     Motion: {direct} '
    g_status.write(status, font=FONT_STATUS)
    g_screen.update()

def on_arrow_key_pressed(key):
    if STATE:
        global direct, last_direct
        if key == 'space':
            direct = last_direct if direct == 'Paused' else 'Paused' 
        else:
            direct = key
            last_direct = direct
        update_status()

def on_timer_snake():
    global snake_cors
    if direct is None: 
        g_screen.ontimer(on_timer_snake, TIMER_SNAKE)
        return  
    if direct == 'Paused':
        g_screen.ontimer(on_timer_snake, TIMER_SNAKE) if STATE else None
        return
    else:
        if block_move(direct, snake_cors) and STATE :
            g_snake.color(*COLOR_BODY)
            g_snake.stamp()
            g_snake.color(COLOR_HEAD)
            g_snake.setheading( HEADING_BY_KEY[direct] )
            g_snake.forward(SZ_SQUARE)
            
            global tail_cors
            snake_cors[0], snake_cors[1] = g_snake.xcor()//1, g_snake.ycor()//1 
            tail_cors.append([snake_cors[0], snake_cors[1]])
            # Shifting or extending the tail.
            # Remove the last square on Shifting.
            if len(g_snake.stampItems) > g_snake_sz:
                g_snake.clearstamps(1) 
                tail_cors.pop(0)
    # eating food will make the snake slower #
    if len(tail_cors) >= 6 and len(g_snake.stampItems) < g_snake_sz:
        delay = 800
    else:
        delay = TIMER_SNAKE

    g_screen.update()
    g_screen.ontimer(on_timer_snake, delay if STATE else None)

def block_move(direct, snake_cors):
    if direct == 'Up':    
        return False if snake_cors[1] >= 220 else True
    elif direct == 'Down':
        return False if snake_cors[1] <= -260 else True
    elif direct == 'Left':
        return False if snake_cors[0] <= -240 else True
    elif direct == 'Right':
        return False if snake_cors[0] >= 240 else True

def move_monsters():
    if STATE:
        idx = list(range(len(monsters)))
        for i in idx:
            if random.random() < DIFFICULTY:
                t = monsters[i]
                angle = t.towards(g_snake)
                qtr = angle // 45 # (0,1,2,3,4,5,6,7)
                heading = qtr * 45 if qtr % 2 == 0 else (qtr + 1) * 45
                t.setheading(heading)
                t.forward(SZ_SQUARE)
                contact_check(t)
        delay = random.randint(TIMER_SNAKE-60, TIMER_SNAKE+100)
        g_screen.ontimer(move_monsters, delay) 

def draw_end_text(text):
    w = turtle.Turtle()
    w.hideturtle()
    w.penup()
    w.goto(0, 0)
    w.color('red')
    w.write(text, align="center", font=("Arial", 20, "bold"))

def contact_check(monster):
    global CONTACT
    for cors in tail_cors:
        if abs(monster.xcor() - cors[0]) <= 16 and abs(monster.ycor() - cors[1]) <= 16:
            CONTACT += 1
            update_status()
            break

def on_time_detect():
    global STATE, monsters
    for monster in monsters:
        if monster.distance(g_snake) <= 15:
            draw_end_text("Game Over!")
            STATE = False
            g_screen.ontimer(None)
        elif len(tail_cors) == 20:
            draw_end_text("Winner!!!")
            STATE = False
            g_screen.ontimer(None)
    g_screen.ontimer(on_time_detect, 20)
        
def on_timer_TIME():
    global TIME
    TIME = int (time.time() - start_time)
    update_status()
    g_screen.ontimer(on_timer_TIME, 1000) if STATE else None

def random_monsters():
    global monster_cors
    factors = [7, 9 ,11, 13, 15, 17, 19, 21]
    monster_cors = arbitrary(factors, monster_cors, 4)

def random_food():
    global food_cors
    factors = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    food_cors = arbitrary(factors, food_cors, FOOD_NUMS)

def arbitrary(factors, cors, num):
    i = 0
    while i < num:
        x = random.choice(factors) * 10 * (-1 if random.random() < 0.5 else 1)
        y = random.choice(factors) * 10 * (-1 if random.random() < 0.5 else 1)
        if [x, y] not in cors:
            cors.append([x, y])
            i += 1
    return cors

def align_food():
    global foods
    for cors in food_cors:
        food = create_turtle(cors[0], cors[1] - 7, '', 'black')
        food.write(str(food_cors.index(cors) + 1), align='center', font= FONT_FOOD)      
        food.hideturtle()
        foods.append(food)

def food_move():
    global foods, food_cors
    if TIME >= 5 and STATE:
        for food in foods:
            if food != None and random.random() < DIFFICULTY**0.5:
                direct = random.choice(['Up', 'Down', 'Left', 'Right'])
                if abs(food.xcor()) <= 180  and abs(food.ycor()) <= 160:
                    food.clear()
                    food.setheading(HEADING_BY_KEY[direct])
                    food.forward(40)
                    # update the food's position in the food_cors list #
                    food_cors[foods.index(food)] = [food.xcor(), food.ycor()]
                    food.write(str(foods.index(food) + 1), align='center', font= FONT_FOOD)      

    g_screen.ontimer(food_move, random.randint(5000, 10000))

def on_timer_food():
    global foods, food_cors
    for food in foods:
        if  food != None and g_snake.distance(food) <= SZ_SQUARE//2:
            food_idx = foods.index(food)
            consume_food(food_idx + 1)
            foods[food_idx] = None
            food_cors[food_idx] = [10000, 10000]
            food.clear() 
    g_screen.ontimer(on_timer_food, 20)

def consume_food(num):
 
    global g_snake_sz
    g_snake_sz += num
    update_status()

def cb_start_game(x, y):
    """
    Starts the game by setting up the initial game state and event handlers.
    
    This function is called when the user clicks on the screen to start the game.
    It performs the following steps:
    
    1. Clears the on-screen click handler to prevent further clicks from starting the game.
    2. Clears the introductory message.
    3. Registers key event handlers for the arrow keys to handle player movement.
    4. Starts the timer-based updates for the snake and monster movements.
    5. Registers key event handlers for consuming food items 1 through 5.
    """
    g_screen.onscreenclick(None)
    g_intro.clear()
    random_food()
    align_food()

    for key in (KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT, KEY_SPACE):
        g_screen.onkey(partial(on_arrow_key_pressed,key), key)

    # it is for cheating #
    for n in range(1,6):
        g_screen.onkey(partial(consume_food,n), n)
    
    global start_time
    start_time = time.time()
    
    on_timer_TIME()
    on_timer_snake()
    on_timer_food()
    food_move()
    move_monsters()
    on_time_detect()


if __name__ == "__main__":
    g_screen = configure_screen()
    g_intro, g_status = configure_play_area()

    update_status()

    g_snake = create_turtle(0,0, COLOR_HEAD, "black")

    # random_monsters() --> to randomly summon 4 cordinates of the monsters 
    random_monsters()
        
    for j in range(4):
        monster = create_turtle(monster_cors[j][0], monster_cors[j][1], COLOR_MONSTER, "black")
    # monsters is a list to store the monster1-4 #
        monsters.append(monster)

    g_screen.onscreenclick(cb_start_game) # set up a mouse-click call back
    g_screen.update()
    g_screen.listen()
    g_screen.mainloop()