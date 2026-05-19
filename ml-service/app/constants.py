FEATURE_COLUMNS = [
    "hour_of_day",
    "weekday",
    "motion_hall",
    "motion_living",
    "temperature",
    "light_level",
    "tv_on",
    "minutes_idle",
]

TARGET_CLASSES = ["day", "night", "away", "movie"]
TARGET_COLUMN = "scenario"
