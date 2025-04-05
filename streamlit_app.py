import streamlit as st
import sqlite3
import datetime
import re

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

def register_user(username, password, role):
    # Validación de campos vacíos
    if not username or not password or not role:
        raise ValueError("Todos los campos son obligatorios")
    
    # Validación de caracteres especiales en el nombre de usuario
    if not re.match("^[a-zA-Z0-9_]+$", username):
        raise ValueError("El nombre de usuario no debe contener caracteres especiales")
    
    # Validación de formato de contraseña
    if not re.search("[A-Z]", password):
        raise ValueError("La contraseña debe contener al menos una letra mayúscula")
    if not re.search("[^a-zA-Z0-9]", password):
        raise ValueError("La contraseña debe contener al menos un carácter especial")
    
    # Validación de usuario existente
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        raise ValueError("El nombre de usuario ya existe")
    
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()


def login_user(username, password):
    # Validación de contraseña
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return c.fetchone()


def create_appointment(user_id, doctor, date, time):
    # Validación de doble reserva
    c.execute("SELECT * FROM appointments WHERE doctor = ? AND date = ? AND time = ?", (doctor, date, time))
    if c.fetchone():
        raise ValueError("Ya existe una cita para el mismo doctor en el mismo horario")
    c.execute("INSERT INTO appointments (user_id, doctor, date, time, status) VALUES (?, ?, ?, ?, ?)", 
              (user_id, doctor, date, time, "reservada"))
    conn.commit()


def get_appointments():
    c.execute("SELECT * FROM appointments")
    return c.fetchall()

# --- Interfaz Streamlit ---
st.title("FastMed - Sistema de Citas (Versión sin fallos)")

menu = ["Inicio", "Registro", "Login", "Reservar Cita", "Ver Citas", "Cerrar Sesión"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "Registro":
    st.subheader("Registro de Usuario")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type='password')
    role = st.selectbox("Rol", ["paciente", "medico"])
    if st.button("Registrar"):
        try:
            register_user(username, password, role)
            st.success("Usuario registrado correctamente")
        except ValueError as e:
            st.error(str(e))

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

if choice == "Reservar Cita":
    if 'user' not in st.session_state:
        st.warning("Debes iniciar sesión")
    else:
        st.subheader("Reservar Cita")
        doctor = st.selectbox("Médico", ["Dra. Salazar", "Dr. Gómez"])
        date = st.date_input("Fecha", min_value=datetime.date.today())
        time = st.selectbox("Hora", ["09:00", "10:00", "11:00"])
        if st.button("Reservar"):
            try:
                create_appointment(st.session_state['user'][0], doctor, str(date), time)
                st.success("Cita reservada")
            except ValueError as e:
                st.error(str(e))

elif choice == "Ver Citas":
    if 'user' not in st.session_state:
        st.warning("Debes iniciar sesión")
    else:
        st.subheader("Listado de Citas")
        citas = get_appointments()
        for cita in citas:
            st.write(f"ID: {cita[0]} | Usuario ID: {cita[1]} | Dr: {cita[2]} | Fecha: {cita[3]} | Hora: {cita[4]} | Estado: {cita[5]}")
      
elif choice == "Cerrar Sesión":
    if 'user' in st.session_state:
        del st.session_state['user']
        st.success("Sesión cerrada correctamente")
    else:
        st.warning("No hay ninguna sesión iniciada")

else:
    st.write("Selecciona una opción en el menú de la izquierda.")
