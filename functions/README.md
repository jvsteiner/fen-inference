# Chess diagram to FEN

Extract the FEN out of images of chess diagrams.

It works in multiple steps:
1. Detect if there exists any chess board in the image
2. Get a bounding box of the (most prominent) chess board
3. Check if the board image is rotated by 0, 90, 180, or 270 degrees
4. Finally detect the FEN by looking at each square tile and predicting the piece (but also getting the entire board as additional input to make distinguishing between black and white pieces easier)
5. Detect if the perspective is from blacks or whites perspective (using a simple fully connected NN)

All these steps (except the fifth) basically use some common pretrained convolutional models available via torchvision with slightly modified heads. Detection is made robust using demanding generated training data and augmentations.

## Install

0. (Optional) It is suggested to use a conda environment.
1. Install [PyTorch](https://pytorch.org/get-started/locally/) (e.g. `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`, but CUDA and ROCm should also both work fine).
2. Download and install the `Chess_diagram_to_FEN` package:
```shell
git clone "https://github.com/tsoj/Chess_diagram_to_FEN.git"
# Or use as git submodule
# git submodule add "https://github.com/tsoj/Chess_diagram_to_FEN"

pip install -e ./Chess_diagram_to_FEN/
```

## Usage

```python
from PIL import Image
from Chess_diagram_to_FEN.chess_diagram_to_fen import get_fen

img = Image.open("your_image.jpg")
result = get_fen(
    img=img,
    num_tries=10,
    auto_rotate_image=True,
    auto_rotate_board=True
)

print(result.fen)
```

Or use the demo program:
```shell
python chess_diagram_to_fen.py --dir resources/test_images/real_use_cases/
```


## Train models yourself

#### Generate training data
Needs about **40 GB** disk space.
```shell
python main.py generate fen

# It is important to generate the fen data before
# the bbox and existence data, since the bbox data generation
# relies on the fen training data

pip install gdown
./download_website_screenshots.sh
python main.py generate bbox
python main.py generate existence

./download_lichess_games.sh
```

Additionally you can download [this Kaggle dataset](https://www.kaggle.com/datasets/koryakinp/chess-positions), unzip it, and place it into `resources/fen_images` to further augment the training data for FEN detection.

#### Review datasets (optional)

```shell
python main.py dataset bbox
python main.py dataset fen
python main.py dataset orientation
python main.py dataset image_rotation
python main.py dataset existence
```

#### Train

```shell
python main.py train bbox
python main.py train fen
python main.py train orientation
python main.py train image_rotation
python main.py train existence
```

#### Evaluate (optional)

```shell
python main.py eval fen
python main.py eval orientation
python main.py eval image_rotation
```

## Examples

### Successes

<img src="./resources/examples/success/success_1.jpg" width="600px" style="border-radius: 20px;">

<img src="./resources/examples/success/success_2.jpg" width="600px" style="border-radius: 20px;">

<img src="./resources/examples/success/success_3.jpg" width="600px" style="border-radius: 20px;">

<img src="./resources/examples/success/success_4.jpg" width="600px" style="border-radius: 20px;">

<img src="./resources/examples/success/success_5.jpg" width="600px" style="border-radius: 20px;">


### Failures

<img src="./resources/examples/failure/failure_1.jpg" width="600px" style="border-radius: 20px;">

<img src="./resources/examples/failure/failure_2.jpg" width="600px" style="border-radius: 20px;">

<img src="./resources/examples/failure/failure_3.jpg" width="600px" style="border-radius: 20px;">

<img src="./resources/examples/failure/failure_4.jpg" width="600px" style="border-radius: 20px;">

<img src="./resources/examples/failure/failure_5.jpg" width="600px" style="border-radius: 20px;">


