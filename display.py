from json import loads
import time
from pathlib import Path

import board
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

from api import DATA_PATH  # should be a Path

class DisplayService:
    def __init__(self, width: int, height: int, addr: int, data_path: Path = DATA_PATH):
        self.width = width
        self.height = height
        self.addr = addr
        self.data_path = Path(data_path)
        self.i2c = board.I2C()

    def send_cmd(self, cmd: int) -> None:
        self.i2c.writeto(self.addr, bytes([0x00, cmd]))

    def kick_panel(self) -> None:
        # display off
        self.send_cmd(0xAE)
        time.sleep(0.02)

        # display on
        self.send_cmd(0xAF)
        time.sleep(0.02)

        # all pixels on (brief “wake”)
        self.send_cmd(0xA5)
        time.sleep(0.05)

        # resume display from RAM
        self.send_cmd(0xA4)

    def render(self, oled, lines: list[str], font) -> None:
        image = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(image)

        # always render exactly 3 lines safely
        safe = (lines + ["", "", ""])[:3]

        draw.text((0, 16), safe[0], font=font, fill=255)
        draw.text((0, 32), safe[1], font=font, fill=255)
        draw.text((0, 48), safe[2], font=font, fill=255)

        oled.image(image)
        oled.show()

    def read_payload(self) -> dict:
        try:
            text = self.data_path.read_text()
            return loads(text)
        except FileNotFoundError:
            return {"source": "none", "flightcode": None}
        except Exception:
            return {"source": "none", "flightcode": None}

    def run_service(self) -> None:
        self.kick_panel()
        oled = adafruit_ssd1306.SSD1306_I2C(self.width, self.height, self.i2c, addr=self.addr)
        font = ImageFont.load_default()

        last_lines: list[str] | None = None

        while True:
            payload = self.read_payload()

            flightcode = payload.get("flightcode") or "--"
            src = payload.get("origin") or "--"
            dest = payload.get("destination") or "--"
            lines = [f"Flight: {flightcode}", f"Src: {src}", f"Dest: {dest}"]

            if lines != last_lines:
                # Pretty crucial, forcing OLED panel to update.
                self.kick_panel()
                
                oled.fill(0)
                self.render(oled, lines, font)
                last_lines = lines

            time.sleep(1.0)

if __name__ == "__main__":
    WIDTH, HEIGHT = 128, 64
    ADDR = 0x3C
    DisplayService(WIDTH, HEIGHT, ADDR).run_service()
