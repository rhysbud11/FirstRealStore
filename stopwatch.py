''' Race Timer using Pygame for graphics
Best lap times  is saved in files
False starts are handled as aborted races
Start and end signal with buzzer
Enables rerun of race
3.1 1st lap not -1
'''
from decimal import Decimal
import RPi.GPIO as GPIO
import time
import random
import pickle
import pygame

# Declare variables 
L1_time = 0
L2_time = 0
elap_f = 0
elap_r = 0
path = "/home/pi/Programming/Pygame/RaceTimer" # Set full path
best_Ferrari = pickle.load(open(path + "/SG/Ferrari.p", "rb")) # Lane 1 save file
best_RedBull = pickle.load(open(path + "/SG/RedBull.p", "rb")) # Lane 2 save file
L1_best_time = 10
L2_best_time = 10
L1_lap = -1    # 1st pass of finish line starts the 1st lap
L2_lap = -1    # 1st pass of finish line starts the 1st lap
Total_time = 0
Laps = 5       # Set No. of laps
Laps_Ferrari = 0 #Used to print laps
Laps_RedBull = 0 #Used to print laps
falsestart = True # Default false start, set to false same time as green light is lit
cheat = False
Ferrari_cheat = False
RedBull_cheat = False
course_length = 8.9 # This is the lenght of the track
avg_speed = 0
top_speed_1 = 0
top_speed_2 = 0


# Startlight & buzzers GPIO PIN numbers
redlight = 17
greenlight = 27
buzzer = 22

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255,40,0)
DARKBLUE = (0,0,128)

# Define separator line thickness (lh) and relative position separator (th)
lh = 15
th = 70
 
# Call this function so the Pygame library can initialize itself
pygame.init()
pygame.font.init()

# Create an 1600x900 sized screen, good to to use fullscreen when testing code.
screen = pygame.display.set_mode((1600, 900), pygame.FULLSCREEN)
#screen = pygame.display.set_mode((1600, 900))


# This sets the name of the window
pygame.display.set_caption("Race Timer")
 
# Add refresh rate ability
clock = pygame.time.Clock()
 
# Before the loop, load the sounds:
pygame.mixer.init()
pygame.mixer.music.set_volume(1.0)
click_sound = pygame.mixer.Sound(path + "/F1-new3.ogg")

 
# Set positions of graphics
dI = pygame.display.Info()
background_position_ferrari = [lh, lh]
background_position_redbull = [lh, dI.current_h/2 + lh*2]

# Create background and copy images to screen:
rectFerrari = pygame.Rect(0,0,dI.current_w,dI.current_h/2)
rectLine = pygame.Rect(0,dI.current_h/2,dI.current_w,lh)
rectRedbull = pygame.Rect(0,dI.current_h/2 + lh,dI.current_w,dI.current_h/2 - lh)

# Font for text in GUI
myFont = pygame.font.Font(path + "/Fonts/DS-DIGI.TTF", 75)
myFont2 = pygame.font.Font(path + "/Fonts/DS-DIGI.TTF", 45)

# Create labels variables
BT = myFont.render("Best Lap", 1, WHITE)
LT = myFont.render("Last Lap ", 1, WHITE)
RT = myFont.render("Record", 1, WHITE)
Lap_No = myFont.render("Lap No:", 1, WHITE)

# Load and set up graphics.
ferrari_image = pygame.image.load(path + "/Pics/ferrari.jpg").convert()
redbull_image = pygame.image.load(path + "/Pics/redbull.jpg").convert()
ferrari_image = pygame.transform.scale(ferrari_image, (341, 148))
redbull_image = pygame.transform.scale(redbull_image, (341, 148))

def time_converter(conv_time):
    minutes = int(conv_time/60)
    seconds = int(conv_time - minutes*60.0)
    hseconds = int((conv_time - minutes*60.0 - seconds)*100)
    return str('%02d:%02d:%02d' % (minutes, seconds, hseconds))

def wait():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

def raceAgain():
    global reRun
    global cheat
    global Ferrari_cheat
    global RedBull_cheat
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                reRun = False
                return

def my_racer1(channel):
    global L1_best_time
    global start_time
    global L1_lap
    global L1_time
    global Laps_Ferrari
    global cheat
    global elap_f
    global Ferrari_cheat
    L1_lap += 1
    if (L1_lap == 0):
        if falsestart:
            Ferrari_cheat = True
            cheat = True
        else:
            pass
    elif (L1_lap == 1):
        Laps_Ferrari = L1_lap
        elap_f = time.time() - start_time
        if (elap_f < L1_best_time):
            L1_best_time = elap_f # Keeping the best lap time for this race
        L1_time = time.time()
    else:
        Laps_Ferrari = L1_lap
        elap_f = time.time() - L1_time
        if (elap_f < L1_best_time):
            L1_best_time = elap_f # Keeping the best lap time for this race
        L1_time = time.time()

def my_racer2(channel):
    global L2_best_time
    global start_time
    global L2_lap
    global L2_time
    global Laps_RedBull
    global cheat
    global elap_r
    global RedBull_cheat
    L2_lap += 1
    if (L2_lap == 0):
        if falsestart:
            RedBull_cheat = True
            cheat = True            
        else:
            pass
    elif (L2_lap == 1):
        Laps_RedBull = L2_lap
        elap_r = time.time() - start_time
        if (elap_r < L2_best_time):
            L2_best_time = elap_r # Keeping the best lap time for this race
        L2_time = time.time()
    else:
        Laps_RedBull = L2_lap
        elap_r = time.time() - L2_time
        if (elap_r < L2_best_time):
            L2_best_time = elap_r # Keeping the best lap time for this race
        L2_time = time.time()

def drawResults():
    #Update times & Laps
    L1_best_time_text = myFont.render(time_converter(L1_best_time), 1, DARKBLUE)
    L1_time_text = myFont.render(time_converter(elap_f), 1, DARKBLUE)
    L1_lap_text = myFont.render(str(Laps_Ferrari), 1, DARKBLUE)

    L2_best_time_text = myFont.render(time_converter(L2_best_time), 1, RED)
    L2_time_text = myFont.render(time_converter(elap_r), 1, RED)
    L2_lap_text = myFont.render(str(Laps_RedBull), 1, RED)
        
    # Draw background and copy images to screen:
    screen.fill(RED, rectFerrari)
    screen.fill(BLACK, rectLine)
    screen.fill(DARKBLUE, rectRedbull)
    screen.blit(ferrari_image, background_position_ferrari)
    screen.blit(redbull_image, background_position_redbull)
        
    # Print Ferrari labels + time
    screen.blit(LT,                 (dI.current_w/3 + lh    , lh))
    screen.blit(BT,                 (2*dI.current_w/3 + lh  , lh))
    screen.blit(RT,                 (lh                     , dI.current_h/5 + lh))
    screen.blit(Lap_No,             (dI.current_w/3 + lh    , dI.current_h/5 + lh))
        
    screen.blit(L1_time_text,       (dI.current_w/3 + lh    , lh + th))
    screen.blit(L1_best_time_text,  (2*dI.current_w/3 + lh  , lh + th))
    screen.blit(RT_Ferrari,         (lh                     , dI.current_h/5 + lh + th))
    screen.blit(L1_lap_text,        (dI.current_w/2 - lh    , dI.current_h/5 + lh))

    # Print RedBull labels + time
    screen.blit(LT,                 (dI.current_w/3 + lh    , dI.current_h/2 + lh))
    screen.blit(BT,                 (2*dI.current_w/3 + lh  , dI.current_h/2 + lh))
    screen.blit(RT,                 (lh                     , dI.current_h/2 + dI.current_h/4))
    screen.blit(Lap_No,             (dI.current_w/3 + lh    , dI.current_h/2 + dI.current_h/4))

    screen.blit(L2_time_text,       (dI.current_w/3 + lh    , dI.current_h/2 + lh + th))
    screen.blit(L2_best_time_text,  (2*dI.current_w/3 + lh  , dI.current_h/2 + lh + th))
    screen.blit(RT_RedBull,         (lh                     , dI.current_h/2 + dI.current_h/4 + th))
    screen.blit(L2_lap_text,        (dI.current_w/2 - lh    , dI.current_h/2 + dI.current_h/4))

    pygame.display.flip()


reRun = True

# Check to race again    
while reRun:

    # Initialize GPIO PINS
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(redlight, GPIO.OUT)

    GPIO.setup(greenlight, GPIO.OUT)

    GPIO.setup(buzzer, GPIO.OUT)

    # GPIO PIN for Lane 1 sensor Team Ferrari
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # GPIO PIN for Lane 2 sensor Team RedBull
    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    #Racer 1 event
    time.sleep(0.1)
    GPIO.add_event_detect(23, GPIO.RISING, callback=my_racer1, bouncetime=2500)
                     
    #Racer 2 event
    time.sleep(0.1)
    GPIO.add_event_detect(24, GPIO.RISING, callback=my_racer2, bouncetime=2500) 

    # Reset variables for reRun 
    L1_time = 0
    L2_time = 0
    elap_f = 0
    elap_r = 0
    best_Ferrari = pickle.load(open(path + "/SG/Ferrari.p", "rb")) # Lane 1 save file   
    best_RedBull = pickle.load(open(path + "/SG/RedBull.p", "rb")) # Lane 2 save file
    L1_best_time = 10
    L2_best_time = 10
    L1_lap = -1    # 1st pass of finish line starts the 1st lap
    L2_lap = -1    # 1st pass of finish line starts the 1st lap
    Laps_Ferrari = 0 #Used to print laps
    Laps_RedBull = 0 #Used to print laps
    Total_time = 0
    falsestart = True # Default false start, set to false same time as green light is lit
    cheat = False
    Ferrari_cheat = False
    RedBull_cheat = False
    #course_length = 8.9 # This is the lenght of the track
    avg_speed = 0
    top_speed_1 = 0
    top_speed_2 = 0

    screen.fill(RED, rectFerrari)
    screen.fill(BLACK, rectLine)
    screen.fill(DARKBLUE, rectRedbull)
    screen.blit(ferrari_image, background_position_ferrari)
    screen.blit(redbull_image, background_position_redbull)

    #Define Record times & start message
    RT_Ferrari = myFont.render(time_converter(best_Ferrari), 1, DARKBLUE)
    RT_RedBull = myFont.render(time_converter(best_RedBull), 1, RED)
    Intro_text = myFont.render("Press Enter when ready to race!", 1, DARKBLUE)
    Exit_text = myFont.render("Press q to quit race.", 1, WHITE)
    Laps_text = myFont.render("Race is set to: " + str(Laps) + " laps.", 1, DARKBLUE)

    # Print Ferrari labels + record time
    screen.blit(LT, (dI.current_w/3 + lh            , lh))
    screen.blit(BT, (2*dI.current_w/3 + lh          , lh))
    screen.blit(RT, (lh                             , dI.current_h/5 + lh))
    screen.blit(RT_Ferrari, (lh                     , dI.current_h/5 + lh + th))

    # Print RedBull labels + record time
    screen.blit(LT, (dI.current_w/3 + lh            , dI.current_h/2 + lh))
    screen.blit(BT, (2*dI.current_w/3 + lh          , dI.current_h/2 + lh))
    screen.blit(RT, (lh                             , dI.current_h/2 + dI.current_h/4))
    screen.blit(RT_RedBull, (lh                     , dI.current_h/2 + dI.current_h/4 + th))

    # Print start message
    screen.blit(Intro_text, (dI.current_w/4         , lh + 2*th))
    screen.blit(Exit_text, (dI.current_w/3          , lh + 3*th))
    screen.blit(Laps_text, (dI.current_w/3 - lh     , lh + 4*th))

    # Update screen
    pygame.display.flip()

    # Play intro sound
    click_sound.play()
    pygame.mixer.fadeout(6000)
    
    # Waits for user to press Enter
    wait()
    pygame.mixer.quit()

    try:
        #Start lights reset
        GPIO.output(redlight, 0)
        GPIO.output(greenlight, 0)
        GPIO.output(buzzer, 0)
        
        #Start light sequence
        time.sleep(1)
        for x in range(0, 3):
            GPIO.output(redlight, 1)
            GPIO.output(buzzer, 1)
            time.sleep(0.3)
            GPIO.output(redlight, 0)
            GPIO.output(buzzer, 0)
            time.sleep(1)
        time.sleep(random.uniform(1, 3))
        falsestart = False
        GPIO.output(greenlight, 1)
        #Timing starts and ensures no false start
        start_time = time.time()

        GPIO.output(buzzer, 1)
        time.sleep(1)
        GPIO.output(buzzer, 0)

        done = False
        
        while ((L1_lap < Laps) and (L2_lap < Laps) and not cheat and not done):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    done = True
        
            drawResults()
            clock.tick(60)

        #Present final results    
        drawResults()

        if cheat:
            if Ferrari_cheat:
                f_cheat_text = myFont.render("Team Ferrari jumped the start!", 1, DARKBLUE)
                screen.blit(f_cheat_text, (dI.current_w/4 , 5*th))
            if RedBull_cheat:
                r_cheat_text = myFont.render("Team RedBull jumped the start!", 1, RED)
                screen.blit(r_cheat_text, (dI.current_w/4 , dI.current_h/2 + 5*th))
            pickle.dump(best_Ferrari, open(path + "/SG/Ferrari.p", "wb" ))
            pickle.dump(best_RedBull, open(path + "/SG/RedBull.p", "wb" ))
            
            pygame.display.flip()

            # False start signal
            GPIO.output(greenlight, 0)
            for x in range(0, 5):
                GPIO.output(redlight, 1)
                GPIO.output(buzzer, 1)
                time.sleep(0.3)
                GPIO.output(redlight, 0)
                GPIO.output(buzzer, 0)
                time.sleep(0.3)

            # Before the loop, load the sounds:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(1.0)
            click_sound = pygame.mixer.Sound(path + "/F1-new3.ogg")
            click_sound.play()
            pygame.mixer.fadeout(6000)
            
        else:       
            Total_time = time.time() - start_time
            if L1_lap > L2_lap:
                f_winner_text = myFont2.render("Team Ferrari is the winner with time: " + time_converter(Total_time), 1, WHITE)
                screen.blit(f_winner_text, (dI.current_w/4 , 4*th))
            if L1_lap < L2_lap:
                r_winner_text = myFont2.render("Team Redbull is the winner with time: " + time_converter(Total_time), 1, WHITE)
                screen.blit(r_winner_text, (dI.current_w/4 , dI.current_h/2 + 4.4*th))

            # Calculate race stats
            avg_speed = Decimal((course_length * Laps) / float(Total_time) * 3.6)
            top_speed_1 = Decimal(course_length / float(L1_best_time) * 3.6)
            top_speed_2 = Decimal(course_length / float(L2_best_time) * 3.6)
           
            if (L1_lap < 1):
                f_stats_text = myFont2.render("Team Ferrari did not complete 1 lap", 1, WHITE)
                screen.blit(f_stats_text, (dI.current_w/4 , 4*th))
            else:
                f_stats_text = myFont2.render("Team Ferrari's top avg. speed: " + str(round(top_speed_1, 2)) + " km/h", 1, WHITE)
                screen.blit(f_stats_text, (dI.current_w/4 , 4.7*th))

            if (L2_lap < 1):
                r_stats_text = myFont2.render("Team RedBull did not complete 1 lap", 1, WHITE)
                screen.blit(r_stats_text, (dI.current_w/4 , dI.current_h/2 + 4.4*th))
            else:
                r_stats_text = myFont2.render("Team RedBull's top avg. speed: " + str(round(top_speed_2, 2)) + " km/h", 1, WHITE)
                screen.blit(r_stats_text, (dI.current_w/4 , dI.current_h/2 + 5.1*th))

            if (L1_best_time < best_Ferrari): #Check and save Ferrari lap record on lane 1
                f_rec_text = myFont2.render("We have a new Ferrari lap record on lane 1! Press Enter.", 1, WHITE)
                screen.blit(f_rec_text, (dI.current_w/4 , 5.4*th))
                pickle.dump(L1_best_time, open(path + "/SG/Ferrari.p", "wb" ))
            else:
                f_rec_text = myFont2.render("No new lap record for Ferrari this race, press Enter.", 1, WHITE)
                screen.blit(f_rec_text, (dI.current_w/4 , 5.4*th))

            if (L2_best_time < best_RedBull): #Check and save RedBull lap record on lane 2
                r_rec_text = myFont2.render("We have a new RedBull lap record on lane 2! Press Enter", 1, WHITE)
                screen.blit(r_rec_text, (dI.current_w/4 , dI.current_h/2 + 5.8*th))
                pickle.dump(L2_best_time, open(path + "/SG/RedBull.p", "wb" ))
            else:
                r_rec_text = myFont2.render("No new lap record for Ferrari this race, press Enter.", 1, WHITE)
                screen.blit(r_rec_text, (dI.current_w/4 , dI.current_h/2 + 5.8*th))

            pygame.display.flip()

            # Before the loop, load the sounds:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(1.0)
            click_sound = pygame.mixer.Sound(path + "/F1-new3.ogg")
            click_sound.play()
            pygame.mixer.fadeout(6000)
                            
            # End of race signal
            for x in range(0, 3):
                GPIO.output(redlight, 1)
                GPIO.output(buzzer, 1)
                time.sleep(0.3)
                GPIO.output(redlight, 0)
                GPIO.output(buzzer, 0)
                time.sleep(0.5)

        # Necessary as GPIO.cleanup() won't remove detect events. 
        GPIO.remove_event_detect(23)
        GPIO.remove_event_detect(24)

    except KeyboardInterrupt:
        print("User controlled exit")
        pygame.quit()
    except:
        print ("Another exception")
        pygame.quit()
    finally:
        print("Cleaning up PINS")
        GPIO.cleanup()  #cleanup regardless of reason for exit.
        
    # Waits for user to press enter
    wait()

    #Text to race again
    race_again_text = myFont.render("Race again (y/n)?", 1, DARKBLUE)
    drawResults()
    screen.blit(race_again_text, (dI.current_w/4 , 5*th))

    # Update screen
    pygame.display.flip()
    
    #Check to race again
    raceAgain()

# Under while loop
pygame.quit()

