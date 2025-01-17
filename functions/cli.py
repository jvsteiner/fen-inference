import os
import sys
import chess
import chess.pgn
from PIL import Image
from chess_diagram_to_fen import get_fen


def process_image_file(file_path):
    # Extract filename without extension to use as player name
    filename = os.path.splitext(os.path.basename(file_path))[0]

    # Determine side to move from filename
    side_to_move = filename[0].lower()
    if side_to_move not in ["w", "b"]:
        print(f"Warning: Cannot determine side to move from filename: {filename}")
        return None

    try:
        # Process image and get FEN
        img = Image.open(file_path)
        result = get_fen(
            img=img, num_tries=10, auto_rotate_image=True, auto_rotate_board=True
        )

        # Get the base FEN and modify the side to move
        fen_parts = result.fen.split()
        fen_parts[1] = side_to_move  # Set the correct side to move
        modified_fen = " ".join(fen_parts)

        print("found FEN:", modified_fen)

        return {"fen": modified_fen, "player_name": filename}
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None


def create_pgn_game(fen_data):
    game = chess.pgn.Game()

    # Set headers
    game.headers["Event"] = "Chess Puzzle"
    game.headers["White"] = fen_data["player_name"]
    game.headers["Black"] = "?"
    game.headers["Result"] = "*"
    game.headers["FEN"] = fen_data["fen"]
    game.headers["SetUp"] = "1"

    # Set the starting position
    game.setup(chess.Board(fen_data["fen"]))

    return game


def main():
    if len(sys.argv) != 2:
        print("Usage: python evgeny.py <target_directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a valid directory")
        sys.exit(1)

    # Process all image files
    games = []
    image_extensions = {".jpg", ".jpeg", ".png"}

    for filename in os.listdir(target_dir):
        if os.path.splitext(filename)[1].lower() in image_extensions:
            file_path = os.path.join(target_dir, filename)
            result = process_image_file(file_path)
            if result:
                game = create_pgn_game(result)
                games.append(game)

    # Write all games to a single PGN file
    output_file = "puzzles.pgn"
    with open(output_file, "w") as pgn_file:
        for i, game in enumerate(games):
            if i > 0:
                print("\n", file=pgn_file)
            print(game, file=pgn_file, end="\n\n")

    print(
        f"Successfully processed {len(games)} puzzles. Output written to {output_file}"
    )


if __name__ == "__main__":
    main()
