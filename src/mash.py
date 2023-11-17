import pandas as pd
import streamlit as st
from datetime import datetime
import altair as alt

def log_me(msg):
    print(f'{datetime.now()} {msg}')


def get_mash_data():
    mash_df = pd.read_csv('./tmp/MASH_Old and New.csv')
    # pd.read_csv('https://drive.google.com/file/d/1I48S6V5aeoSNSKo4cJywrQY1nZUFX17Q/view?usp=sharing', names=['Spend', 'Geography', 'Media Vertical', 'Media Name', 'Campaign Id', 'Product Category'])

    # mash_pan = mash_df[mash_df['Geography'] == 'All India']
    # if len(mash_pan) > 0:
    #     mash_df = mash_df[mash_df['Geography'] != 'All India'] # Removed pan india geography
    #     cities = ('Bengaluru', 'Delhi', 'Mumbai', 'Chennai', 'Pune', 'Hyderabad')
    #     new_rows = []
    #     for index, row in mash_pan.iterrows():
    #         for c in cities:
    #             row['Geography'] = c
    #             row_dict = row.to_dict()
    #             new_rows.append(row_dict)
    #     mash_df = pd.concat([mash_df, pd.DataFrame(new_rows)])

    return mash_df


def parse_vertical_data(parm_mash_df, filter_product=None, filter_geo=None):
    mash_df = parm_mash_df.copy(deep=True)
    if filter_product is not None:
        mash_df = mash_df[mash_df['Product Category'] == filter_product]
    if filter_geo is not None:
        mash_df = mash_df[mash_df['Geography'] == filter_geo]

    if len(mash_df) == 0:
        return None, 0

    sort_order = {'Newspaper': 0, 'Magazine': 1, 'Cinema': 2, 'Influencer Marketing': 3, 'Television': 4, 'Nontraditional': 5, 'Radio': 6, 'Airport': 7, 'Outdoor': 8, 'Digital': 9}
    filtered_df = mash_df[['Media Vertical', 'Campaign Id']].drop_duplicates().groupby('Media Vertical').count().reset_index()
    filtered_df.columns = ['Media Vertical', 'Campaign Count']
    filtered_df['Campaign Percentage'] = filtered_df['Campaign Count'].map(lambda x: round((x * 100) / filtered_df['Campaign Count'].sum()))
    filtered_df = filtered_df.sort_values(by=['Media Vertical'], key=lambda x: x.map(sort_order), ascending=True).reset_index(drop=True)
    nof_campaigns = filtered_df['Campaign Count'].sum()

    return filtered_df[['Media Vertical', 'Campaign Percentage']], nof_campaigns


def parse_sub_verticaSl_data(parm_mash_df, vertical, filter_product=None, filter_geo=None):
    mash_df = parm_mash_df[parm_mash_df['Media Vertical'] == vertical].copy(deep=True)
    if filter_product is not None:
        mash_df = mash_df[mash_df['Product Category'] == filter_product]
    if filter_geo is not None:
        mash_df = mash_df[mash_df['Geography'] == filter_geo]

    if len(mash_df) == 0:
        return None, 0

    mash_df['Sub Vertical'] = mash_df[['Media Name']].map(lambda x: x.rstrip('/').split('/')[-1])
    filtered_df = mash_df[['Sub Vertical', 'Campaign Id']].drop_duplicates().groupby('Sub Vertical').count().reset_index()
    filtered_df.columns = ['Sub Vertical', 'Campaign Count']
    filtered_df['Campaign Percentage'] = filtered_df['Campaign Count'].map(lambda x: round((x * 100) / filtered_df['Campaign Count'].sum()))
    filtered_df = filtered_df.sort_values(by=['Campaign Percentage'], ascending=False).reset_index(drop=True)

    return filtered_df[['Sub Vertical', 'Campaign Percentage']]



def get_new_mash_data():
    pass


def frame_header():
    header = 'Media Popularity'
    if st.session_state.selection_prod == None and st.session_state.selection_geo == None:
        header += ' Report'
    if st.session_state.selection_prod != None:
        header += f' for {st.session_state.selection_prod} Category'
    if st.session_state.selection_geo != None:
        header += f' in {st.session_state.selection_geo}'

    return header


def main():
    mash_df = get_mash_data()
    products = tuple(mash_df['Product Category'].drop_duplicates().sort_values().to_list())
    geo = tuple(mash_df['Geography'].drop_duplicates().drop_duplicates().sort_values().to_list())

    if 'selection_prod' not in st.session_state:
        st.session_state.selection_prod = None
    if 'selection_geo' not in st.session_state:
        st.session_state.selection_geo = None

    with st.container():
        if "visibility" not in st.session_state:
            st.session_state.visibility = "visible"
            st.session_state.disabled = False

        r11, r12 = st.columns(2)
        with r11:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.selection_prod = st.selectbox("Product Category", tuple(products), index=None, placeholder='Choose an option')
                log_me(f'Selection Product state is {st.session_state.selection_prod}')
            with c2:
                st.session_state.selection_geo = st.selectbox("Geography", tuple(geo), index=None, placeholder='Choose an option')
                log_me(f'Selection Geo state is {st.session_state.selection_geo}')
            with c3:
                pass
        with r12:
            pass

        filtered_mash, nof_campains = parse_vertical_data(mash_df, filter_product=st.session_state.selection_prod, filter_geo=st.session_state.selection_geo)

        r21, r22 = st.columns(2)
        with r21:
            st.header(frame_header())
            log_me(frame_header())
        with r22:
            st.header("Historic Campaigns: {}".format(nof_campains))

    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            # st.table(filtered_mash)
            for i, row in filtered_mash.iterrows():
                st.progress(row['Campaign Percentage'])
                sub_vertical = parse_sub_verticaSl_data(mash_df, row['Media Vertical'], filter_product=st.session_state.selection_prod, filter_geo=st.session_state.selection_geo)
                with st.expander(f"{row['Media Vertical']}      {row['Campaign Percentage']}%"):
                    for j, sub_row in sub_vertical.iterrows():
                        if j > 10:
                            break
                        st.progress(sub_row['Campaign Percentage'])
                        st.write(f"{sub_row['Sub Vertical']} {sub_row['Campaign Percentage']}%")

        with c2:
            pass


if __name__ == '__main__':
    st.set_page_config(
        page_title="Mash",
        page_icon="🧊",
        layout="wide",
    )
    st.markdown(
        """
        <style>
            .stProgress > div > div > div > div {
                background-color: green;
            }
            .stProgress > div > div > div {
                height: 15px; 
            }
            [data-testid="stExpander"] details {
                border-style: none;
            }
        </style>""",
        unsafe_allow_html=True,
    )
    st.title(body='Media Advertising Spend Hub (MASH)')
    main()
