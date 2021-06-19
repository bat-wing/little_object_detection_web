import torch
from PIL import ImageDraw
from torchvision.transforms.functional import to_tensor

from net import get_net
import numpy as np
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def draw_det_boxes_on_image(image, bboxes, labels):
    draw = ImageDraw.Draw(image)
    length = labels.shape[0]
    good = 0
    bad = 0
    for i in range(length):
        if labels[i] == 1:
            draw.rectangle(bboxes[i], width=9, outline='#28FF28')
            good += 1
        else:
            draw.rectangle(bboxes[i], width=9, outline=255)
            bad += 1
    return good, bad


class InferenceService:
    def __init__(self):
        self.model = get_net()
        state_dict = torch.load(
            r'..\static\model\model.pkl', map_location=device)

        self.model.load_state_dict(state_dict)
        self.model.eval()

    def inference(self, image):
        tensor = to_tensor(image)
        with torch.no_grad():
            r = self.model([tensor])[0]
        g, b = draw_det_boxes_on_image(
            image, r['boxes'].numpy(), r['labels'].numpy())
        return g, b, image.rotate(-90)
