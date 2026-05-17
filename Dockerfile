FROM python:3.9-slim

# Sistem bağımlılıkları (OpenCV, Qt5, xdotool, ses, medya, ekran görüntüsü)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libegl1 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5x11extras5 \
    libqt5dbus5 \
    xvfb \
    xdotool \
    pulseaudio-utils \
    playerctl \
    scrot \
    && rm -rf /var/lib/apt/lists/*

# GPU devre dışı, yazılım render
ENV MEDIAPIPE_DISABLE_GPU=1
ENV QT_OPENGL=software
ENV LIBGL_ALWAYS_SOFTWARE=1

# Python paketleri
RUN pip install --no-cache-dir \
    mediapipe==0.10.9 \
    opencv-contrib-python==4.8.1.78 \
    numpy==1.26.4

WORKDIR /app
COPY . /app

# Xvfb'yi başlatan giriş betiği (isteğe bağlı)
RUN echo '#!/bin/bash\nif [ -z "$DISPLAY" ]; then\n  export DISPLAY=:99\n  Xvfb :99 -screen 0 1024x768x24 &\nfi\nexec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "main.py"]
