ARG BASE_DIST
ARG CUDA_VERSION
# CUDA
FROM nvidia/cuda:${CUDA_VERSION}-base-${BASE_DIST}

RUN apt-key adv --fetch-keys "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub"

# vulkan
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglvnd0 \
    libgl1 \
    libglx0 \
    libegl1  \
    libgles2  \
    libxcb1-dev \
    wget \
    vulkan-utils \
    && rm -rf /var/lib/apt/lists/*

#set VULKAN_SDK_VERSION as a build-arg=`curl https://vulkan.lunarg.com/sdk/latest/linux.txt`
ARG VULKAN_SDK_VERSION
# Download the Vulkan SDK and extract the headers, loaders, layers and binary utilities
RUN wget -q --show-progress \
    --progress=bar:force:noscroll \
    https://sdk.lunarg.com/sdk/download/latest/linux/vulkan_sdk.tar.gz \
    -O /tmp/vulkansdk-linux-x86_64-${VULKAN_SDK_VERSION}.tar.gz \ 
    && echo "Installing Vulkan SDK ${VULKAN_SDK_VERSION}" \
    && mkdir -p /opt/vulkan \
    && tar -xf /tmp/vulkansdk-linux-x86_64-${VULKAN_SDK_VERSION}.tar.gz -C /opt/vulkan \
    && mkdir -p /usr/local/include/ && cp -ra /opt/vulkan/${VULKAN_SDK_VERSION}/x86_64/include/* /usr/local/include/ \
    && mkdir -p /usr/local/lib && cp -ra /opt/vulkan/${VULKAN_SDK_VERSION}/x86_64/lib/* /usr/local/lib/ \
    && cp -a /opt/vulkan/${VULKAN_SDK_VERSION}/x86_64/lib/libVkLayer_*.so /usr/local/lib \
    && mkdir -p /usr/local/share/vulkan/explicit_layer.d \
    && cp /opt/vulkan/${VULKAN_SDK_VERSION}/x86_64/etc/vulkan/explicit_layer.d/VkLayer_*.json /usr/local/share/vulkan/explicit_layer.d \
    && mkdir -p /usr/local/share/vulkan/registry \
    && cp -a /opt/vulkan/${VULKAN_SDK_VERSION}/x86_64/share/vulkan/registry/* /usr/local/share/vulkan/registry \
    && cp -a /opt/vulkan/${VULKAN_SDK_VERSION}/x86_64/bin/* /usr/local/bin \
    && ldconfig \
    && rm /tmp/vulkansdk-linux-x86_64-${VULKAN_SDK_VERSION}.tar.gz && rm -rf /opt/vulkan

# Setup the required capabilities for the container runtime    
ENV NVIDIA_DRIVER_CAPABILITIES compute,graphics,utility

# Licensed under the NGC Deep Learning Container License
COPY NGC-DL-CONTAINER-LICENSE.txt /

# Python3.7
#RUN apt update && apt install software-properties-common -y && apt update
# RUN apt-get install add-apt-repository
#RUN apt update && apt upgrade -y && add-apt-repository ppa:deadsnakes/ppa -y && apt update && DEBIAN_FRONTEND=noninteractive apt #install python3.7 python3.7-distutils python3.7-dev python3-pip -y
#CMD ["python3.7", "app.py"]

# need python3.6.9?
RUN packages='libsdl2-2.0 xserver-xorg libvulkan1 libomp5' && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y $packages --no-install-recommends

# ROS2
RUN locale  # check for UTF-8
RUN apt update -y && apt install -y locales
RUN locale-gen en_US en_US.UTF-8
RUN update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
RUN export LANG=en_US.UTF-8
RUN locale  # verify settings

RUN apt install -y software-properties-common
RUN add-apt-repository -y universe

RUN apt update -y && apt install -y curl gnupg2 lsb-release
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key  -o /usr/share/keyrings/ros-archive-keyring.gpg

# dashing
#RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/#ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

# foxy
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt update && apt upgrade
RUN DEBIAN_FRONTEND=noninteractive apt install -y ros-foxy-desktop python3-argcomplete ros-dev-tools

# tools
RUN apt install -y python3-pip git make cmake python3-rosdep build-essential python3-colcon-common-extensions wget vim ros-foxy-derived-object-msgs

RUN python3 -m pip install -U argcomplete setuptools pygame shapely networkx

# qwen
RUN git lfs install

RUN python3 -m pip install transformers==4.37.2 accelerate einops transformers_stream_generator==0.0.4 scipy pillow tensorboard matplotlib optimum==1.17.1 ms-swift==1.6.1 peft==0.7.1 huggingface-hub==0.20.3

# python3.8
#python3.8 -m pip install --upgrade pip

# qwen_ros2_running: torch
RUN python3 -m pip install torch==1.12.0 torchvision==0.13.0 torchaudio==0.12.0
RUN python3 -m pip install modelscope tiktoken transformers_stream_generator auto-gptq optimum==1.17.1


RUN useradd -m carla

COPY --chown=carla:carla . /home/carla

USER carla
WORKDIR /home/carla
