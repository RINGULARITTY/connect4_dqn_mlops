import streamlit as st

ROWS, COLS = 6, 7
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

def display_grid():
    st.title('Connect 4')

    for row in grid:
        row_display = []
        for cell in row:
            if cell == 0:
                row_display.append("⚪")
            elif cell == 1:
                row_display.append("🔴")
            else:
                row_display.append("🟡")
        
        row_str = ' '.join(row_display)
        st.markdown(f"<span style='font-size: 60px'>{row_str}</span>", unsafe_allow_html=True)
    
    button_html = ''.join(f'<button class="grid-button" id="button{col}" style="width: 85px; height: 50px; margin-right: 35px">{col}</button>' for col in range(COLS))

    st.markdown(
        f'<div style="display: flex; justify-content: start; width: {85*COLS}px;">{button_html}</div>',
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    display_grid()
