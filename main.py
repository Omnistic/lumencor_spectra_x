from lumencor_spectra_x import lumencor_spectra_x
from nicegui import ui

global spectra_x

def toggle_connection():
    if connection_switch.value:
        ui.notify("Connecting to SPECTRA X...")
        try:
            global spectra_x
            spectra_x = lumencor_spectra_x("COM14")
            temperature_timer.activate()
            ui.notify("Connected successfully!")
        except Exception as e:
            ui.notify(f"Connection failed: {e}")
    else:
        if 'spectra_x' in globals():
            spectra_x.close()

            red_switch.value = False
            green_switch.value = False
            cyan_switch.value = False
            uv_switch.value = False
            blue_switch.value = False
            teal_switch.value = False
            red_knob.value = 0
            green_knob.value = 0
            cyan_knob.value = 0
            uv_knob.value = 0
            blue_knob.value = 0
            teal_knob.value = 0

            temperature_timer.deactivate()
            temperature_label.text = ''

            ui.notify("Disconnected from SPECTRA X.")
        else:
            ui.notify("No active connection to disconnect.")

def toggle_led(e):
    global spectra_x
    spectra_x.toggle_leds(e.sender.text.lower())

def change_intensity(color, intensity):
    global spectra_x
    spectra_x.set_intensity(color, intensity)

def update_temperature():
    global spectra_x
    temperature_label.text = 'Temperature: {:.1f}°C'.format(spectra_x.get_temperature())

connection_switch = ui.switch('Toggle SPECTRA X', on_change=toggle_connection)

with ui.card():
    with ui.row():
        red_switch = ui.switch('Red', on_change=toggle_led).bind_enabled_from(connection_switch, target_name='value')
        with ui.knob(min=0, max=255, step=1, value=0, show_value=True, track_color='gray-2', on_change=lambda:change_intensity('red', red_knob.value)).bind_enabled_from(connection_switch, target_name='value') as red_knob:
            ui.icon('light_mode')
    with ui.row():
        green_switch = ui.switch('Green', on_change=toggle_led).bind_enabled_from(connection_switch, target_name='value')
        with ui.knob(min=0, max=255, step=1, value=0, show_value=True, track_color='gray-2', on_change=lambda:change_intensity('green', green_knob.value)).bind_enabled_from(connection_switch, target_name='value') as green_knob:
            ui.icon('light_mode')
    with ui.row():
        cyan_switch = ui.switch('Cyan', on_change=toggle_led).bind_enabled_from(connection_switch, target_name='value')
        with ui.knob(min=0, max=255, step=1, value=0, show_value=True, track_color='gray-2', on_change=lambda:change_intensity('cyan', cyan_knob.value)).bind_enabled_from(connection_switch, target_name='value') as cyan_knob:
            ui.icon('light_mode')
    with ui.row():
        uv_switch = ui.switch('UV', on_change=toggle_led).bind_enabled_from(connection_switch, target_name='value')
        with ui.knob(min=0, max=255, step=1, value=0, show_value=True, track_color='gray-2', on_change=lambda:change_intensity('uv', uv_knob.value)).bind_enabled_from(connection_switch, target_name='value') as uv_knob:
            ui.icon('light_mode')
    with ui.row():
        blue_switch = ui.switch('Blue', on_change=toggle_led).bind_enabled_from(connection_switch, target_name='value')
        with ui.knob(min=0, max=255, step=1, value=0, show_value=True, track_color='gray-2', on_change=lambda:change_intensity('blue', blue_knob.value)).bind_enabled_from(connection_switch, target_name='value') as blue_knob:
            ui.icon('light_mode')
    with ui.row():
        teal_switch = ui.switch('Teal', on_change=toggle_led).bind_enabled_from(connection_switch, target_name='value')
        with ui.knob(min=0, max=255, step=1, value=0, show_value=True, track_color='gray-2', on_change=lambda:change_intensity('teal', teal_knob.value)).bind_enabled_from(connection_switch, target_name='value') as teal_knob:
            ui.icon('light_mode')
    with ui.row():
        filter_switch = ui.switch('Filter', on_change=toggle_led).bind_enabled_from(connection_switch, target_name='value')

temperature_timer = ui.timer(5.0, callback=update_temperature, active=False)

temperature_label = ui.label('')

ui.run(dark=True, port=80)