"""
Holds information about time on Mundus
"""

DAYS = ['Morndas', 'Tirdas', 'Middas', 'Turdas', 'Fredas', 'Loredas', 'Sundas']

MONTHS = [
    'Morning Star', "Sun's Dawn", 'First Seed', "Rain's Hand", 'Second Seed',
    'Mid Year', "Sun's Height", 'Last Seed', 'Heartfire', 'Frostfall',
    "Sun's Dusk", 'Evening Star'
]

# starting mud time is 4E100 (10 years after oblivion crisis and 190 years before the events of the Dragonborn, and 5 years after Red Year)
START_ERA = 4
START_YEAR = 10

DAYS_IN_WEEK = 7
DAYS_IN_MONTH = 31
DAYS_IN_YEAR = 364

# month: {day: holiday_name}
HOLIDAYS = {
    # Morning Star
    0: {
        1: 'New Life Festival',
        2: 'Scour Day',
        12: "Sound Wind's Prayer",
        16: "The Day of Lights",
        18: "Waking Day"
    },
    # Sun's Dawn
    1: {
        2: "Mad Pelagius",
        5: "Othroktide",
        8: "Day of Release",
        16: "Heart's Day",
        27: "Perserverance Day",
        28: "Aduros Nau"
    },

    # First Seed
    2: {
        7: "First Planting",
        9: "The Day of Waiting",
        21: "Hogithum",
        25: "Flower Day",
        26: "Festival of Blades"
    },

    # Rain's Hand
    3: {
        1: "Gardtide",
        13: "The Day of the Dead",
        20: "The Da of Shame",
        28: "Jester's Day"
    },

    # Second Seed
    4: {
        7: "Second Planting",
        9: "Marukh's Day",
        20: "The Fire Festival",
        30: "Fishing Day"
    },

    # Mid Year
    5: {
        1: "Drigh R'Zimb Day",
        16: "Mid Year Celebration",
        23: "Dancing Day",
        24: "Tibedetha"
    }
}