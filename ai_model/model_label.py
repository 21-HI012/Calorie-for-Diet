from .models import *
from ..utils.datasets import *
from ..utils.utils import *
import argparse
import cv2


class Config:
    def parameters():
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--cfg', type=str, default='cfg/yolov3-spp-403cls.cfg', help='*.cfg path')
        parser.add_argument('--names', type=str,
                            default='data/403food.names', help='*.names path')
        parser.add_argument(
            '--weights', type=str, default='weights/best_403food_e200b150v2.pt', help='weights path')
        # input file/folder, 0 for webcam
        parser.add_argument('--source', type=str,
                            default='data/samples', help='source')
        parser.add_argument('--output', type=str, default='output',
                            help='output folder')  # output folder
        parser.add_argument('--img-size', type=int,
                            default=512, help='inference size (pixels)')
        parser.add_argument('--conf-thres', type=float,
                            default=0.3, help='object confidence threshold')
        parser.add_argument('--iou-thres', type=float,
                            default=0.6, help='IOU threshold for NMS')
        parser.add_argument('--fourcc', type=str, default='mp4v',
                            help='output video codec (verify ffmpeg support)')
        parser.add_argument('--half', action='store_true',
                            help='half precision FP16 inference')
        parser.add_argument('--device', default='',
                            help='device id (i.e. 0 or 0,1) or cpu')
        parser.add_argument(
            '--view-img', action='store_true', help='display results')
        parser.add_argument('--save-txt', action='store_true',
                            help='save results to *.txt')
        parser.add_argument('--classes', nargs='+',
                            type=int, help='filter by class')
        parser.add_argument(
            '--agnostic-nms', action='store_true', help='class-agnostic NMS')
        parser.add_argument('--augment', action='store_true',
                            help='augmented inference')

        opt, _ = parser.parse_known_args()

        return opt


params = Config.parameters()


def Model():
    model = Darknet(params.cfg, (320, 192))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    state_dict = torch.load(params.weights, map_location=device)
    state_dict = state_dict['model']
    new_state_dict = {key: state_dict[key] for key in state_dict.keys() if 'total' not in key}
    model.load_state_dict(new_state_dict)

    model.eval()

    return model


run = Model()


def inputdata(img):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    img_org = img[..., ::-1].copy()
    img = cv2.resize(img, dsize=(320, 192))
    img = torch.from_numpy(img[..., ::-1].copy())
    img = img.permute(2, 0, 1)
    img = img[None, ...]
    img = img / 255.0
    img = img.to(device)

    res = run(img)
    pred = non_max_suppression(res[0], conf_thres=0.3, iou_thres=0.5,
                               multi_label=False, classes=params.classes, agnostic=params.agnostic_nms)
    if pred == [None]:
        confidence = 0
        label = 9999
    else:
        det = pred[0]
        det[:, :4] = scale_coords(
            img.shape[2:], det[:, :4], img_org.shape).round()

        confidence = det[0, 4].item()
        label = int(det[0, 5])

    return [round(confidence * 100, 2), label]