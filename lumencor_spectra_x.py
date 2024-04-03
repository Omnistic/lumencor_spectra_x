import serial, struct, sys, time

# Serial communication settings
COM_SETTINGS = {
    "baudrate": 9600,
    "bytesize": serial.EIGHTBITS,
    "parity": serial.PARITY_EVEN,
    "stopbits": serial.STOPBITS_ONE,
}

# LED enable in decimal representation
# Notice bit 4 is the Yellow (0) / Green (1) filter
LED_ENABLE = {
    "red": 1,     # 0b0000 0001
    "green": 2,   # 0b0000 0010
    "cyan": 4,    # 0b0000 0100
    "uv": 8,      # 0b0000 1000
    "filter": 16, # 0b0001 0000
    "blue": 32,   # 0b0010 0000
    "teal": 64,   # 0b0100 0000
}

# DAC IIC Address 18 colors
DAC_IIC_ADDRESS_18 = [
    "red",
    "green",
    "cyan",
    "uv",
]

# DAC IIC Address 1A colors
DAC_IIC_ADDRESS_1A = [
    "blue",
    "teal",
]

# LED intensity in decimal representation
# The DAC IIC Address discriminates between UV and Blue, and Cyan and Teal
LED_INTENSITY = {
    "red": 8,   # 0b0000 1000
    "green": 4, # 0b0000 0100
    "cyan": 2,  # 0b0000 0010
    "uv": 1,    # 0b0000 0001
    "blue": 1,  # 0b0000 0001
    "teal": 2,  # 0b0000 0010
}

# Temperature factor
TEMPERATURE_FACTOR = 0.125

class lumencor_spectra_x:
    def __init__(self, port) -> None:
        # Establish serial communication
        self.port = port
        try:
            self.sr = serial.Serial(
                port,
                COM_SETTINGS["baudrate"],
                COM_SETTINGS["bytesize"],
                COM_SETTINGS["parity"],
                COM_SETTINGS["stopbits"],
                )
        except serial.SerialException:
            print("Could not open serial port")
            raise
        
        # Send initialization commands
        self.sr.write(b"\x57\x02\xFF\x50") # Set GPIO0-3 as open drain output
        self.sr.write(b"\x57\x03\xAB\x50") # Set GPI05-7 push-pull out, GPIO4 open drain out

        # Set initial LED status to all off (and yellow filter, Bit 4) and minimum intensity
        self.turn_off_all_leds()

    def close(self):
        self.turn_off_all_leds()
        self.sr.close()

    def toggle_leds(self, colors: list)-> None:
        # Initialize byte decimal representation of the LEDs to enable
        colors_enable = 0

        # Attempt to enable the specified LEDs
        try:
            # If a single color is passed as a string, convert it to a list
            if type(colors) == str:
                colors = [colors]

            # Add corresponding colors to the byte decimal representation
            for color in colors:
                colors_enable += LED_ENABLE[color]

            # Update LED status and write the command to the serial port
            self.led_status = self.led_status ^ colors_enable
            self.sr.write(b"\x4F" + struct.pack("B", self.led_status) + b"\x50")
        except KeyError:
            print("Invalid color")
            raise

    def turn_off_all_leds(self)-> None:
        # Update LED status to all colors disabled
        self.led_status = 127

        # Send command to disable all LEDs
        self.sr.write(b"\x4F\x7F\x50")

        # Send command to put all LEDs intensity to minimum (0xFF)
        self.sr.write(b"\x53\x18\x03\x0F\xFF\xF0\x50")
        self.sr.write(b"\x53\x1A\x03\x0F\xFF\xF0\x50")

    def set_intensity(self, colors: list, intensity: int)-> None:
        dac_18_colors_byte = 0
        dac_1A_colors_byte = 0
        
        if type(colors) == str:
            colors = [colors]

        for color in colors:
            if color in DAC_IIC_ADDRESS_18:
                dac_18_colors_byte += LED_INTENSITY[color]
            elif color in DAC_IIC_ADDRESS_1A:
                dac_1A_colors_byte += LED_INTENSITY[color]
        
        intensity = 255 - intensity
        intensity_byte_one = intensity % 16 << 4
        intensity_byte_two = intensity // 16 + 240

        if dac_18_colors_byte:
            self.sr.write(b"\x53\x18\x03" + struct.pack("B", dac_18_colors_byte) + struct.pack("B", intensity_byte_two) + struct.pack("B", intensity_byte_one) + b"\x50")
        if dac_1A_colors_byte:
            self.sr.write(b"\x53\x1A\x03" + struct.pack("B", dac_1A_colors_byte) + struct.pack("B", intensity_byte_two) + struct.pack("B", intensity_byte_one) + b"\x50")

    def get_temperature(self):
        """
        Temperature is read from the serial port as two bytes. The decimal representation of the eleven most significant bits times
        the temperature factor (0.125) gives the temperature in degrees Celsius.
        """
        # Send command to ask the device to send the temperature
        self.sr.write(b"\x53\x91\x02\x50")

        # Convert the recieved bytes to temperature
        temperature = ( int.from_bytes(self.sr.read(2), "big" ) >> 5) * TEMPERATURE_FACTOR

        return temperature

def main():
    my_lamp = lumencor_spectra_x("COM3")

    print("Turn on a LED at full power (255)")
    color = "red"
    my_lamp.toggle_leds(color)
    my_lamp.set_intensity(color, 255)

    time.sleep(1)

    write = sys.stdout.write
    write("Vary intensity (255 to 0):    ")
    for ii in range(255, -1, -1):
        write("\b\b\b")
        write("{:3d}".format(ii)),
        my_lamp.set_intensity(color, ii)
        time.sleep(0.01)
    my_lamp.toggle_leds(color)
    write("\n")

    time.sleep(1)

    print("Turn on two LEDs at full power (255)")
    my_lamp.toggle_leds(["red", "green"])
    my_lamp.set_intensity(["red", "green"], 255)

    time.sleep(1)

    print("Engine temp: {:.2f}deg".format(my_lamp.get_temperature()))

    my_lamp.close()

if __name__ == "__main__":
    main()