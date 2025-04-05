import streamlit as st
import sqlite3
import datetime

# --- Configuración de la base de datos ---
conn = sqlite3.connect('fastmed.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                role TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                doctor TEXT,
                date TEXT,
                time TEXT,
                status TEXT)''')
conn.commit()

# --- Funciones con fallas intencionales ---
def register_user(username, password, role):
    # No valida si el usuario ya existe (fallo)
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()


def login_user(username, password):
    # No valida contraseña correctamente (fallo)
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone()


def create_appointment(user_id, doctor, date, time):
    # Permite doble reserva en mismo horario (fallo)
    c.execute("INSERT INTO appointments (user_id, doctor, date, time, status) VALUES (?, ?, ?, ?, ?)",
              (user_id, doctor, date, time, "reservada"))
    conn.commit()


def get_appointments():
    c.execute("SELECT * FROM appointments")
    return c.fetchall()

# --- Interfaz Streamlit ---
st.title("FastMed - Sistema de Citas (Versión con fallos)")

menu = ["Inicio", "Registro", "Login", "Reservar Cita", "Ver Citas"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registro":
    st.subheader("Registro de Usuario")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type='password')
    role = st.selectbox("Rol", ["paciente", "medico"])
    if st.button("Registrar"):
        register_user(username, password, role)
        st.success("Usuario registrado correctamente")

elif choice == "Login":
    st.subheader("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type='password')
    if st.button("Ingresar"):
        user = login_user(username, password)
        if user:
            st.session_state['user'] = user
            st.success(f"Bienvenido {user[1]} ({user[3]})")
        else:
            st.error("Usuario no encontrado")

elif choice == "Reservar Cita":
    if 'user' not in st.session_state:
        st.warning("Debes iniciar sesión")
    else:
        st.subheader("Reservar Cita")
        doctor = st.selectbox("Médico", ["Dra. Salazar", "Dr. Gómez"])
        date = st.date_input("Fecha", min_value=datetime.date.today())
        time = st.selectbox("Hora", ["09:00", "10:00", "11:00"])
        if st.button("Reservar"):
            create_appointment(st.session_state['user'][0], doctor, str(date), time)
            st.success("Cita reservada")

elif choice == "Ver Citas":
    st.subheader("Listado de Citas")
    citas = get_appointments()
    for cita in citas:
        st.write(f"ID: {cita[0]} | Usuario ID: {cita[1]} | Dr: {cita[2]} | Fecha: {cita[3]} | Hora: {cita[4]} | Estado: {cita[5]}")

else:
    st.write("Selecciona una opción en el menú de la izquierda.")
