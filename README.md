# VLM-Auto

This is the repo for our paper 'VLM-Auto: VLM-based Autonomous Driving Assistant with Human-like Behavior and Understanding for Complex Road Scenes'

## Dataset
Follow this [link](https://pan.baidu.com/s/19ejR9HIJDpL6kwKQ9f7dPg?pwd=rdkd) to download the dataset.


## Pipeline

### Fine-tuning
Follow the official instructions of [Qwen-VL](https://github.com/QwenLM/Qwen-VL/blob/master/finetune.py) for fine-tuning or other alternatives you need. Our dataset's format is based on the fine-tuning format of Qwen-vl.

### Docker
In docker/, dockerfile for the env of this pipeline is provided.

### CARLA
Prepare the [CARLA simulator](https://github.com/carla-simulator/carla), we used CARLA 0.9.15 for our experiments.

### CARLA-ROS-bridge
Install ROS package for the communication between ROS and CARLA: [link](https://github.com/carla-simulator/ros-bridge)

### Run VLM with ROS2
We provide an example to run the VLM module to send the ROS2 topics to CARLA for the experiments by:
```
python qwen_ROS2.py
```



