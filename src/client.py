import streamlit as st
import requests as rq

url = ...

st.title("Connect 4")

# Initier la grille de jeu
ROWS, COLS = 6, 7
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

def display_grid():
    st.write("Connect 4")
    
    # Afficher les boutons pour jouer un pion
    col_selected = None
    for col in range(COLS):
        if st.button(f"Play in column {col}"):
            col_selected = col
    st.write("Selected column:", col_selected)

    # Mettre à jour la grille (c'est ici que vous ajouteriez la logique du jeu)
    

    # Afficher la grille
    for row in grid:
        row_display = []
        for cell in row:
            if cell == 0:
                row_display.append("⚪")  # Cellule vide
            elif cell == 1:
                row_display.append("🔴")  # Pion rouge
            else:
                row_display.append("🟡")  # Pion jaune
        st.write(" ".join(row_display))

if __name__ == "__main__":
    display_grid()