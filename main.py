import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from numerize.numerize import numerize


data = pd.read_csv('user_fake_authentic_2class.csv')
new_columns = {'pos': 'posts', 'pic': 'profile picture', 'flg': 'following', 'flw': 'followers', 'bl': 'bio length',
               'lin': 'link',
               'cl': 'average caption length', 'ni': 'non image percentage', 'lt': 'location tag percentage','hc':'average hashtag count',
               'pi': 'avg_interval_between_posts_h'}
data = data.rename(columns=new_columns)
fake_profiles = data[data['class'] == 'f']
genuine_profiles = data[data['class'] == 'r']

REAL_COLOR = 'lightblue'
FAKE_COLOR = 'lightcoral'


def start_info():
    total1, total2,total3 = st.columns(3, gap='large')

    with total1:
        st.image('images/fake-news (3).png',width=100, use_column_width='Auto')
        st.metric(label='Total fake profiles', value=numerize(len(fake_profiles)))

    with total2:
        st.image('images/verified-user.png',width=100, use_column_width='Auto')
        st.metric(label='Total real profiles', value=numerize(len(genuine_profiles)))

    with total3:
        st.image('images/post.png',width=100, use_column_width='Auto')
        st.metric(label='Total posts', value=numerize(len(data['posts'])))


def create_bar_plot():
    options_columns = ['posts', 'following', 'followers']
    st.markdown("### Comparison of profile features between fake and genuine users")
    fig = go.Figure()
    categories = ['Fake profiles', 'Genuine profiles']
    x = options_columns

    for i, category in enumerate(categories):
        values = []
        for param in options_columns:
            if category == 'Fake profiles':
                value = (fake_profiles[param].sum() / len(fake_profiles))
            else:
                value = (genuine_profiles[param].sum() / len(genuine_profiles))
            values.append(value)

        fig.add_trace(go.Bar(
            x=x if i == 0 else [val for val in x],
            y=values,
            name=category,
            marker={'color': FAKE_COLOR if i == 0 else REAL_COLOR}
        ))

    fig.update_layout(
        xaxis_title='Profile features',
        yaxis_title='Average value',
        # title='Comparison of Profile Features between Fake and Real Users',
        width=600,
        height=400
    )

    fig.update_xaxes(tickangle=45)

    st.plotly_chart(fig)


def create_scatter():
    options_columns = ['following', 'followers']
    st.markdown(f"### Comparison of followers and following between genuine and fake profiles")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=genuine_profiles[options_columns[0]],
        y=genuine_profiles[options_columns[1]],
        mode='markers',
        marker=dict(color=REAL_COLOR),
        name='Genuine Profiles'
    ))
    fig.add_trace(go.Scatter(
        x=fake_profiles[options_columns[0]],
        y=fake_profiles[options_columns[1]],
        mode='markers',
        marker=dict(color=FAKE_COLOR),
        name='Fake Profiles'
    ))

    # Get user inputs for axis ranges
    x_axis_range = st.slider("X-Axis Range", min_value=min(genuine_profiles[options_columns[0]]),
                             max_value=max(genuine_profiles[options_columns[0]]),
                             value=(
                                 min(genuine_profiles[options_columns[0]]), max(genuine_profiles[options_columns[0]])),
                             key="x_range_slider",
                             help="Select the range for the X-axis")

    y_axis_range = st.slider("Y-Axis Range", min_value=min(genuine_profiles[options_columns[1]]),
                             max_value=max(genuine_profiles[options_columns[1]]),
                             value=(
                                 min(genuine_profiles[options_columns[1]]), max(genuine_profiles[options_columns[1]])),
                             key="y_range_slider",
                             help="Select the range for the Y-axis")

    col = f''' <style> div.stSlider > div[data-baseweb = "slider"] > div > div {{
        background: linear-gradient(to right, rgb(1, 183, 158) 0%, 
                                    rgb(1, 183, 158) {x_axis_range}%, 
                                    rgba(151, 166, 195, 0.25) {x_axis_range}%, 
                                    rgba(1, 166, 195, 0.25) 100%); }} </style>'''

    st.markdown(col, unsafe_allow_html=True)

    fig.update_layout(
        # title='Comparison of Followers between Genuine and Fake Profiles',
        xaxis=dict(range=x_axis_range),
        yaxis=dict(range=y_axis_range),
        width=1000,
        height=500,
        xaxis_title='following',
        yaxis_title='Followers'
    )

    st.plotly_chart(fig, use_container_width=True)


def create_interval_graph(df):
    options_columns = ['following', 'followers']

    x_axis_param = st.radio("Select X-Axis Parameter", options_columns)
    groups = []
    if x_axis_param == 'followers':
        name = 'followers groups'
        st.markdown(f"### Average interval between posts by {name}")

        for i in range(0, 100000, 10000):
            groups.append((i, i + 10000))
        df[name] = pd.cut(df['followers'], bins=[group[0] for group in groups] + [float('inf')],
                          labels=[f"{group[0]}-{group[1]}" for group in groups])
    else:
        name = 'following groups'
        st.markdown(f"### Average interval between posts by {name}")
        for i in range(0, 9000, 500):
            groups.append((i, i + 500))
        df[name] = pd.cut(df['following'], bins=[group[0] for group in groups] + [float('inf')],
                          labels=[f"{group[0]}-{group[1]}" for group in groups])

    # Create a new column to categorize followers into groups

    df['avg_interval_between_posts_d'] = df['avg_interval_between_posts_h'] / 24
    avg_interval = df.groupby([name, 'class'])['avg_interval_between_posts_d'].mean().reset_index()
    fig = go.Figure()
    colors = {'r': REAL_COLOR, 'f': FAKE_COLOR}
    for user_type in avg_interval['class'].unique():
        user_type_data = avg_interval[avg_interval['class'] == user_type]
        fig.add_trace(go.Scatter(
            x=user_type_data[name],
            y=user_type_data['avg_interval_between_posts_d'],
            mode='lines',
            name='genuine user' if user_type == 'r' else 'fake user',
            line=dict(color=colors[user_type])
        ))

    fig.update_layout(
        xaxis_title=f'{name}',
        yaxis_title='Average interval between posts (days)'
    )
    st.plotly_chart(fig)
    # Create a box plot based on the selected group
    selected_group = st.selectbox("Select gslideroup", avg_interval[name].unique())
    columns = ['followers', 'following', 'profile picture', 'bio length','average hashtag count']
    col_box = st.radio("Select parameter", columns)
    st.markdown(f"#### Comparison of profiles with {selected_group} {col_box} between Genuine and Fake Profiles ")
    fig_box = go.Figure()
    fake_users = df[(df[name] == selected_group) & (df['class'] == 'f')]
    real_users = df[(df[name] == selected_group) & (df['class'] == 'r')]
    fig_box.add_trace(go.Box(y=fake_users[col_box], name='Fake Users'))
    fig_box.add_trace(go.Box(y=real_users[col_box], name='Real Users'))

    # fig_box.add_trace(go.Box(y=fake_users['followers','following','profile picture','bio length'], name='Fake Users'))
    # fig_box.add_trace(go.Box(y=real_users['followers'], name='Real Users'))
    fig_box.update_layout(xaxis=dict(title='User Type'), yaxis=dict(title=f'{col_box}'), showlegend=True)
    st.plotly_chart(fig_box)



def main():
    st.title("Visualization Final Project")
    st.header('Fake/Authentic User Instagram')
    start_info()
    create_bar_plot()
    create_scatter()
    create_interval_graph(data)


if __name__ == "__main__":
    main()
