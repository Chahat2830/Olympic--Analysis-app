import numpy as np
import pandas as pd


def fetch_medal_tally(df, year, country):
    if year == 'Overall' and country == 'Overall':
        temp_df = df
        x = temp_df.groupby('region').sum(numeric_only=True)[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()

    elif year == 'Overall' and country != 'Overall':
        temp_df = df[df['region'] == country]
        x = temp_df.groupby('Year').sum(numeric_only=True)[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()

    elif year != 'Overall' and country == 'Overall':
        temp_df = df[df['Year'] == int(year)]
        x = temp_df.groupby('region').sum(numeric_only=True)[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()

    else:
        temp_df = df[(df['Year'] == int(year)) & (df['region'] == country)]
        x = temp_df.groupby('region').sum(numeric_only=True)[['Gold', 'Silver', 'Bronze']].reset_index()

    x['Total'] = x['Gold'] + x['Silver'] + x['Bronze']
    return x


def country_year_list(df):
    years = sorted(df['Year'].unique().tolist())
    years.insert(0, 'Overall')

    country = sorted(np.unique(df['region'].dropna().values).tolist())
    country.insert(0, 'Overall')

    return country, years


def data_over_time(df, col_name):
    temp_df = (
        df.drop_duplicates(['Year', col_name])['Year']
        .value_counts()
        .reset_index()
    )
    temp_df.columns = ['Edition', col_name]
    temp_df = temp_df.sort_values('Edition')
    return temp_df

def most_successful(df, filter_value, filter_type='sport'):
    """
    Returns top 10 most successful athletes based on medals.
    filter_type can be:
      - 'sport'   → filter by sport
      - 'country' → filter by country (region)
    """
    temp_df = df.dropna(subset=['Medal']).copy()

    if filter_type == 'sport' and filter_value != 'Overall':
        temp_df = temp_df[temp_df['Sport'].str.lower() == filter_value.lower()]

    elif filter_type == 'country':
        # Case-insensitive + partial match for region name
        temp_df = temp_df[temp_df['region'].str.contains(filter_value, case=False, na=False)]

    # If no medals found, return empty DataFrame safely
    if temp_df.empty:
        return pd.DataFrame(columns=['Name', 'Medals', 'Sport', 'region'])

    # Count medals per athlete
    top_athletes = temp_df['Name'].value_counts().reset_index().head(10)
    top_athletes.columns = ['Name', 'Medals']

    # Merge with info to get sport and region
    info = df[['Name', 'Sport', 'region']].drop_duplicates(subset=['Name'])
    top_athletes = top_athletes.merge(info, on='Name', how='left')

    return top_athletes[['Name', 'Medals', 'Sport', 'region']]


def yearwise_medal(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()
    temp_df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'],
        inplace=True
    )

    new_df = temp_df[temp_df['region'] == country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()
    return final_df


def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()
    temp_df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'],
        inplace=True
    )

    new_df = temp_df[temp_df['region'] == country]

    pt = new_df.pivot_table(
        index='Sport',
        columns='Year',
        values='Medal',
        aggfunc='count'
    ).fillna(0).astype(int)

    return pt


def weight_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region']).copy()
    athlete_df['Medal'].fillna('No Medal', inplace=True)

    if sport != 'Overall':
        return athlete_df[athlete_df['Sport'] == sport]
    else:
        return athlete_df


def men_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region']).copy()

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='outer').fillna(0)
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)

    return final
