# Raspberry pi flight tracker
I built a raspberry pi flight tracker that involves zero-api cost. 
I bought:
1. Adafruit SSD1306 OLED display
2. Raspberry Pi 4 Model B Starter Kit (32 GB memory card option)
3. Female-to-Female jumper wires (Whoever named this is probably a weirdo)

![Working demo](/assets/success.jpeg)

## Special thanks
This project would not be completed without these api providers! A special shout-out to them:
1. <a href='https://github.com/mrjackwills/adsbdb'>Mr Jack Wills' adsbdb</a>
2. <a href="https://opensky-network.org/">OpenSky network</a>

## How to run the given scripts on Raspberry Pi
Instructions coming soon!

## Restarting the services after re-plugging pi.
```bash
sudo systemctl stop flight-display.service
sudo systemctl stop flight-fetcher.service
sudo systemctl stop flight-fetcher.timer
```

Then
```bash
sudo systemctl daemon-reload
sudo systemctl restart flight-display.service
sudo systemctl restart flight-fetcher.service
sudo systemctl restart flight-fetcher.timer
```

## Next steps
Update the documentation. \\
Add a python rate limiter. \\
Add a TTL cache. \\
