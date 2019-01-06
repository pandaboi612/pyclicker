import logging
import sys
import threading
import time

from pynput import keyboard, mouse
from pynput.mouse import Button, Controller

# TODO: add click package for arg parsing

# If these are changed, be sure to change the help text as well.
ACTIVATE_KEY = u'k'
DEACTIVATE_KEY = u'l'
DELAY = 0.0334
MOUSE_DELAY = 5

# Activate debugging output.
DEBUG = False

# Initializing variables.
cursor = Controller()
ready = False
clicking = False
click_counter = 0
total_clicks = 0
click_start_time = 0

# Logging setup.
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
screenhandler = logging.StreamHandler(sys.stdout)
if DEBUG:
    screenhandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
else:
    screenhandler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
screenhandler.setFormatter(formatter)
log.addHandler(screenhandler)


def on_press(key):
    global ready
    global clicking
    log.debug('Detected key press.')
    try:
        if key.char == ACTIVATE_KEY:
            log.debug('Activation key was pressed.')
            ready = True
        elif key.char == DEACTIVATE_KEY and clicking:
            log.debug('Deactivation key was pressed and clicking is True.')
            clicking = False
    except AttributeError:
        pass

    if key == keyboard.Key.esc:
        log.info('Quitting. Clicked {0} times in total.'.format(total_clicks))
        # Stop listeners
        keyboard.Listener.stop
        mouse.Listener.stop
        return False


def on_release(key):
    global ready
    log.debug('Detected key release.')
    try:
        if key.char == ACTIVATE_KEY:
            log.debug('Activation key was released.')
            ready = False
    except AttributeError:
        pass


def on_click(x, y, button, pressed):
    global clicking
    global total_clicks
    global click_counter
    global click_start_time
    # log.debug('Click detected.') #Too noisy, even for debug mode.
    if button == Button.left and ready and not clicking:
        log.info('Started clicking.')
        click_start_time = int(time.time())
        clicking = True
        start_clicking = ClickForever()


def on_move(x, y):
    global clicking
    global click_start_time
    log.debug('Mouse movement detected. Coords: {0}, {1}'.format(x, y))
    if clicking:
        if int(time.time()) - click_start_time > MOUSE_DELAY:
            log.info('Mouse movement detected after {0} seconds (configurable), stopping clicks.'.format(MOUSE_DELAY))
            clicking = False


class ClickForever(object):
    def __init__(self, interval=DELAY):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        """ Click forever, or until clicking is stopped. """
        global click_counter
        global total_clicks
        global click_stop_time
        global clicking
        while True:
            if not clicking:
                click_stop_time = int(time.time())
                total_time = click_stop_time - click_start_time
                actual_delay = 1 / float(click_counter / total_time)
                log.info(
                    'Clicking stopped. Just clicked {0} times. '
                    'Clicked for {1} seconds, this gives us an average actual delay of {2} which is {3} than the '
                    'expected delay of {4}. {5} clicks total this session.'.format(
                        click_counter,
                        total_time,
                        '{0:.5f}'.format(actual_delay),
                        'slower' if actual_delay > DELAY else 'faster',
                        DELAY,
                        total_clicks
                    )
                )
                click_counter = 0
                break
            else:
                cursor.click(Button.left, 1)
                log.debug('CLICK! {0}'.format(click_counter))
                click_counter += 1
                total_clicks += 1
            time.sleep(self.interval)


def main():
    # Intro banner
    log.info('{0}'.format('*'*80))
    log.info('* Welcome to pyClicker.{0}*'.format(' '*56))
    log.info('* Hold the letter {0} and left click to start clicking.{1}*'.format(ACTIVATE_KEY, ' '*26))
    log.info('* Once clicking has started, hit the lowercase {0} ({1}) to stop clicking.{2}*'.format(
        DEACTIVATE_KEY.upper(),
        DEACTIVATE_KEY.lower(),
        ' '*9
    ))
    log.info('* Hit Esc to quit.{0}*'.format(' '*61))
    log.info('* Current click delay is {0} seconds.{1}*'.format(DELAY, ' '*(45-len(str(DELAY)))))
    log.info('{0}'.format('*'*80))

    # Setup listeners
    m_listener = mouse.Listener(on_click=on_click, on_move=on_move)
    k_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    # Start listeners
    m_listener.start()
    k_listener.start()

    # Block until either listener exits.
    while k_listener.is_alive() and m_listener.is_alive():
        time.sleep(0.3)


if __name__ == '__main__':
    main()
