from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


def get_net():
    model = fasterrcnn_resnet50_fpn(
        pretrained=True,
        box_score_thresh=0.8,
        min_size=480,
        max_size=720)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, 3)  # 目标数

    return model
