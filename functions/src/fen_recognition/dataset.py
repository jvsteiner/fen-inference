import chess
import torch
import random
from torch.utils.data import Dataset
from torchvision.transforms import v2
from PIL import Image
from pathlib import Path
from src import common, consts


default_transforms = torch.nn.Sequential(
    v2.ToDtype(torch.float32),
    v2.Resize(
        size=(consts.BOARD_PIXEL_WIDTH, consts.BOARD_PIXEL_WIDTH),
        interpolation=v2.InterpolationMode.BICUBIC,
    ),
    common.MinMaxMeanNormalization(),
)

augment_transforms = torch.nn.Sequential(
    v2.RandomApply(
        [common.AddGaussianNoise(std=0.1, scale_to_input_range=True)], p=0.4
    ),
    v2.RandomApply(
        [v2.ElasticTransform(alpha=30.0), v2.ElasticTransform(alpha=40.0)], p=0.4
    ),
    v2.RandomGrayscale(p=0.4),
    v2.RandomPosterize(bits=2, p=0.2),
    v2.RandomApply(
        [v2.ColorJitter(brightness=0.9, contrast=(0.1, 1.5), hue=0.3)], p=0.3
    ),
    v2.RandomApply([v2.GaussianBlur(kernel_size=(3, 3))], p=0.2),
    v2.RandomApply([v2.GaussianBlur(kernel_size=(5, 5))], p=0.1),
    v2.RandomAdjustSharpness(sharpness_factor=10, p=0.1),
    v2.RandomEqualize(p=0.8),
)

affine_transforms = v2.RandomAffine(
    degrees=1.5, translate=(0.01, 0.01), scale=(0.99, 1.01), shear=1.5
)


class ChessBoardDataset(Dataset):

    def __init__(
        self,
        root_dir,
        augment_ratio=0.5,
        affine_augment_ratio=0.8,
        max=None,
        device=torch.device("cpu"),
    ):

        self.device = device
        self.augments = torch.nn.Sequential(
            v2.RandomApply([affine_transforms], p=affine_augment_ratio),
            v2.RandomApply([augment_transforms], p=augment_ratio),
        )

        root_dir = Path(root_dir)
        assert root_dir.is_dir(), f"With root_dir = {root_dir}"

        img_list = common.glob_all_image_files_recursively(root_dir)

        self.image_files = []
        for filename in img_list:

            fen = common.normalize_fen(Path(filename).stem)

            if fen is not None:
                self.image_files.append(filename)
            else:
                print("WARNING: Couldn't detect ground truth FEN: " + str(filename))

        random.shuffle(self.image_files)
        if max is not None:
            self.image_files = self.image_files[0 : min(len(self.image_files), max)]

        print(f"Found {len(self.image_files)} files")

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        file_path = self.image_files[idx]
        fen = common.normalize_fen(file_path.stem)

        assert fen is not None

        board = chess.Board(fen)
        try:
            img = Image.open(file_path)
        except RuntimeError:
            print("Error:", file_path)
            raise

        input_img = common.to_rgb_tensor(img).to(self.device)

        target = common.chess_board_to_tensor(board).to(self.device)

        while True:
            input_img = self.augments(input_img)

            if input_img.isnan().any():
                print("WARNING: Found nan after augmentation. Trying again.")
                continue

            input_img = default_transforms(input_img)

            if input_img.isnan().any():
                print(f"WARNING: Found nan after default transform. Trying again.")
                continue
            break

        return (input_img, target)
