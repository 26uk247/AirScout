# python script to run once or on a schedule to download the meteo data into /tmp/rain_aircraft.json, which will be picked up by the node-red flow and served as a JSON feed for Airscout


import boto3
from botocore import UNSIGNED
from botocore.config import Config
import h5py
import numpy as np
from scipy import ndimage
from pyproj import Transformer
import requests
import socket
import urllib3.util.connection as urllib3_cn
import json
import time
import os

MIN_DBZ = 30.0
MIN_PIXELS = 4
GRID_SPLIT_KM = 12
OUTPUT_FILE = "/tmp/rain_aircraft.json"

LAT_MIN, LAT_MAX = 45.0, 55.0
LON_MIN, LON_MAX = -10, -0

def get_weather_params():
    try:
        urllib3_cn.allowed_gai_family = lambda: socket.AF_INET
        base_url = "https" + chr(58) + "//api.open-meteo" + chr(46) + "com/v1/forecast"
        params = {
            "latitude": 50.3,
            "longitude": -5.2,
            "hourly": "freezing_level_height,wind_speed_850hPa,wind_direction_850hPa",
            "forecast_days": 1,
            "timezone": "UTC"
        }
        data = requests.get(base_url, params=params, timeout=10).json()
        hourly = data.get("hourly", {})
        target_hour = time.strftime("%Y-%m-%dT%H:00", time.gmtime())
        times = hourly.get("time", [])
        idx = times.index(target_hour) if target_hour in times else time.gmtime().tm_hour

        height_m = hourly.get("freezing_level_height", list()).__getitem__(idx)
        w_spd_kmh = hourly.get("wind_speed_850hPa", list()).__getitem__(idx)
        w_dir_from = hourly.get("wind_direction_850hPa", list()).__getitem__(idx)

        alt_ft = int(round(max(450.0, float(height_m) - 200.0) * 3.28084)) if height_m is not None else 5000
        spd_kts = max(5, int(round(float(w_spd_kmh) * 0.539957))) if w_spd_kmh is not None else 35
        trak_deg = int(round((float(w_dir_from) + 180.0) % 360.0)) if w_dir_from is not None else 75
        return alt_ft, spd_kts, trak_deg
    except Exception as e:
        print(f"Open-Meteo warning: {e}")
    return 5000, 35, 75
def fetch_latest_radar_hdf5(local_path="/tmp/latest_radar.h5"):
    s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED), region_name="eu-west-2")
    bucket = "met-office-radar-obs-data"
    now_utc = time.time()
    for offset_sec in (0, -86400):
        prefix = time.strftime("radar/%Y/%m/%d/", time.gmtime(now_utc + offset_sec))
        resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        h5_objs = [o for o in resp.get("Contents", []) if o["Key"].endswith(".h5")]
        if h5_objs:
            latest_obj = sorted(h5_objs, key=lambda x: x["Key"]).__getitem__(-1)
            s3.download_file(bucket, latest_obj["Key"], local_path)
            return latest_obj["Key"]
    return None

def process_radar():
    h5_path = "/tmp/latest_radar.h5"
    latest_key = fetch_latest_radar_hdf5(h5_path)
    if not latest_key:
        print("No radar files found.")
        return
    alt_ft, spd_kts, trak_deg = get_weather_params()
    now_ms = int(time.time() * 1000)
    ac_list = []
    with h5py.File(h5_path, "r") as f:
        raw_data = f["dataset1/data1/data"][:]
        what = f["dataset1/data1/what"].attrs
        gain = float(what.get("gain", 1.0))
        offset = float(what.get("offset", 0.0))
        nodata = float(what.get("nodata", -1.0))
        undetect = float(what.get("undetect", 0.0))
        valid = (raw_data != nodata) & (raw_data != undetect) & (raw_data > 0)
        rain_rate = np.zeros_like(raw_data, dtype=float)
        rain_rate[valid] = raw_data[valid] * gain + offset
        dbz = np.zeros_like(rain_rate)
        pos = rain_rate > 0.05
        dbz[pos] = 10.0 * np.log10(200.0 * (rain_rate[pos] ** 1.6))
        where = f["where"].attrs
        proj_str = where["projdef"].decode("utf-8") if isinstance(where["projdef"], bytes) else where["projdef"]
        xscale = float(where["xscale"])
        yscale = float(where["yscale"])
        to_proj = Transformer.from_crs("EPSG:4326", proj_str, always_xy=True)
        to_latlon = Transformer.from_crs(proj_str, "EPSG:4326", always_xy=True)
        ul_x, ul_y = to_proj.transform(float(where["UL_lon"]), float(where["UL_lat"]))
        x_min, y_min = to_proj.transform(LON_MIN, LAT_MIN)
        x_max, y_max = to_proj.transform(LON_MAX, LAT_MAX)
        col_start = max(0, int((x_min - ul_x) / xscale))
        col_end = min(dbz.shape.__getitem__(1), int((x_max - ul_x) / xscale))
        row_start = max(0, int((ul_y - y_max) / yscale))
        row_end = min(dbz.shape.__getitem__(0), int((ul_y - y_min) / yscale))
        sub_dbz = dbz[row_start:row_end, col_start:col_end]
        rows, cols = sub_dbz.shape
        step = GRID_SPLIT_KM
        target_id = 0
        for r0 in range(0, rows, step):
            for c0 in range(0, cols, step):
                tile = sub_dbz[r0:r0 + step, c0:c0 + step]
                mask = tile >= MIN_DBZ
                pixel_count = int(np.sum(mask))
                if pixel_count < MIN_PIXELS:
                    continue
                cy, cx = ndimage.center_of_mass(tile * mask)
                proj_x = ul_x + (col_start + c0 + cx) * xscale
                proj_y = ul_y - (row_start + r0 + cy) * yscale
                lon, lat = to_latlon.transform(proj_x, proj_y)
                max_dbz = int(round(np.max(tile[mask])))
                target_id += 1
                ac_list.append({
                    "Id": 990000 + target_id,
                    "Icao": f"{0x4F0000 + target_id:06X}",
                    "Call": f"RNC{target_id:04X}",
                    "Reg": f"RN-{target_id:04X}{max_dbz}{pixel_count}",
                    "Type": f"RN{max_dbz}",
                    "Lat": round(float(lat), 5),
                    "Long": round(float(lon), 5),
                    "Alt": alt_ft,
                    "Spd": spd_kts,
                    "Trak": trak_deg,
                    "PosTime": now_ms
                })
    payload = {"src": 1, "feeds": [{"id": 1, "name": "SW-RainScatter"}], "srcFeed": 1, "showSil": True, "showFlg": True, "flgH": 20, "flgW": 85, "acList": ac_list, "totalAc": len(ac_list), "lastDv": str(now_ms), "stm": now_ms}
    tmp_out = OUTPUT_FILE + ".tmp"
    with open(tmp_out, "w") as out:
        json.dump(payload, out)
    os.replace(tmp_out, OUTPUT_FILE)
    print(f"Processed {latest_key.split('/')[-1]} -> {len(ac_list)} scatter nodes at {alt_ft} ft ({spd_kts} kts @ {trak_deg} deg).")

if __name__ == "__main__":
    process_radar()
