import pandas as pd

athlete = pd.read_csv('athlete_events.csv')
region = pd.read_csv('noc_regions.csv')

def preprocess():
    global athlete, region

    # Keep only Summer Olympics
    athlete_summer = athlete[athlete['Season'] == 'Summer']

    # Merge with regions
    athlete_summer = athlete_summer.merge(region, on='NOC', how='left')

    # Drop duplicates
    athlete_summer.drop_duplicates(inplace=True)

    # Add medal dummy columns (0/1)
    athlete_summer = pd.concat(
        [athlete_summer, pd.get_dummies(athlete_summer['Medal'])],
        axis=1
    )

    return athlete_summer
