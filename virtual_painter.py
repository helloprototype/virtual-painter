import cv2
import numpy as np
import mediapipe as mp
import time
import os
from collections import deque
import math
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class VideoProcessor(VideoTransformerBase):
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.7)

        self.canvas = np.zeros((720, 1280, 3), dtype=np.uint8) 
        self.temp_canvas = np.zeros((720, 1280, 3), dtype=np.uint8)

        self.colors = [
            (0, 0, 255), (0, 127, 255), (0, 255, 255),
            (110, 255, 0), (255, 0, 0), (255, 0, 255),
            (150, 150, 150), (255, 255, 255), (57, 255, 20),
            (255, 20, 147), (0, 191, 255), (255, 255, 0)
        ]
        self.current_color = self.colors[0]

        self.brush_size = [5, 10, 15, 20, 30]
        self.brush_size_index = 2
        self.brush_thickness = self.brush_size[self.brush_size_index]
        self.eraser_thickness = 50

        self.tools = ["brush", "eraser", "rectangle", "circle", "line", "filled_rectangle", "filled_circle", "clear_canvas"]
        self.current_tool = "brush"

        self.drawing = False
        self.prev_x = self.prev_y = 0
        self.start_x = self.start_y = 0
        self.point_history = deque(maxlen=5)

        self.last_ui_interaction_time = 0
        self.button_height = 60
        self.color_button_width = 40
        self.tool_button_width = 90
        self.action_button_width = 100

    def smooth_points(self, x, y):
        self.point_history.append((x, y))
        avg_x = int(np.mean([pt[0] for pt in self.point_history]))
        avg_y = int(np.mean([pt[1] for pt in self.point_history]))
        return avg_x, avg_y

    def draw_brush(self, canvas, x, y):
        if self.prev_x == 0 and self.prev_y == 0:
            self.prev_x, self.prev_y = x, y
        if self.current_tool == "brush":
            cv2.line(canvas, (self.prev_x, self.prev_y), (x, y), self.current_color, self.brush_thickness)
        elif self.current_tool == "eraser":
            cv2.line(canvas, (self.prev_x, self.prev_y), (x, y), (0, 0, 0), self.eraser_thickness)
        self.prev_x, self.prev_y = x, y

    def draw_shape(self, canvas, shape, x1, y1, x2, y2, color, thickness):
        if shape == 'rectangle':
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, thickness)
        elif shape == 'filled_rectangle':
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, -1)
        elif shape == 'circle':
            radius = int(math.hypot(x2 - x1, y2 - y1))
            cv2.circle(canvas, (x1, y1), radius, color, thickness)
        elif shape == 'filled_circle':
            radius = int(math.hypot(x2 - x1, y2 - y1))
            cv2.circle(canvas, (x1, y1), radius, color, -1)
        elif shape == 'line':
            cv2.line(canvas, (x1, y1), (x2, y2), color, thickness)

    def draw_ui(self, frame):
        colors_per_row = 6
        for i, color in enumerate(self.colors):
            row = i // colors_per_row
            col = i % colors_per_row
            x_start = 10 + col * (self.color_button_width + 5)
            y_start = 10 + row * (self.button_height + 10)
            cv2.rectangle(frame, (x_start, y_start), (x_start + self.color_button_width, y_start + self.button_height), color, -1)
            if color == self.current_color:
                cv2.rectangle(frame, (x_start - 2, y_start - 2), (x_start + self.color_button_width + 2, y_start + self.button_height + 2), (255, 255, 255), 2)
        
        tool_start_x = 10 + colors_per_row * (self.color_button_width + 5) + 20
        for i, tool in enumerate(self.tools):
            x_start = tool_start_x + i * (self.tool_button_width + 5)
            color = (200, 200, 200)
            cv2.rectangle(frame, (x_start, 10), (x_start + self.tool_button_width, self.button_height), color, -1)
            if tool == self.current_tool:
                cv2.rectangle(frame, (x_start, 10), (x_start + self.tool_button_width, self.button_height), (0, 255, 0), 2)
            label = tool.replace("_", " ").title()
            if label == "Clear Canvas":
                label = "Clear"
            cv2.putText(frame, label, (x_start + 5, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        brush_ui_x = tool_start_x + len(self.tools) * (self.tool_button_width + 5) + 20
        cv2.putText(frame, "Brush Size", (brush_ui_x, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.rectangle(frame, (brush_ui_x, 40), (brush_ui_x + 30, 70), (50, 50, 50), -1)
        cv2.putText(frame, "-", (brush_ui_x + 7, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"{self.brush_thickness}", (brush_ui_x + 40, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.rectangle(frame, (brush_ui_x + 90, 40), (brush_ui_x + 120, 70), (50, 50, 50), -1)
        cv2.putText(frame, "+", (brush_ui_x + 97, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def handle_ui_interaction(self, x, y):
        
        colors_per_row = 6
        for i, color in enumerate(self.colors):
            row = i // colors_per_row
            col = i % colors_per_row
            x_start = 10 + col * (self.color_button_width + 5)
            y_start = 10 + row * (self.button_height + 10)
            if x_start < x < x_start + self.color_button_width and y_start < y < y_start + self.button_height:
                self.current_color = color
                return
        
        tool_start_x = 10 + colors_per_row * (self.color_button_width + 5) + 20
        for i, tool in enumerate(self.tools):
            x_start = tool_start_x + i * (self.tool_button_width + 5)
            if x_start < x < x_start + self.tool_button_width and 10 < y < self.button_height:
                if tool == "clear_canvas":
                    self.canvas = np.zeros((720, 1280, 3), dtype=np.uint8)
                else:
                    self.current_tool = tool
                return
        
        brush_ui_x = tool_start_x + len(self.tools) * (self.tool_button_width + 5) + 20
        if brush_ui_x < x < brush_ui_x + 30 and 40 < y < 70:
            self.brush_size_index = max(0, self.brush_size_index - 1)
            self.brush_thickness = self.brush_size[self.brush_size_index]
        elif brush_ui_x + 90 < x < brush_ui_x + 120 and 40 < y < 70:
            self.brush_size_index = min(len(self.brush_size) - 1, self.brush_size_index + 1)
            self.brush_thickness = self.brush_size[self.brush_size_index]

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1) 

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img, handLms, self.mp_hands.HAND_CONNECTIONS)

                x1 = int(handLms.landmark[8].x * img.shape[1]) 
                y1 = int(handLms.landmark[8].y * img.shape[0]) 
                x2 = int(handLms.landmark[12].x * img.shape[1]) 
                y2 = int(handLms.landmark[12].y * img.shape[0]) 
                distance = math.hypot(x2 - x1, y2 - y1)
                pinch = distance < 40

                x1, y1 = self.smooth_points(x1, y1)
                cv2.circle(img, (x1, y1), 10, self.current_color, -1)

                if y1 < 150: 

                    self.drawing = False
                elif pinch:
                    if not self.drawing:
                        self.drawing = True
                        self.prev_x, self.prev_y = x1, y1
                        self.start_x, self.start_y = x1, y1
                    elif self.current_tool in ["brush", "eraser"]:
                        self.draw_brush(self.canvas, x1, y1)
                    else:
                        self.temp_canvas = self.canvas.copy()
                        self.draw_shape(self.temp_canvas, self.current_tool, self.start_x, self.start_y, x1, y1, self.current_color, self.brush_thickness)
                else:
                    if self.drawing and self.current_tool in ["rectangle", "circle", "line", "filled_rectangle", "filled_circle"]:
                        self.draw_shape(self.canvas, self.current_tool, self.start_x, self.start_y, x1, y1, self.current_color, self.brush_thickness)
                    self.drawing = False
                    self.prev_x, self.prev_y = 0, 0


        display = self.temp_canvas if self.drawing and self.current_tool in ["rectangle", "circle", "line", "filled_rectangle", "filled_circle"] else self.canvas
        mask = cv2.cvtColor(display, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(mask, 5, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        bg = cv2.bitwise_and(img, img, mask=mask_inv)
        fg = cv2.bitwise_and(display, display, mask=mask)
        final = cv2.add(bg, fg)

        self.draw_ui(final)

        return final

st.title("Virtual Painter with Hand Tracking")
st.write("Draw in the air using your hand!")

if 'painter_state' not in st.session_state:
    st.session_state.painter_state = VideoProcessor()


col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

with col1:
    st.subheader("Colors")
    selected_color_rgb = st.color_picker("Choose a color", '#0000FF', key='color_picker')
    selected_color_bgr = tuple(int(selected_color_rgb.lstrip('#')[i:i+2], 16) for i in (4, 2, 0))
    st.session_state.painter_state.current_color = selected_color_bgr


with col2:
    st.subheader("Tools")
    selected_tool = st.radio("Select Tool", st.session_state.painter_state.tools, key='tool_radio')
    st.session_state.painter_state.current_tool = selected_tool
    if selected_tool == "clear_canvas":
        if st.button("Clear Canvas"):
            st.session_state.painter_state.canvas = np.zeros((720, 1280, 3), dtype=np.uint8)


with col3:
    st.subheader("Brush Size")
    brush_thickness_val = st.slider("Thickness", 1, 50, st.session_state.painter_state.brush_thickness, key='brush_slider')
    st.session_state.painter_state.brush_thickness = brush_thickness_val
    st.session_state.painter_state.eraser_thickness = brush_thickness_val * 2 

webrtc_streamer(key="painter_app", video_processor_factory=VideoProcessor, rtc_configuration=RTC_CONFIGURATION)