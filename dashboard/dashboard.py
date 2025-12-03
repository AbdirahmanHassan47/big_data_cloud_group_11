import streamlit as st
from connect_duck_pond import query_job_listings
from plots import create_bar_chart

st.set_page_config(layout="wide")

def layout():
    st.title("Yrkesfakta vägledaren")

    choices = {
        "Pedagogik": "mart_p",
        "Säkerhet och bevakning": "mart_sb",
        "Transport, distribution, lager": "mart_tdl",
    }

    selected_occupation_field = st.selectbox(
        "Välj yrkeskategori", options=list(choices.keys()), index=None
    )
    if not selected_occupation_field:
        st.info("Välj en yrkeskategori för att visa data.")
        return

    table = choices[selected_occupation_field]
    df_all = query_job_listings(f'SELECT * FROM {table}')
    if df_all is None or df_all.empty:
        st.info(f"Ingen data i {table} ännu.")
        return

    st.dataframe(df_all, use_container_width=True)

    cols = st.columns(3)

    with cols[0]:
        st.metric(label="Total antal annonser", value=int(df_all["vacancies"].sum()))
        st.write(f"Top 10 flest yrkesroller för {selected_occupation_field}")
        df_roles = query_job_listings(f'''
            SELECT
              OCCUPATION AS "Yrkestitel",
              SUM(VACANCIES) AS "Annonser"
            FROM {table}
            GROUP BY OCCUPATION
            ORDER BY "Annonser" DESC
            LIMIT 10
        ''')
        st.dataframe(df_roles, hide_index=True)

    with cols[1]:
        df_top10_employers = query_job_listings(f'''
            SELECT
              SUM(VACANCIES) AS "Annonser",
              employer_name  AS "Arbetsgivare"
            FROM {table}
            GROUP BY employer_name
            ORDER BY "Annonser" DESC
            LIMIT 10
        ''')
        fig_top10 = create_bar_chart(
            df_top10_employers,
            x_col="Arbetsgivare",
            y_col="Annonser",
            xaxis_title="Företag",
            yaxis_title="Antal annonser",
            title="Top 10 företag med flest annonser",
        )
        st.plotly_chart(fig_top10, use_container_width=True)

    with cols[2]:
        df_top5_region = query_job_listings(f'''
            SELECT
              workplace_region AS "Region",
              SUM(vacancies)   AS "Annonser"
            FROM {table}
            GROUP BY workplace_region
            ORDER BY "Annonser" DESC
            LIMIT 5
        ''')
        fig_top5 = create_bar_chart(
            df_top5_region,
            x_col="Region",
            y_col="Annonser",
            xaxis_title="Regioner",
            yaxis_title="Antal annonser",
            title="Top 5 regioner med flest annonser",
        )
        st.plotly_chart(fig_top5, use_container_width=True)

    st.markdown("## Hitta jobbannons")
    cols2 = st.columns(2)

    with cols2[0]:
        employers = sorted(df_all["employer_name"].dropna().unique().tolist())
        selected_company = st.selectbox("Välj arbetsgivare:", employers, index=None)
        if selected_company:
            filtered = df_all[df_all["employer_name"] == selected_company]
            headlines = filtered["headline"].dropna().tolist()
            selected_headline = st.selectbox("Välj en jobbannons:", headlines, index=None)
            if selected_headline:
                html_val = filtered.loc[filtered["headline"] == selected_headline, "description_html_formatted"].values
                if len(html_val):
                    st.markdown(html_val[0], unsafe_allow_html=True)

    with cols2[1]:
        st.write("")

if __name__ == "__main__":
    layout()