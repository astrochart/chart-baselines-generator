import hashlib
import matplotlib.pyplot as plt
import numpy as np
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# Use center of continguous US as reference point
center_lon = np.radians(-98.5795)
center_lat = np.radians(39.8283)
R = 6371000  # Radius of Earth in meters

# Google My Maps KML export URL for the CHART builds map.
# Replace the mid value if you need to point to a different shared map.
kml_url = (
    'https://www.google.com/maps/d/kml?mid=1tf58mb1arKZsweu0ZZLQyEQon6SK6y4&forcekml=1'
)

script_dir = Path(__file__).resolve().parent
kml_path = script_dir / 'builds.kml'

ns = {'kml': 'http://www.opengis.net/kml/2.2'}


def parse_coords_from_kml(kml_bytes):
    tree = ET.fromstring(kml_bytes)
    placemarks = tree.findall('.//kml:Placemark', ns)
    if not placemarks:
        raise RuntimeError('No placemarks found in KML export.')

    coords = []
    for placemark in placemarks:
        coord_el = placemark.find('.//kml:coordinates', ns)
        if coord_el is None or not coord_el.text:
            continue
        lon_str, lat_str, *_ = coord_el.text.strip().split()[0].split(',')
        coords.append((float(lon_str), float(lat_str)))
    return coords


def coords_hash(coords):
    normalized = sorted((f"{lon:.8f},{lat:.8f}" for lon, lat in coords))
    digest = hashlib.sha256('\n'.join(normalized).encode('utf-8')).hexdigest()
    return digest

with urllib.request.urlopen(kml_url) as response:
    fetched_kml = response.read()

current_coords = parse_coords_from_kml(fetched_kml)
current_hash = coords_hash(current_coords)

previous_hash = None
if kml_path.exists():
    previous_kml = kml_path.read_bytes()
    try:
        previous_coords = parse_coords_from_kml(previous_kml)
        previous_hash = coords_hash(previous_coords)
    except Exception:
        previous_hash = None

if previous_hash == current_hash:
    print('No underlying coordinate changes detected; skipping plot generation.')
    raise SystemExit(0)

kml_path.write_bytes(fetched_kml)

lonlat = [(np.radians(lon), np.radians(lat)) for lon, lat in current_coords]
lonlat = [(lon - center_lon, lat) for lon, lat in lonlat]

# Get x/y/z in meters from lon/lat
x = [R * np.cos(lat) * np.sin(lon) for lon, lat in lonlat]
y = [R * np.cos(lat) * np.cos(lon) for lon, lat in lonlat]
z = [R * np.sin(lat) for lon, lat in lonlat]

# Now we rotate about the x-axis by 90 degrees minus center_lat to make the center of the US at the origin
theta = np.radians(90) - center_lat
x_rot = x
y_rot = [-y[i] * np.cos(theta) + z[i] * np.sin(theta) for i in range(len(y))]
z_rot = [y[i] * np.sin(theta) + z[i] * np.cos(theta) for i in range(len(z))]

# Make array of baseline coordinates
baselines = np.empty((len(x_rot)**2, 2))
for i in range(len(x_rot)):
    for j in range(len(x_rot)):
        baselines[i * len(x_rot) + j] = [x_rot[i] - x_rot[j], y_rot[i] - y_rot[j]]
baselines /= 1e3  # Convert to kilometers

# Plot the baselines
plt.figure()
plt.scatter(baselines[:, 0], baselines[:, 1], s=50, marker='D')
plt.title('CHART Build Baselines')
plt.xlabel('East  (km)')
plt.ylabel('North (km)')
maxdim = 1.2 * np.max(np.abs(baselines))
plt.xlim([-maxdim, maxdim])
plt.ylim([-maxdim, maxdim])
plt.gca().set_aspect('equal')
plt.tight_layout()
plt.savefig(script_dir / 'chart_baselines.png', dpi=300)
