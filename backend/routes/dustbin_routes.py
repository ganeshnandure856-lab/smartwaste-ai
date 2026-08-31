from flask import Blueprint, jsonify
from backend.database import get_all_dustbins

dustbin_bp = Blueprint("dustbin", __name__)


@dustbin_bp.route("/api/dustbins", methods=["GET"])
def get_dustbins():

    try:
        dustbins = get_all_dustbins()

        return jsonify({
            "success": True,
            "count": len(dustbins),
            "data": dustbins
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500