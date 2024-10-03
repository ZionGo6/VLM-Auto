import os 
import os.path as osp
import glob
import logging
import numpy as np
import cv2
import sys
import json

import torch
from modelscope import (
   snapshot_download,
   AutoModelForCausalLM,
   AutoTokenizer,
   GenerationConfig,
)
import base64
import re
from PIL import Image
from io import BytesIO
from peft import AutoPeftModelForCausalLM
# import xml.etree.ElementTree as ET

import rclpy
import cv_bridge
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, HistoryPolicy, QoSDurabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String

sys.path.append('/home/carla')
os.environ['HF_HOME'] = '/home/carla'
os.environ['offload_buffers'] = 'True'

DEFAULT_CKPT_PATH = '/home/carla/weights/Qwen-VL-Chat-Int4'
DEFAULT_ADAPT_CKPT_PATH = '/home/carla/output_co_driver/checkpoint-2000/'
# BOX_TAG_PATTERN = r"<box>([\s\S]*?)</box>"
# PUNCTUATION = "！？。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."


ros_time = rclpy.clock.Clock().now().to_msg()
carla_temp_folder = '/home/carla/temp_images/'

numbers = re.compile(r'(\d+)')

def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

tokenizer = AutoTokenizer.from_pretrained(DEFAULT_CKPT_PATH, trust_remote_code=True)
model = AutoPeftModelForCausalLM.from_pretrained(
    DEFAULT_ADAPT_CKPT_PATH,
    device_map="auto",
    trust_remote_code=True,
    cache_dir='/home/carla/'
).eval()
model.generation_config = GenerationConfig.from_pretrained(DEFAULT_CKPT_PATH, trust_remote_code=True)

class VLM(Node):
    def __init__(self):
        super().__init__("VLM")

        self.bridge = CvBridge()
        self.i = 1
        qos_policy = QoSProfile(reliability=QoSReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_ALL, 
                                depth=10, durability=QoSDurabilityPolicy.VOLATILE)
        
        '''
        /carla/ego_vehicle/gnss
        /carla/ego_vehicle/imu
        /carla/ego_vehicle/objects
        '''

        self.image_sub = self.create_subscription(Image, '/carla/ego_vehicle/rgb_front/image', self.image_sub_callback, qos_profile=qos_policy)
        self.vlm_control_pub = self.create_publisher(String, '/carla/vlm/control/max_speed', qos_profile=qos_policy)
        self.timer = self.create_timer(0.5, self.vlm_pub_callback)

    def image_sub_callback(self, carla_image):
        self.image = self.bridge.imgmsg_to_cv2(carla_image, 'bgr8')
        rostime = self.get_clock().now()
        cv2.imwrite(carla_temp_folder + f'{rostime}_{self.i}.jpg', self.image)
        self.get_logger().info(f'Received_Saved_images:{self.i}')
        carla_image_list.append(self.image)
        self.i += 1

    def vlm_pub_callback(self):
        
        image_flie_list = sorted(os.listdir(carla_temp_folder), key=numericalSort)
        
        n = 0
        
        for image_path in image_flie_list:
            
            query = tokenizer.from_list_format([
                {'image': f'{carla_temp_folder}{image_path}'},
                {'text': f'Describe the type of control and its settings for the self-driving car using the first-person image: <img>{carla_temp_folder}{image_path}</img>. Provide an XML document with the driving parameters for this situation.'}])
            
            response, history = model.chat(tokenizer, query=query, history=None)
            response_list = []
            
            start_tag_1 = response.find('<distance>') + len('<distance>')
            end_tag_1 = response.find('</distance>')
            distance = response[start_tag_1:end_tag_1]
            print('safety distance:', distance)
            response_list.append(distance)
            
            start_tag_2 = response.find('<weather>') + len('<weather>')
            end_tag_2 = response.find('</weather>')
            weather = response[start_tag_2:end_tag_2]
            print('weather:', weather)
            response_list.append(weather)
            
            start_tag_3 = response.find('<light>') + len('<light>')
            end_tag_3 = response.find('</light>')
            light = response[start_tag_3:end_tag_3]
            print('light condition:', light)
            response_list.append(light)
            
            start_tag_4 = response.find('<surface>') + len('<surface>')
            end_tag_4 = response.find('</surface>')
            surface = response[start_tag_4:end_tag_4]
            print('road surface:', surface)
            response_list.append(surface)
            
            start_tag_5 = response.find('<locality>') + len('<locality>')
            end_tag_5 = response.find('</locality>')
            locality = response[start_tag_5:end_tag_5]
            print('driving locality:', locality)
            response_list.append(locality)
            
            start_tag_7 = response.find('<max_speed>') + len('<max_speed>')
            end_tag_7 = response.find('</max_speed>')
            max_speed = response[start_tag_7:end_tag_7]
            print('max speed:', max_speed)
            response_list.append(max_speed)
            
            start_tag_8 = response.find('<max_break>') + len('<max_break>')
            end_tag_8 = response.find('</max_break>')
            max_brake = response[start_tag_8:end_tag_8]
            print('max brake:', max_brake)
            response_list.append(max_brake)
            
            start_tag_9 = response.find('<max_trottle>') + len('<max_trottle>')
            end_tag_9 = response.find('</max_trottle>')
            max_throttle = response[start_tag_9:end_tag_9]
            print('max throttle:', max_throttle)
            response_list.append(max_throttle)
            
            start_tag_10 = response.find('<max_acceleration>') + len('<max_acceleration>')
            end_tag_10 = response.find('</max_acceleration>')
            max_acceleration = response[start_tag_10:end_tag_10]
            print('max acceleration:', max_acceleration)
            response_list.append(max_acceleration)
            
            start_tag_11 = response.find('<max_steering_speed>') + len('<max_steering_speed>')
            end_tag_11 = response.find('</max_steering_speed>')
            max_steering_speed = response[start_tag_11:end_tag_11]
            print('max steering speed:', max_steering_speed)
            response_list.append(max_steering_speed)
            
            n += 1
            
            max_speed_msg = String()
            max_speed_msg.data = max_speed
            
            self.vlm_control_pub.publish(max_speed_msg)

            print('============================ msg_published ==========================')
        
        image_sequence = [os.path.join(carla_temp_folder, image) for image in image_flie_list] 
        os.remove(file) for file in image_sequence
        del carla_image_list[:n]

def main(args=None):
    rclpy.init(args=args)
    vlm_publisher = VLM()
    rclpy.spin(vlm_publisher)
    vlm_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
