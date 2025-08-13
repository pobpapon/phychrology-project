from machine import I2C
import time

# ========================
# LCD API Base Class
# ========================
class LcdApi:
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_ENTRY_INC = 0x02
    LCD_ENTRY_SHIFT = 0x01
    LCD_ON_CTRL = 0x08
    LCD_ON_DISPLAY = 0x04
    LCD_ON_CURSOR = 0x02
    LCD_ON_BLINK = 0x01
    LCD_MOVE = 0x10
    LCD_MOVE_DISP = 0x08
    LCD_MOVE_RIGHT = 0x04
    LCD_FUNCTION = 0x20
    LCD_FUNCTION_8BIT = 0x10
    LCD_FUNCTION_2LINES = 0x08
    LCD_FUNCTION_10DOTS = 0x04
    LCD_CGRAM = 0x40
    LCD_DDRAM = 0x80
    LCD_RS_CMD = 0
    LCD_RS_DATA = 1
    LCD_RW_WRITE = 0
    LCD_RW_READ = 2
    LCD_BACKLIGHT = 8
    LCD_NOBACKLIGHT = 0

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        if self.num_lines > 4:
            self.num_lines = 4
        self.num_columns = num_columns
        if self.num_columns > 40:
            self.num_columns = 40
        self.cursor_x = 0
        self.cursor_y = 0

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        time.sleep_ms(2)
        self.cursor_x = 0
        self.cursor_y = 0

    def home(self):
        self.hal_write_command(self.LCD_HOME)
        time.sleep_ms(2)
        self.cursor_x = 0
        self.cursor_y = 0

    def move_to(self, col, row):
        if row >= self.num_lines:
            row = self.num_lines - 1
        if col >= self.num_columns:
            col = self.num_columns - 1
        addr = col & 0x3f
        if row & 1:
            addr += 0x40
        if row & 2:
            addr += 0x14
        self.hal_write_command(self.LCD_DDRAM | addr)
        self.cursor_x = col
        self.cursor_y = row

    def putchar(self, char):
        self.hal_write_data(ord(char))

    def putstr(self, string):
        for char in string:
            if char == '\n':
                self.cursor_x = 0
                self.cursor_y += 1
                if self.cursor_y >= self.num_lines:
                    self.cursor_y = 0
                self.move_to(self.cursor_x, self.cursor_y)
            else:
                self.putchar(char)
                self.cursor_x += 1
                if self.cursor_x >= self.num_columns:
                    self.cursor_x = 0
                    self.cursor_y += 1
                    if self.cursor_y >= self.num_lines:
                        self.cursor_y = 0
                    self.move_to(self.cursor_x, self.cursor_y)

# ========================
# I2C LCD Driver
# ========================
class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = self.LCD_BACKLIGHT
        time.sleep_ms(20)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        self.hal_write_init_nibble(0x02)
        self.hal_write_command(self.LCD_FUNCTION | self.LCD_FUNCTION_2LINES)
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)
        self.clear()
        super().__init__(num_lines, num_columns)

    def hal_write_init_nibble(self, nibble):
        self.hal_write_byte(nibble << 4)

    def hal_backlight_on(self):
        self.backlight = self.LCD_BACKLIGHT
        self.hal_write_byte(0)

    def hal_backlight_off(self):
        self.backlight = self.LCD_NOBACKLIGHT
        self.hal_write_byte(0)

    def hal_write_command(self, cmd):
        self.hal_write_byte((cmd & 0xF0) | self.LCD_RS_CMD)
        self.hal_write_byte(((cmd << 4) & 0xF0) | self.LCD_RS_CMD)

    def hal_write_data(self, data):
        self.hal_write_byte((data & 0xF0) | self.LCD_RS_DATA)
        self.hal_write_byte(((data << 4) & 0xF0) | self.LCD_RS_DATA)

    def hal_write_byte(self, val):
        self.i2c.writeto(self.i2c_addr, bytes([val | self.backlight | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([val | self.backlight]))
        time.sleep_us(50)