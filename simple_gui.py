import PySimpleGUI as sg
from lumencor_spectra_x import lumencor_spectra_x, LED_ENABLE

def main():
    my_lamp = lumencor_spectra_x("COM3")

    layout = [[], [], [], []]

    colors = list(LED_ENABLE.keys())
    filter_index = colors.index("filter")
    colors.remove("filter")

    for color in colors:
        layout[0].append([])
        layout[1].append(sg.Button(color.upper() + ": OFF", key=color, size=(10, 2)))
        layout[2].append(sg.Slider(range=(0, 255), default_value=0, orientation="horizontal", size=(9.8, 20), enable_events=True, key=color + "_intensity"))
        layout[3].append([])

    layout[0][filter_index] = sg.Button("FILTER: GREEN", key="filter", size=(10, 2))
    layout[3][0] = sg.Button("GET TEMPERATURE", key="temperature", size=(20, 2))
    layout[3][1] = sg.Text("Temperature: ", key="temperature_text", size=(20, 2))

    window = sg.Window(title="Lumencor Spectra X", layout=layout, margins=(50, 50))

    while True:
        event, values = window.read()

        if event in colors:
            my_lamp.toggle_leds(event)

            if window[event].get_text() == event.upper() + ": OFF":
                window[event].update(event.upper() + ": ON")
            elif window[event].get_text() == event.upper() + ": ON":
                window[event].update(event.upper() + ": OFF")

        if event == "filter":
            my_lamp.toggle_leds("filter")

            if window[event].get_text() == "FILTER: YELLOW":
                window[event].update("FILTER: GREEN")
            elif window[event].get_text() == "FILTER: GREEN":
                window[event].update("FILTER: YELLOW")

        if event in [color + "_intensity" for color in colors]:
            my_lamp.set_intensity(event[:-10], int(values[event]))

        if event == "temperature":
            window["temperature_text"].update("Temperature: {:.2f} °C".format(my_lamp.get_temperature()))

        if event == "OK" or event == sg.WIN_CLOSED:
            break
        
    my_lamp.close()
    window.close()

if __name__ == "__main__":
    main()