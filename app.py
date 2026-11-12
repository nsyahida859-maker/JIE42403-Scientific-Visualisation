
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Malaysia Demographic Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv(
        "malaysia_demographic_2017_2024.csv"
    )
    return df

df = load_data()

st.title("Malaysia Demographic Visualisation Dashboard")
st.caption(
    "Marriage, Live Births and Population Trends "
    "Across Malaysian States (2017–2024)"
)

st.sidebar.title("Dashboard Navigation")

page = st.sidebar.radio(
    "Select Visualization",
    [
        "1. Demographic Changes",
        "2. State Demographic Profiles",
        "3. Population Distribution"
    ]
)

states = sorted(df["state"].unique())

selected_states = st.sidebar.multiselect(
    "Select States",
    states,
    default=states
)

filtered = df[
    df["state"].isin(selected_states)
].copy()

if filtered.empty:
    st.warning("Please select at least one state.")
    st.stop()

if page == "1. Demographic Changes":

    st.header("Objective 1: Demographic Changes")

    st.write(
        "To investigate changes in marriage rates, "
        "birth rates, and population across Malaysian "
        "states before and after the COVID-19 pandemic."
    )

    comparison = filtered[
        filtered["year"].isin(
            [2017, 2018, 2019, 2022, 2023, 2024]
        )
    ].copy()

    comparison["period"] = comparison["year"].apply(
        lambda y: "Before" if y <= 2019 else "After"
    )

    summary = comparison.groupby(
        ["state", "period"],
        as_index=False
    )[["marriage_rate", "birth_rate", "population"]].mean()

    before = summary[
        summary["period"] == "Before"
    ].set_index("state")

    after = summary[
        summary["period"] == "After"
    ].set_index("state")

    results = []

    for col, label in {
        "marriage_rate": "Marriage Rate",
        "birth_rate": "Birth Rate",
        "population": "Population"
    }.items():

        changes = (
            (after[col] - before[col]) / before[col]
        ) * 100

        for state, value in changes.items():
            results.append({
                "State": state,
                "Indicator": label,
                "Change (%)": value
            })

    changes_df = pd.DataFrame(results)

    c1, c2, c3 = st.columns(3)

    for box, indicator in zip(
        [c1, c2, c3],
        ["Marriage Rate", "Birth Rate", "Population"]
    ):
        value = changes_df[
            changes_df["Indicator"] == indicator
        ]["Change (%)"].mean()

        box.metric(
            indicator + " Change",
            f"{value:+.1f}%"
        )

    fig = px.bar(
        changes_df,
        x="State",
        y="Change (%)",
        color="Indicator",
        barmode="group",
        title="Demographic Changes Before and After COVID-19"
    )

    fig.update_layout(
        height=600,
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Interpretation")

    st.write(
        "Birth rates declined across Malaysian states "
        "between the two periods. Marriage rates showed "
        "mixed patterns, while population increased in "
        "several states despite declining birth rates."
    )

elif page == "2. State Demographic Profiles":

    st.header("Objective 2: State Demographic Profiles")

    st.write(
        "To identify differences in demographic profiles "
        "among Malaysian states based on marriage rates, "
        "birth rates, and population in 2024."
    )

    data = filtered[
        filtered["year"] == 2024
    ].copy()

    indicators = [
        "marriage_rate",
        "birth_rate",
        "population"
    ]

    for col in indicators:
        minimum = data[col].min()
        maximum = data[col].max()

        if maximum > minimum:
            data[col + "_scaled"] = (
                (data[col] - minimum) /
                (maximum - minimum)
            )
        else:
            data[col + "_scaled"] = 0.5

    data = data.sort_values("state")
    data["state_id"] = range(1, len(data) + 1)

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Highest Marriage Rate",
        data["marriage_rate"].max()
    )

    c2.metric(
        "Highest Birth Rate",
        data["birth_rate"].max()
    )

    c3.metric(
        "Total Population",
        f"{data['population'].sum():,.0f}"
    )

    fig = px.parallel_coordinates(
        data,
        dimensions=[
            "marriage_rate_scaled",
            "birth_rate_scaled",
            "population_scaled"
        ],
        color="state_id",
        color_continuous_scale="Viridis",
        labels={
            "marriage_rate_scaled": "Marriage Rate",
            "birth_rate_scaled": "Birth Rate",
            "population_scaled": "Population"
        },
        title="Demographic Profiles Across Malaysian States (2024)"
    )

    fig.update_layout(height=600)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Interpretation")

    st.write(
        "The visualization shows differences in "
        "demographic profiles among Malaysian states. "
        "Higher marriage rates do not necessarily "
        "correspond to higher birth rates or population."
    )

else:

    st.header("Objective 3: Population Distribution")

    st.write(
        "To examine how population is distributed "
        "across Malaysian states and explore differences "
        "in marriage and birth rates in 2024."
    )

    data = filtered[
        filtered["year"] == 2024
    ].copy()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Population",
        f"{data['population'].sum():,.0f}"
    )

    c2.metric(
        "Average Birth Rate",
        f"{data['birth_rate'].mean():.2f}"
    )

    c3.metric(
        "Average Marriage Rate",
        f"{data['marriage_rate'].mean():.2f}"
    )

    fig = px.treemap(
        data,
        path=["state"],
        values="population",
        color="birth_rate",
        color_continuous_scale="RdYlBu_r",
        custom_data=[
            "marriage_rate",
            "birth_rate",
            "population"
        ],
        title="Population Distribution and Demographic Indicators (2024)"
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Marriage Rate: %{customdata[0]:.2f}<br>"
            "Birth Rate: %{customdata[1]:.2f}<br>"
            "Population: %{customdata[2]:,.0f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(height=650)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Interpretation")

    st.write(
        "Selangor has the largest population, "
        "while Terengganu records a high birth rate. "
        "Population size does not necessarily correspond "
        "to higher birth rates."
    )

st.divider()

st.caption(
    "Data Source: Department of Statistics Malaysia "
    "(OpenDOSM) | Period: 2017–2024"
)
