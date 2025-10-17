import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.figure_factory as ff

import preprosesing
import helper

# Load and preprocess data
df = preprosesing.preprocess()

st.sidebar.title('🏅 Olympic Analysis Dashboard')

user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# ----------------- MEDAL TALLY -----------------
if user_menu == 'Medal Tally':
    st.sidebar.header('Medal Tally')

    country, years = helper.country_year_list(df)
    selected_country = st.sidebar.selectbox('Select Country', country)
    selected_year = st.sidebar.selectbox('Select Year', years)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title('🏆 Overall Medal Tally')
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f"Medal Tally in {selected_year}")
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f"Overall Performance of {selected_country}")
    else:
        st.title(f"{selected_country}'s Performance in {selected_year}")

    st.dataframe(medal_tally)

# ----------------- OVERALL ANALYSIS -----------------
elif user_menu == 'Overall Analysis':
    st.title("📊 Overall Olympic Analysis")

    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("🏟️ Editions", editions)
    col2.metric("🌆 Host Cities", cities)
    col3.metric("🏅 Sports", sports)

    col4, col5, col6 = st.columns(3)
    col4.metric("🎯 Events", events)
    col5.metric("🌍 Nations", nations)
    col6.metric("👨‍💼 Athletes", athletes)

    # Trend graphs
    for col in ['region', 'Event', 'Sport', 'Name']:
        data = helper.data_over_time(df, col)
        fig = px.line(data, x='Edition', y=col, markers=True, title=f"{col.capitalize()} Over Time")
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap: Events per sport over time
    st.subheader("🔥 Events Over Time by Sport")
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    pivot = x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int)

    fig, ax = plt.subplots(figsize=(20, 20))
    sns.heatmap(pivot, annot=True, cmap="YlGnBu", ax=ax)
    st.pyplot(fig)

    # Top athletes
    sport_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
    selected_sport = st.selectbox("Select Sport", sport_list)
    x = helper.most_successful(df, selected_sport)
    st.subheader(f"🏆 Top 10 Most Successful Athletes in {selected_sport}")
    st.dataframe(x)

# ----------------- COUNTRY-WISE ANALYSIS -----------------
elif user_menu == 'Country-wise Analysis':
    st.title("🌎 Country-wise Olympic Analysis")

    country_list = sorted(df['region'].dropna().unique().tolist())
    selected_country = st.selectbox("Select a Country", country_list)

    country_df = helper.yearwise_medal(df, selected_country)

    if not country_df.empty:
        fig = px.line(country_df, x='Year', y='Medal', markers=True,
                      title=f"{selected_country} - Medal Trend Over Years")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No medal data available for {selected_country}.")

    st.subheader("🔥 Events Heatmap (Sport vs Year)")
    pt = helper.country_event_heatmap(df, selected_country)
    if not pt.empty:
        fig, ax = plt.subplots(figsize=(20, 20))
        sns.heatmap(pt, annot=True, cmap="YlGnBu", ax=ax)
        st.pyplot(fig)
    else:
        st.warning(f"No event data available for {selected_country}.")

    st.subheader(f"🏅 Top 10 Most Successful Athletes from {selected_country}")
    top_athletes = helper.most_successful(df, selected_country, filter_type='country')

    if not top_athletes.empty:
        st.dataframe(top_athletes)
    else:
        st.info(f"No athlete data available for {selected_country}.")


# ----------------- ATHLETE-WISE ANALYSIS -----------------
elif user_menu == 'Athlete-wise Analysis':
    st.title("👨‍🎓 Athlete-wise Analysis")

    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot(
        [x1, x2, x3, x4],
        ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
        show_hist=False, show_rug=False
    )
    fig.update_layout(title="Age Distribution by Medal Type", xaxis_title="Age", yaxis_title="Density")
    st.plotly_chart(fig, use_container_width=True)

    sport_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
    selected_sport = st.selectbox("Select Sport", sport_list)

    temp_df = helper.weight_height(df, selected_sport)
    fig, ax = plt.subplots()
    sns.scatterplot(x='Weight', y='Height', data=temp_df, hue='Medal', style='Sex', s=100, ax=ax)
    plt.title(f"Weight vs Height ({selected_sport})")
    st.pyplot(fig)

    final = helper.men_women(df)
    fig = px.line(final, x='Year', y=['Male', 'Female'], title="Male vs Female Participation Over Years")
    st.plotly_chart(fig, use_container_width=True)
