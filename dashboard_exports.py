import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(page_title="Agriculture Trade Dashboard", layout="wide")

# Load data (relative paths)
export_df = pd.read_csv(r'D:\cls\task\data\export_df_converted.csv')
# إعداد أهم 5 شركاء لكل منتج ولكل دولة (من نفس export_df)
top_5_partners_each=pd.read_csv(r'D:\cls\task\data\top_5_partners_each.csv')
top_5_partners= pd.read_csv(r'D:\cls\task\data\top_5_partners.csv')
top_partners = export_df.groupby(['Product', 'Reporter', 'Partner'])['Value'].sum().reset_index()
top_partners_sorted = top_partners.sort_values(['Product', 'Reporter', 'Value'], ascending=[True, True, False])
top_5_partners_each = top_partners_sorted.groupby(['Product', 'Reporter']).head(5)
comparison_table = pd.read_excel(r'D:\cls\task\data\comparison_table.xlsx')

# Define filters options
products = export_df['Product'].unique().tolist()
countries = export_df['Reporter'].unique().tolist()
years = sorted(export_df['Year'].unique())

# Sidebar navigation
page = st.sidebar.radio("Navigation", [
    "🏠 Home",
    "📦 Export Analysis",
    "🌍 Top Trading Partners",
    "📊 Comparison Table",
    "📌 Summary"
])

# ---------- Home Page ----------
if page == "🏠 Home":
    st.title("Agriculture Trade Dashboard – India vs Turkey")
    st.markdown("""
    ### Project Objective
    Compare price and export data of wheat and onions between India and Turkey.

    ### Data Sources
    - Source: FAOSTAT
    - Products: Wheat and Onions

    ### Notes
    Data cleaned and organized for analysis and visualization.
    """)

# ---------- Export Analysis Page ----------
elif page == "📦 Export Analysis":
    st.title("Export Analysis")

    # Filters
    product_filter = st.selectbox("Select Product", products)
    country_filter = st.multiselect("Select Country/Countries", countries, default=countries)
    year_range = st.slider("Select Year Range", min_value=min(years), max_value=max(years), value=(min(years), max(years)))

    df_filtered = export_df[
        (export_df['Product'] == product_filter) &
        (export_df['Reporter'].isin(country_filter)) &
        (export_df['Year'].between(year_range[0], year_range[1]))
    ]

    st.subheader("Export Quantity Over Years")
    df_quantity = df_filtered[df_filtered['Measure'] == 'Export quantity']
    plt.figure(figsize=(10, 4))
    sns.lineplot(data=df_quantity, x='Year', y='Value', hue='Reporter', marker='o')
    plt.ylabel("Export Quantity")
    plt.xlabel("Year")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()

    st.subheader("Export Value Over Years")
    df_value = df_filtered[df_filtered['Measure'] == 'Export value']
    plt.figure(figsize=(10, 4))
    sns.lineplot(data=df_value, x='Year', y='Value', hue='Reporter', marker='o')
    plt.ylabel("Export Value (USD)")
    plt.xlabel("Year")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()

    # Calculate Unit Price (USD/ton)
    st.subheader("Unit Price (USD/ton) Over Time – Calculated Live")
    quantity_df = df_filtered[df_filtered['Measure'] == 'Export quantity']
    value_df = df_filtered[df_filtered['Measure'] == 'Export value']

    group_cols = ['Reporter', 'Partner', 'Product', 'Year']
    merged_df = pd.merge(
        quantity_df,
        value_df,
        on=group_cols,
        suffixes=('_qty', '_val')
    )

    merged_df['USD_per_ton'] = merged_df['Value_val'] / merged_df['Value_qty']
    merged_df = merged_df[(merged_df['USD_per_ton'] > 0) & (merged_df['USD_per_ton'] < 10000)]

    avg_price_dynamic = merged_df.groupby(['Year', 'Reporter'])['USD_per_ton'].mean().reset_index()

    plt.figure(figsize=(10, 4))
    sns.lineplot(data=avg_price_dynamic, x='Year', y='USD_per_ton', hue='Reporter', marker='o')
    plt.ylabel("Unit Price (USD/ton)")
    plt.xlabel("Year")
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()

    st.subheader("Quantity and Value Comparison Between India and Turkey")
    comp_table = df_filtered.pivot_table(index='Year', columns='Reporter', values='Value', aggfunc='sum')
    st.dataframe(comp_table.style.format("{:,.0f}"))

    # Download filtered data
    st.download_button(
        label="Download Filtered Data as CSV",
        data=df_filtered.to_csv(index=False).encode('utf-8'),
        file_name=f'export_data_filtered_{product_filter}.csv',
        mime='text/csv'
    )

if page == "🌍 Top Trading Partners":
    st.title("Top Trading Partners")

    st.subheader("Top 5 Export Partners for India and Türkiye (by Quantity)")

    # تحميل البيانات من الملف المحفوظ مسبقًا
    top_5_partners_each = pd.read_csv(r"D:\cls\task\data\top_5_partners.csv")

    # فلترة للهند وتركيا فقط
    top_5_filtered = top_5_partners_each[top_5_partners_each['Reporter'].isin(['India', 'Türkiye'])]

    # رسم الأعمدة المجمعة
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_5_filtered, x='Partner', y='Value', hue='Reporter', ax=ax)
    ax.set_title('Top 5 Export Partners by Quantity for India and Turkey')
    ax.set_xlabel('Partner Country')
    ax.set_ylabel('Export Quantity')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    # رسم كل دولة على حدة في عمودين بجانب بعض
    st.subheader("Top 5 Export Partners - Individual Charts")

    countries = top_5_filtered['Reporter'].unique()

    cols = st.columns(len(countries))  # عمود لكل دولة (عادة 2)

    for i, country in enumerate(countries):
        subset = top_5_filtered[top_5_filtered['Reporter'] == country]
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=subset, x='Partner', y='Value', ax=ax)
        ax.set_title(f'Top 5 Export Partners for {country}')
        ax.set_xlabel('Partner')
        ax.set_ylabel('Export Quantity')
        plt.xticks(rotation=45)
        plt.tight_layout()
        cols[i].pyplot(fig)

elif page == "📊 Comparison Table":
    st.title("Comparison Table")

    countries = comparison_table['Country'].unique()
    country_filter = st.multiselect("Select Countries", countries, default=list(countries[:2]))  # تقدر تحط اختيار افتراضي لدولتين

    if country_filter:
        df_comp_filtered = comparison_table[comparison_table['Country'].isin(country_filter)]
        st.dataframe(df_comp_filtered)
    else:
        st.warning("Please select at least one country.")

    # التحميل
    import io
    output = io.BytesIO()
    comparison_table.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    st.download_button(
        label="Download Comparison Table as Excel",
        data=output,
        file_name='comparison_table.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )




# ---------- Summary Page ----------
elif page == "📌 Summary":
    st.title("Summary and Recommendations")

    st.markdown("""
    ### Which country has more stable prices?
    - India shows more stable prices for wheat and onions compared to Turkey.

    ### Who exports more?
    - Turkey leads in quantity and value of onion exports; India leads in wheat exports.

    ### Which market seems more promising?
    - India's wheat market appears promising due to stable prices and increasing quantity.

    ### Potential Risks or Opportunities?
    - Price volatility in Turkey's onion market could pose risks.
    - Growth opportunities depend on price stability and product quality improvement.
    """)
