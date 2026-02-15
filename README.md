## How to run these programs on Raspberry pi
Documentation coming soon!

<!-- 1. Read the raspi documentation for booting

For the record, I set the username as pi and the hostname as flighttracker in my Raspberry pi 4B model.
 -->

## Restarting the services after unplugging pi.
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