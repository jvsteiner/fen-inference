import os
import base64
import asyncio
import aiohttp
from pathlib import Path
import json
import chess
import chess.pgn
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API URL from environment variable
API_URL = os.getenv(
    "API_URL", "http://localhost:8080"
)  # Default to localhost if not set


def encode_image_to_base64(image_path):
    """Convert an image file to base64 string with data URL format."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        # Get the file extension and create appropriate mime type
        ext = image_path.suffix.lower()
        mime_type = f"image/jpeg" if ext in [".jpg", ".jpeg"] else f"image/{ext[1:]}"
        return f"data:{mime_type};base64,{encoded_string}"


async def process_puzzle(session, image_path):
    """Process a single puzzle image through the API."""
    # Get filename without extension to determine side to move
    filename = image_path.stem
    side_to_move = filename[0].lower() if filename[0].lower() in ["w", "b"] else "w"

    # Prepare the request data
    data = {"image": encode_image_to_base64(image_path), "side": side_to_move}

    # Make the API request
    try:
        async with session.post(
            API_URL,
            json=data,
            headers={"Content-Type": "application/json"},
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"Successfully processed {image_path.name}")
                print(f"FEN: {result['fen']}")
                return {"fen": result["fen"], "player_name": filename}
            else:
                error_text = await response.text()
                print(f"Error processing {image_path.name}: {error_text}")
                return None

    except Exception as e:
        print(f"Exception while processing {image_path.name}: {str(e)}")
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


async def process_all_puzzles(image_paths, max_concurrent=5):
    """Process multiple puzzles concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        # Create a semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(image_path):
            async with semaphore:
                return await process_puzzle(session, image_path)

        # Create tasks for all images
        for image_path in image_paths:
            task = asyncio.create_task(process_with_semaphore(image_path))
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]


async def main():
    # Get the puzzles directory path
    puzzles_dir = Path("puzzles")

    if not puzzles_dir.exists():
        print(f"Error: {puzzles_dir} directory not found")
        return

    # Get all valid image paths
    image_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    image_paths = [
        p for p in puzzles_dir.iterdir() if p.suffix.lower() in image_extensions
    ]

    if not image_paths:
        print("No image files found in puzzles directory")
        return

    print(f"Found {len(image_paths)} images to process")

    # Process all puzzles concurrently
    # Adjust max_concurrent based on your Cloud Run configuration
    results = await process_all_puzzles(
        image_paths, max_concurrent=80
    )  # or whatever limit you set

    # Create PGN games from results
    games = [create_pgn_game(result) for result in results]

    # Write all games to a single PGN file
    if games:
        output_file = "puzzles.pgn"
        with open(output_file, "w") as pgn_file:
            for i, game in enumerate(games):
                if i > 0:
                    print("\n", file=pgn_file)
                print(game, file=pgn_file, end="\n\n")

        print(
            f"\nSuccessfully processed {len(games)} puzzles. Output written to {output_file}"
        )


if __name__ == "__main__":
    asyncio.run(main())
