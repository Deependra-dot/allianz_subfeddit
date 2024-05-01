from datetime import datetime


"""
this is a util file to find out the utc time corresponding to the unix timestamp
"""
# Unix timestamp to convert
time_stamp = 1714526641

# Convert Unix timestamp to UTC datetime object
utc_time = datetime.fromtimestamp(time_stamp)

# Print the UTC time in a specific format
utc_time_str = utc_time.strftime('%Y-%m-%d %H:%M:%S')
print(utc_time_str)
