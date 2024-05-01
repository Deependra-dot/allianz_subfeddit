from datetime import datetime

# Unix timestamp to convert
timestamp = 1714526641

# Convert Unix timestamp to UTC datetime object
utc_time = datetime.fromtimestamp(timestamp)

# Print the UTC time in a specific format
utc_time_str = utc_time.strftime('%Y-%m-%d %H:%M:%S')
print(utc_time_str)
