import os

from ultralytics import YOLO
import cv2
import torch
VIDEOS_DIR = os.path.join('.', 'videos')

video_folder_path = "./samples_videos"
video_folder_resutlt= './result_videos'

videlo_list=os.listdir(video_folder_path)
model_path = "./model.pt"
model = YOLO(model_path)  # load a custom model
threshold = 0.5

for video_path in videlo_list:
    video_path = os.path.join(video_folder_path, video_path)  # join the folder path with the video name
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret or frame is None:
        print(f"Failed to read video: {video_path}")
        continue
    H, W, _ = frame.shape
    video_path_out=os.path.join(video_folder_resutlt,"result_"+ os.path.basename(video_path))
    out = cv2.VideoWriter(video_path_out, cv2.VideoWriter_fourcc(*'MP4V'), int(cap.get(cv2.CAP_PROP_FPS)), (W, H))
    while ret:

        results = model(frame)[0]

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            if score > threshold:
                class_name = results.names[int(class_id)]
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                cv2.putText(frame, class_name.upper(), (int(x1), int(y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

        out.write(frame)
        ret, frame = cap.read()

    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Load a model



