import firebase_functions as functions
from PIL import Image
import chess
import chess.pgn
import tempfile
import io
from chess_diagram_to_fen import get_fen


@functions.https.on_request()
def process_chess_image(req: functions.Request) -> functions.Response:
    """HTTP Cloud Function that processes a chess image and returns FEN."""

    # Check if image is in request
    if not req.files or "image" not in req.files:
        return functions.Response(status=400, response="No image file provided")

    # Get the image file
    image_file = req.files["image"]

    # Get side to move from query parameter (default to 'w')
    side_to_move = req.args.get("side", "w").lower()
    if side_to_move not in ["w", "b"]:
        side_to_move = "w"

    try:
        # Convert uploaded file to PIL Image
        img = Image.open(io.BytesIO(image_file.read()))

        # Process image and get FEN
        result = get_fen(
            img=img, num_tries=10, auto_rotate_image=True, auto_rotate_board=True
        )

        # Modify FEN with correct side to move
        fen_parts = result.fen.split()
        fen_parts[1] = side_to_move
        modified_fen = " ".join(fen_parts)

        # Return the FEN string
        return functions.Response(
            response={"fen": modified_fen}, status=200, content_type="application/json"
        )

    except Exception as e:
        return functions.Response(
            response={"error": str(e)}, status=500, content_type="application/json"
        )
