"""Aplicación backend Flask con API REST y conexión a PostgreSQL."""

from flask import Flask, jsonify, request

from config import Config
from models import Item, db


def create_app(config_class=Config):
    """Factory de la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)

    # Crear tablas al arrancar
    with app.app_context():
        db.create_all()

    # ── Rutas ─────────────────────────────────────────────

    @app.route("/")
    def index():
        """Información general de la API."""
        return jsonify(
            {
                "app": "PRJ5 Backend API",
                "version": "1.0.0",
                "autor": "Hector Garcia",
                "status": "ok",
                "endpoints": [
                    "GET  /",
                    "GET  /health",
                    "GET  /items",
                    "POST /items",
                    "GET  /items/<id>",
                    "DELETE /items/<id>",
                ],
            }
        )

    @app.route("/health")
    def health():
        """Health check con verificación de la base de datos."""
        try:
            db.session.execute(db.text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {e}"

        return jsonify(
            {
                "status": "healthy" if db_status == "connected" else "unhealthy",
                "database": db_status,
            }
        )

    @app.route("/items", methods=["GET"])
    def list_items():
        """Listar todos los ítems."""
        items = Item.query.order_by(Item.created_at.desc()).all()
        return jsonify([item.to_dict() for item in items])

    @app.route("/items", methods=["POST"])
    def create_item():
        """Crear un nuevo ítem."""
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "El campo 'name' es obligatorio"}), 400

        item = Item(
            name=data["name"],
            description=data.get("description", ""),
        )
        db.session.add(item)
        db.session.commit()

        return jsonify(item.to_dict()), 201

    @app.route("/items/<int:item_id>", methods=["GET"])
    def get_item(item_id):
        """Obtener un ítem por su ID."""
        item = db.session.get(Item, item_id)
        if item is None:
            return jsonify({"error": "Item no encontrado"}), 404
        return jsonify(item.to_dict())

    @app.route("/items/<int:item_id>", methods=["DELETE"])
    def delete_item(item_id):
        """Eliminar un ítem por su ID."""
        item = db.session.get(Item, item_id)
        if item is None:
            return jsonify({"error": "Item no encontrado"}), 404
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item eliminado correctamente"})

    # ── Manejo de errores ─────────────────────────────────

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Error interno del servidor"}), 500

    return app


# Punto de entrada para ejecución directa
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
