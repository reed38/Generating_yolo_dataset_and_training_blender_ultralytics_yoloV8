# Introduction
- This directory contains the files and the ressources used to train the model
- For further explainaitions on yoloV8 training on custom dataset you can check this video: [Link](https://www.youtube.com/watch?v=m9fH9OWn8YM)


## Configuration
- In order to train the model ultralytics libray must me installed first.
    - Look into **/workplace_setup** for further instructions
- Edit the config.yaml file to define the following variables:
    - **train**: Path to the directory in which the dataset for training is located. The images and lables MUST be in the same folder
    - **val**: Path to the directory in which the dataset for validation is located. The images and lables MUST be in the same folder
    - **names** : This is used to define the class and class name used.

## Training

- Source the virtual environement in which the package were installed for ultralytics during setup: run the command `. ../workplace_setup/venv/bin/activate` from the `yoloV8_traing` folder.
- Then run the python script `train.py` with the command `python3 train.py`.

## Results
- Once the training is finished, the results can be found in the **/train** folder


## Video validation
- In order to further test the model you can generate a quick animation in which you turn arround the object, export this video, and then used the model on the video.
- Here is a link to a video explaining how to quickly and easily do it in blender:
    - Creating the animation [Link](https://www.youtube.com/watch?v=a7qyW1G350g&list=PLPAVX2ozmg6-wKC0b5XaraQ6Hkp11xVur)
    - Exporting to mp4 video: [Link](https://www.youtube.com/watch?v=3eJmISziyIY)

- Using the **predict_video.py** you can then apply  the model on the video and get an anotated video on which the images have been added.
    - Put all the videos you want to test the model on in **/samples_videos**
    - Put the trained model **x.pt** in the same directory as the python script and name it **"model.pt"**
    - run the script `python3 predict_video.py`
    - The annotated videos generated will then be placed in the **/result_videos** directory
