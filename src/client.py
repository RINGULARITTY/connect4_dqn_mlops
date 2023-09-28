import streamlit as st
import requests
from time import sleep
import numpy as np
import plotly.graph_objects as go
import pandas as pd

host = "http://51.77.192.29"
port = 5656

if 'log_step' not in st.session_state:
    st.session_state['log_step'] = 0
    st.session_state['player_key'] = ""
    st.session_state['picked_model'] = ""
    st.session_state['board'] = []
    st.session_state['player_turn'] = -1
    st.session_state['winner'] = ""

if st.session_state['log_step'] == -1:
    response = requests.post(f'{host}:{port}/get_server_info', json={'admin_password': "admin"})
    if response.status_code == 200:
        json_response = response.json()
        st.write(f"Games running : {json_response['players_amount']}")
        
        st.write("Picked models :")
        total = sum(json_response['picked_models'].values())
        for k, v in json_response['picked_models'].items():
            st.write(f"\t- {k}: {v} ({round(100 * v / total, 2)}%)")
        
        total_requests = json_response['requests_amount'][0]
        st.write(f"Total requests: {total_requests} ({100 * round(json_response['requests_amount'][1] / total_requests, 2)}% success)")
    
        st.divider()
    
        st.write(f"Requests visualization")
        time_selector = st.selectbox('Delta time', ['Minutes', 'Hours', 'Days'])
    
        data = []
        for name, req_list in json_response["requests_timeline"].items():
            for status, dt in req_list:
                data.append({'name': name, 'status': 1 if status else -1, 'datetime': dt})
        
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['datetime'])

        if time_selector == 'Minutes':
            df['time_group'] = df['datetime'].dt.floor('T')
        elif time_selector == 'Hours':
            df['time_group'] = df['datetime'].dt.floor('H')
        elif time_selector == 'Days':
            df['time_group'] = df['datetime'].dt.floor('D')

        fig = go.Figure()
        for name in json_response["requests_timeline"].keys():
            filtered_df = df[df['name'] == name]
            grouped = filtered_df.groupby(['time_group', 'status']).size().reset_index(name='counts')
            for status in [-1, 1]:
                status_df = grouped[grouped['status'] == status]
                fig.add_trace(go.Bar(x=status_df['time_group'], y=status_df['counts'] * status, name=f"{name} {'Success' if status == 1 else 'Fail'}"))

        fig.update_layout(barmode='relative', title='Requests over time')
        st.plotly_chart(fig)
    else:
        st.error('Connection failed')

if st.session_state['log_step'] == 0:
    password = st.text_input("Password :", type="password")
    if st.button("Connect"):
        if password == "admin":
            st.session_state['log_step'] = -1
            st.rerun()
        if password == "error":
            response = requests.post(f'{host}:{port}/connect', json={'password': "prout"})
            st.rerun()
        response = requests.post(f'{host}:{port}/connect', json={'password': password})

        if response.status_code == 200:
            json_response = response.json()
            st.session_state['player_key'] = json_response["message"]
            st.session_state['log_step'] = 1

            st.rerun()
        else:
            st.error('Connection failed')

if st.session_state['log_step'] > 0:
    st.write(f"Player key : {st.session_state['player_key']}")

if st.session_state['log_step'] == 1:
    if 'existing_models' not in st.session_state:
        response = requests.post(f'{host}:{port}/get_existing_models', json={'player_key': st.session_state['player_key']})
        if response.status_code == 200:
            json_response = response.json()
            st.session_state['existing_models'] = json_response["message"]
            st.rerun()
        else:
            st.error('Connection failed')
    else:
        selected_model = st.selectbox("Pick an existing model", st.session_state['existing_models'])
        if st.button("Take this model"):
            response = requests.post(f'{host}:{port}/pick_model', json={
                'player_key': st.session_state['player_key'],
                'model_name': selected_model
            })
            if response.status_code == 200:
                st.session_state['picked_model'] = selected_model
                st.session_state['board'] = response.json()["message"]
                st.session_state['log_step'] = 2
                st.rerun()
            else:
                st.error('Connection failed')
        st.divider()
        st.write("Or create a new model")
        width = st.number_input("Width", 4, 10)
        height = st.number_input("Height", 4, 10)

        if st.button("Create new model"):
            pass

if st.session_state['log_step'] >= 2:
    st.write(f"Picked model : {st.session_state['picked_model']}")

if st.session_state['log_step'] == 2:
    ROWS, COLS = len(st.session_state['board']), len(st.session_state['board'][0])
    
    def display_grid():
        for row in st.session_state['board'][::-1]:
            row_display = []
            for cell in row:
                if cell == 0:
                    row_display.append("⚪")
                elif cell == 1:
                    row_display.append("🔴")
                else:
                    row_display.append("🟡")
            
            row_str = ' '.join(row_display)
            st.markdown(f"<span style='font-size: 60px;'>{row_str}</span>", unsafe_allow_html=True)
        
        cols = st.columns(COLS)
        for col in range(COLS):
            if cols[col].button(f"{col}"):
                if st.session_state['player_turn'] == 1:
                    response = requests.post(f'{host}:{port}/play_player', json={
                        'player_key': st.session_state['player_key'],
                        'action': col
                    })
                    
                    if response.status_code == 200:
                        json_response = response.json()["message"]
                        st.session_state['board'] = json_response["board"]
                        if json_response["finished"]:
                            st.session_state['player_turn'] = 0
                            if np.any(np.array(st.session_state['board']) == 0):
                                st.session_state['winner'] = "You won !!"
                            else:
                                st.session_state['winner'] = "Draw"
                            st.rerun()
                        st.session_state['player_turn'] *= -1
                        st.rerun()
                    else:
                        st.error('Connection failed')

    display_grid()
    if st.session_state['winner'] != "":
        st.write(st.session_state['winner'])
    else:
        sleep(0.5)
        if st.session_state['player_turn'] == -1:
            response = requests.post(f'{host}:{port}/play_model', json={'player_key': st.session_state['player_key']})
            if response.status_code == 200:
                json_response = response.json()["message"]
                st.session_state['board'] = json_response["board"]
                if json_response["finished"]:
                    st.session_state['player_turn'] = 0
                    if np.any(np.array(st.session_state['board']) == 0):
                        st.session_state['winner'] = "Model won !!"
                    else:
                        st.session_state['winner'] = "Draw"
                    st.rerun()
                st.session_state['player_turn'] *= -1
                st.rerun()
            else:
                st.error('Connection failed')