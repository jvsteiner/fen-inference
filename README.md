# Chess Position Recognition Service

This service uses computer vision to recognize chess positions from images and convert them to FEN notation. It's built using Python and deployed on Google Cloud Run.

## Prerequisites

- Python 3.11+
- Google Cloud account
- Firebase CLI
- gcloud CLI
- Docker

## Project Structure

````

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
````

2. Install local dependencies:

   ```bash
   pip install -r functions/requirements.txt
   pip install python-dotenv aiohttp python-chess
   ```

3. Set up Google Cloud:

   ```bash
   # Initialize gcloud with your project
   gcloud init

   # Set your project ID
   gcloud config set project YOUR_PROJECT_ID
   ```

4. Configure environment:

   ```bash
   # Copy example env file
   cp .env.example .env

   # Edit .env with your settings
   # After deployment, update API_URL with your Cloud Run URL
   ```

## Deployment

1. Enable required APIs:

   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   ```

2. Deploy to Cloud Run:

   ```bash
   gcloud builds submit
   ```

3. After deployment, get your service URL:

   ```bash
   gcloud run services describe fen-inference --region=us-central1 --format='value(status.url)'
   ```

4. Update your .env file with the service URL:
   ```
   API_URL=<your-cloud-run-url>
   ```

## Usage

1. Create a `puzzles` directory and add your chess position images:

   ```bash
   mkdir puzzles
   # Add your .jpg/.png files to the puzzles directory
   # Filename format: [W/B]_description.jpg
   # Example: W_puzzle1.jpg for a white-to-move position
   ```

2. Run the client script:

   ```bash
   python process_puzzles.py
   ```

   This will:

   - Process all images in the puzzles directory
   - Generate FEN strings for each position
   - Create a PGN file with all positions

## Configuration

### Cloud Run Settings

You can adjust the service configuration in the Cloud Console:

- Memory allocation
- CPU allocation
- Concurrency
- Autoscaling

### Client Settings

Adjust concurrent processing in `process_puzzles.py`:

```python
results = await process_all_puzzles(image_paths, max_concurrent=80)
```

## Monitoring

Monitor your service through the Google Cloud Console:

- Metrics: https://console.cloud.google.com/run/detail/us-central1/fen-inference/metrics
- Logs: https://console.cloud.google.com/run/detail/us-central1/fen-inference/logs
- Configuration: https://console.cloud.google.com/run/detail/us-central1/fen-inference/configuration

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

This project is based on the work of [Jost Triller](https://github.com/tsoj/Chess_diagram_to_FEN).
