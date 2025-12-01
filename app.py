from flask import Flask, render_template, request, redirect, session, url_for
import qrcode
import base64
from io import BytesIO

# ---------------- CONFIGURACIÓN BASE ----------------
app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"  # Necesario para manejar sesiones

# ---------------- DATOS DE PELÍCULAS ----------------
peliculas = {
    "1": {
        "titulo": "Rápidos y Furiosos 10",
        "imagen": "https://static.cinepolis.com/resources/mx/movies/posters/414x603/41958-723264-20230519041114.jpg",
        "sinopsis": "La décima entrega llena de acción extrema, carreras peligrosas y lazos familiares.",
        "rating": "PG-13",
        "fecha": "2025-12-01",
        "hora": "20:00"
    },
    "2": {
        "titulo": "Asu Mare 3",
        "imagen": "https://is1-ssl.mzstatic.com/image/thumb/RxWzwXrw0BlmPt9dpW8v0Q/1200x675.jpg",
        "sinopsis": "La tercera parte de esta comedia peruana llena de humor y momentos emotivos.",
        "rating": "PG",
        "fecha": "2025-12-02",
        "hora": "18:00"
    },
     "3": {
        "titulo": "Drácula: A Love Tale",
        "imagen": "https://image.tmdb.org/t/p/original/rcDS8ns496oOKZgEwVCMMjeQ8ak.jpg",
        "sinopsis": "Una versión romántica y oscura de la leyenda de Drácula.",
        "rating": "R",
        "fecha": "2025-12-03",
        "hora": "21:00"
    },
    "4": {
        "titulo": "Son Como Niños",
        "imagen": "https://m.media-amazon.com/images/M/MV5BMDJmYWI5NDctZjM5Zi00NzJiLTk4YTEtZjFhYTZhMTJiYWEzXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "sinopsis": "Un grupo de amigos de la infancia se reúne para un fin de semana lleno de humor.",
        "rating": "PG-13",
        "fecha": "2025-12-04",
        "hora": "19:00"
    },
    "5": {
        "titulo": "Jumanji: Welcome to the Jungle",
        "imagen": "https://m.media-amazon.com/images/M/MV5BYWRmZWZlMDctNjUwMS00MmQ5LWJkZjItMmE4OGQ4NDQzZjAyXkEyXkFqcGc@._V1_.jpg",
        "sinopsis": "Cuatro adolescentes quedan atrapados en un videojuego y deben sobrevivir.",
        "rating": "PG-13",
        "fecha": "2025-12-05",
        "hora": "17:00"
    },
    "6": {
        "titulo": "¿Qué Pasó Ayer?",
        "imagen": "https://play-lh.googleusercontent.com/BKK63bcAzhBOcST8rqKuhAjNt4QPTBKN5bNLvlw5_GjPJrT6PEY3NeVRJDMwzMI56vat",
        "sinopsis": "Tres amigos despiertan en Las Vegas sin recordar la noche anterior.",
        "rating": "R",
        "fecha": "2025-12-06",
        "hora": "22:00"
    },
    "7": {
        "titulo": "The Conjuring (El Conjuro)",
        "imagen": "https://image.tmdb.org/t/p/original/wVYREutTvI2tmxr6ujrHT704wGF.jpg",
        "sinopsis": "Una familia es aterrorizada por una presencia demoníaca en su nueva casa.",
        "rating": "R",
        "fecha": "2025-12-07",
        "hora": "23:00"
    },
    "8": {
        "titulo": "Annabelle",
        "imagen": "https://m.media-amazon.com/images/M/MV5BNjkyMDU5ZWQtZDhkOC00ZWFjLWIyM2MtZWFhMDUzNjdlNzU2XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "sinopsis": "Una pareja joven enfrenta el terror de una muñeca poseída.",
        "rating": "R",
        "fecha": "2025-12-08",
        "hora": "21:30"
    },
    "9": {
        "titulo": "A Minecraft Movie",
        "imagen": "https://m.media-amazon.com/images/M/MV5BYzFjMzNjOTktNDBlNy00YWZhLWExYTctZDcxNDA4OWVhOTJjXkEyXkFqcGc@._V1_.jpg",
        "sinopsis": "Una aventura épica en el mundo de Minecraft.",
        "rating": "PG",
        "fecha": "2025-12-09",
        "hora": "16:00"
    }
}

# ---------------- LISTA DE RESERVAS ----------------
reservas = []

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        if usuario == "admin" and clave == "1234":  # credenciales simples
            session["admin"] = True
            return redirect("/admin")
        else:
            return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

# ---------------- PÁGINA PRINCIPAL ----------------
@app.route("/")
def index():
    return render_template("index.html", peliculas=peliculas)

@app.route("/reservas")
def reservas_page():
    pelicula_id = request.args.get("id")
    if pelicula_id not in peliculas:
        return "Película no encontrada", 404
    return render_template("reservas.html", pelicula=peliculas[pelicula_id], id=pelicula_id)

# ---------------- HACER RESERVA ----------------
@app.route("/hacer_reserva", methods=["POST"])
def hacer_reserva():
    usuario = request.form["usuario"]
    edad = request.form["edad"]
    pelicula_id = request.form["pelicula_id"]
    cinema = request.form["cinema"]
    room = request.form["room"]
    selectedSeats = request.form["selectedSeats"]

    # Calcular precio total
    premium = [45, 46, 55, 56]
    asientos = [int(s) for s in selectedSeats.split(",") if s]
    total = sum(15 if s in premium else 10 for s in asientos)

    reserva = {
        "usuario": usuario,
        "edad": edad,
        "pelicula_id": pelicula_id,
        "cinema": cinema,
        "room": room,
        "selectedSeats": selectedSeats,
        "total": total
    }
    reservas.append(reserva)

    # Generar QR con los datos de la reserva
    datos_qr = f"Usuario: {usuario}, Película: {peliculas[pelicula_id]['titulo']}, Cine: {cinema}, Sala: {room}, Asientos: {selectedSeats}, Total: ${total}"
    qr_img = qrcode.make(datos_qr)

    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Mostrar ticket con QR
    return render_template("ticket.html", reserva=reserva, pelicula=peliculas[pelicula_id], qr_code=qr_base64)

# ---------------- PANEL ADMIN ----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    total_reservas = len(reservas)
    total_recaudado = sum(r["total"] for r in reservas) if reservas else 0

    conteo = {}
    for r in reservas:
        titulo = peliculas[r["pelicula_id"]]["titulo"]
        conteo[titulo] = conteo.get(titulo, 0) + 1
    pelicula_popular = max(conteo, key=conteo.get) if conteo else "Ninguna"

    return render_template(
        "admin.html",
        peliculas=peliculas,
        reservas=reservas,
        total_reservas=total_reservas,
        total_recaudado=total_recaudado,
        pelicula_popular=pelicula_popular
    )

@app.route("/admin/edit/<id>", methods=["POST"])
def admin_edit(id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    if id in peliculas:
        peliculas[id]["titulo"] = request.form["titulo"]
        peliculas[id]["imagen"] = request.form["imagen"]
        peliculas[id]["sinopsis"] = request.form["sinopsis"]
        peliculas[id]["rating"] = request.form["rating"]
        peliculas[id]["fecha"] = request.form["fecha"]
        peliculas[id]["hora"] = request.form["hora"]
    return redirect("/admin")

@app.route("/admin/delete/<int:index>", methods=["POST"])
def admin_delete(index):
    if not session.get("admin"):
        return redirect(url_for("login"))
    if 0 <= index < len(reservas):
        reservas.pop(index)
    return redirect("/admin")

# ---------------- MAIN ----------------
# Importante: NO usamos app.run() porque Render lo lanza con Gunicorn
# El archivo expone la variable 'app' directamente