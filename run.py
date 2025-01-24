from app import create_app, db

app = create_app()

if __name__ == "__main__":
# # Las siguientes 2 líneas se usan para crear tablas en la DB conectada, basadas en los modelos actuales. 
#     with app.app_context():
#         db.create_all()
    app.run(debug=True)
