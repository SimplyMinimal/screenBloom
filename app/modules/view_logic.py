import sb_controller
import hue_interface
import ConfigParser
import utility
import json
import ast
import os


def get_index_data():
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())

    state = config.get('App State', 'running')
    hue_ip = config.get('Configuration', 'hue_ip')
    username = config.get('Configuration', 'username')
    auto_start = config.getboolean('Configuration', 'auto_start')
    current_preset = config.get('Configuration', 'current_preset')
    update = config.get('Light Settings', 'update')
    update_buffer = config.get('Light Settings', 'update_buffer')
    max_bri = config.get('Light Settings', 'max_bri')
    min_bri = config.get('Light Settings', 'min_bri')
    bulb_settings = json.loads(config.get('Light Settings', 'bulb_settings'))
    default = config.get('Light Settings', 'default')
    black = config.get('Light Settings', 'black_rgb')
    zones = config.get('Light Settings', 'zones')
    zone_state = config.getboolean('Light Settings', 'zone_state')
    color_mode = config.get('Light Settings', 'color_mode')
    party_mode = config.getboolean('Party Mode', 'running')

    default_color = default.split(',')
    black_rgb = black.split(',')
    zones = ast.literal_eval(zones)

    lights = hue_interface.get_lights_data(hue_ip, username)
    for light in lights:
        light.append(int(bulb_settings[unicode(light[0])]['max_bri']))
        light.append(int(bulb_settings[unicode(light[0])]['min_bri']))

    display_index = config.get('Light Settings', 'display_index')

    filepath = utility.get_json_filepath()
    presets = []
    if os.path.isfile(filepath):
        with open(filepath) as data_file:
            presets = json.load(data_file)

    icon_size = 10
    if len(lights) > 3:
        icon_size = 4

    data = {
        'state': state,
        'auto_start_state': auto_start,
        'update': update,
        'update_buffer': update_buffer,
        'max_bri': max_bri,
        'min_bri': min_bri,
        'default': default,
        'default_color': default_color,
        'black_rgb': black_rgb,
        'lights': lights,
        'lights_number': len(lights),
        'icon_size': icon_size,
        'username': username,
        'party_mode': party_mode,
        'zones': zones,
        'zone_state': zone_state,
        'display_index': display_index,
        'presets': presets,
        'current_preset': current_preset,
        'color_mode': color_mode
    }
    return data


def start_screenbloom():
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())
    state = int(config.get('App State', 'running'))
    update = config.get('Light Settings', 'update')
    sb_controller.get_screen_object().bulb_state = 'on'

    if update:
        state = False

    if state:
        message = 'ScreenBloom already running'
    else:
        utility.write_config('App State', 'running', '1')

        global t
        t = sb_controller.ScreenBloom(update)
        t.start()

        print '\nHello!'
        message = 'ScreenBloom thread initialized'

    data = {
        'message': message
    }
    return data


def stop_screenbloom():
    print '\nEnding screenBloom thread...'
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())
    utility.write_config('App State', 'running', '0')

    # End currently running threads
    try:
        t.join()
    except NameError:
        print 'ScreenBloom thread not running'

    sb_controller.update_bulb_default()
    data = {
        'message': 'Successfully ended screenBloom thread'
    }
    return data


def restart_check():
    global t
    config = ConfigParser.RawConfigParser()
    config.read(utility.get_config_path())
    update = config.get('Light Settings', 'update')

    try:
        if t.isAlive():
            print 'Restarting thread...'
            t.join()
            sb_controller.re_initialize()
            utility.write_config('App State', 'running', '1')

            t = sb_controller.ScreenBloom(update)
            t.start()

            print '\nHello!'
        else:
            sb_controller.re_initialize()
    except NameError:
        print 'Thread does not exist yet'
        sb_controller.re_initialize()
