
import wifi
import socketpool
import displayio
import terminalio
import board
from adafruit_display_text import label
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font
import time
from romi import Romi

try:
    from networkconfig import preferred_networks
    from networkconfig import preferred_ap_info
except ImportError:
    print("Network Configuration is in networkconfig.py. Please add them there")
    raise

display = board.DISPLAY

romi = Romi()
print("Voltage: ",romi.get_battery_mv())
time.sleep(2)
romi.ledDemo()
romi.motorDemo()

# Set up background images and text
group = displayio.Group()

romi_bitmap = displayio.OnDiskBitmap("/images/romi-esp.bmp")
romi_tile_grid = displayio.TileGrid(romi_bitmap, pixel_shader=romi_bitmap.pixel_shader)

wifi_sta_bitmap = displayio.OnDiskBitmap("/images/wifi.bmp")
wifi_sta_tile_grid = displayio.TileGrid(wifi_sta_bitmap, pixel_shader=wifi_sta_bitmap.pixel_shader)
wifi_sta_tile_grid.y = 50

wifi_ap_bitmap = displayio.OnDiskBitmap("/images/router.bmp")
wifi_ap_tile_grid = displayio.TileGrid(wifi_ap_bitmap, pixel_shader=wifi_ap_bitmap.pixel_shader)
wifi_ap_tile_grid.y = 50

wifi_font = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")
wifi_name_text_area = bitmap_label.Label(wifi_font, text="", color=0xFFFFFF)
wifi_name_text_area.x = 65
wifi_name_text_area.y = 65
group.append(wifi_name_text_area)

ip_address_text_area = label.Label(terminalio.FONT, text="", color=0x0000FF)
ip_address_text_area.x = 65
ip_address_text_area.y = 85
group.append(ip_address_text_area)

status_text_area = label.Label(terminalio.FONT, text="", color=0x00FF00)
status_text_area.x = 5
status_text_area.y = 125
group.append(status_text_area)


group.append(romi_tile_grid)

display.show(group)

in_station_mode = False
connected_ssid = ""
ip_address = ""
# Attempt to connect to WiFi
for wifi_network in preferred_networks:
    print("Connecting to ", wifi_network["ssid"], "...")
    status_text_area.text = "Connecting to " + wifi_network["ssid"] + "..."
    try:
        wifi.radio.connect(wifi_network["ssid"], wifi_network["password"])
        in_station_mode = True
        connected_ssid = wifi_network["ssid"]
        ip_address = wifi.radio.ipv4_address
        group.append(wifi_sta_tile_grid)
    except ConnectionError:
        print("Failed to connect to ", wifi_network["ssid"])

if in_station_mode:
    print("Successfully connected to ", connected_ssid)
    status_text_area.text = "Successfully connected to " + wifi_network["ssid"]
else:
    # Set up the chip in AP mode
    print("Starting AP ", preferred_ap_info["ssid"])
    status_text_area.text = "Starting AP " + preferred_ap_info["ssid"]
    wifi.radio.start_ap(preferred_ap_info["ssid"], preferred_ap_info["password"])
    ip_address = wifi.radio.ipv4_address_ap
    group.append(wifi_ap_tile_grid)
    status_text_area.text = "AP Set up"
    connected_ssid = preferred_ap_info["ssid"]

wifi_name_text_area.text = connected_ssid
ip_address_text_area.text = "IP Address: " + str(ip_address)


# Main event loop
while True:
    pass
