import functions_framework
from PIL import Image
import chess
import chess.pgn
import tempfile
import io
from chess_diagram_to_fen import get_fen
import base64
import re
import json


@functions_framework.http
def process_chess_image(request):
    """HTTP Cloud Function that processes a base64 encoded chess image and returns FEN."""

    # Ensure the request has a JSON body
    if not request.is_json:
        return {"error": "Request must be JSON"}, 400

    request_json = request.get_json()

    # Check if image data is in request
    if not request_json or "image" not in request_json:
        return {"error": "No image data provided"}, 400

    # Get the base64 image string
    image_data_url = request_json["image"]

    # Validate data URL format
    data_url_pattern = r"^data:image/(?:jpeg|png|jpg|gif);base64,"
    if not re.match(data_url_pattern, image_data_url):
        return {"error": "Invalid image data URL format"}, 400

    try:
        # Extract the base64 data part
        base64_data = image_data_url.split(",")[1]

        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_data)

        # Convert bytes to PIL Image
        img = Image.open(io.BytesIO(image_bytes))

        # Get side to move from JSON (default to 'w')
        side_to_move = request_json.get("side", "w").lower()
        if side_to_move not in ["w", "b"]:
            side_to_move = "w"

        # Process image and get FEN
        result = get_fen(
            img=img, num_tries=10, auto_rotate_image=True, auto_rotate_board=True
        )

        # Modify FEN with correct side to move
        fen_parts = result.fen.split()
        fen_parts[1] = side_to_move
        modified_fen = " ".join(fen_parts)

        # Return the FEN string
        return {"fen": modified_fen}, 200

    except base64.binascii.Error:
        return {"error": "Invalid base64 encoding"}, 400
    except Exception as e:
        return {"error": str(e)}, 500
