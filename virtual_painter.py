import cv2
import numpy as np
import mediapipe as mp
import time 
import os
from collections import deque

class VirtualPainter:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)  
        self.cap.set(4, 720)
        self.canvas = np.zeros((720,1280,3),dtype=np.uint8) 
        self.temp_canvas = np.zeros((720,1280,3),dtype=np.uint8)
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.7)
        self.colors = [(0,0,255), (0,127,255), (0,255,255), (0,255,0), (255,0,0), (255,0,255), (150,150,150)]
        self.current_color = self.colors[0]
        self.brush_size = [5,10,15,20,30]
        self.brush_size_index = 2
        self.brush_thickness = self.brush_size[self.brush_size_index]
        self.eraser_thickness = 40 
        self.tools = ["brush", "eraser", "rectangle", "circle", "line"]
        self.current_tools = "brush"

        self.save_dir = "paintings"
        os.makedirs(self.save_dir, exist_ok=True)


        self.drawing = False
        self.prev_x = self. prev_y = 0 
        self.start_x = self.start_y = 0
        self.point_history = deque(maxlen=5)
        self.last_ui_inctration_time = 5 

        self.prev_time = 0 

        self.button_height = 60 
        self.color_button_width = 40
        self.tool_button_width = 120 
        self.action_button_width = 100 

        self.mouse_dwon = False
        cv2.namedWindow('proffessional virtual painter ')
        cv2.setMouseCallback('proffessional virtual painter ',self.mouse_events)

    def smooth_points(self,x,y):
        self.point_history((x,y))
        avg_x = int(np.mean(pt[0] for pt in self.point_history))   
        avg_y = int(np.mean(pt[1] for pt in self.point_history))   
        return avg_x,avg_y
    
    def mouse_events(self, event, x, y, flags, param):
        if y < self . button_height + 20 :
            if event == cv2.EVENT_LBUTTONDOWN:
                self.handle_ui_inctrations(x,y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_dwon =True      
            self.drawing = True
            self.prev_x ,self.prev_y = x,y
            self.start_x,self.start_y = x,y
        elif event == cv2.EVENT_LBUTTONUP:
              self.mouse_dwon = False
              self.drawing =False
              if self.current_tools in ["rectangle", "circle", "line"]:
                   self.draw_shape(self.canvas, self.current_tool, self.start_x, self.start_y, x, y, self.current_color, self.brush_thickness)
        elif event == cv2.EVENT_MOUSEMOVE and self.mouse_dwon:
            if self.current_tools in  ["brush", "eraser"]:
                self.draw_brush(self.canvas,x,y)
    def draw_ui(self,frame):
        for i ,color in enumerate(self.colors):
             x_starts = 10 + i * (self.color_button_width + 5 )
             cv2.rectangle(frame,(x_starts,10,),(x_starts+self.color_button_width),self.button_height,color,-1)
             if color == self.current_color:
                 cv2.rectangle(frame, (x_starts-2, 8), (x_starts+self.color_button_width+2, self.button_height+2), (255,255,255), 2)
            
        tool_starts_x = 10 + len(self.colors) * (self.color_button_width +5) +20
        for i ,tool in enumerate(self.tool):
            x_start = tool_starts_x + i * (self.tool_button_width +5)
            color = (200,200,200)
            cv2.rectangle(frame,(x_start,10),(x_start+self.tool_button_width,self.button_height),color-1,)
            if tool == self.current_tools:
                cv2.rectangle(frame,(x_start,10),(x_start+self.tool_button_width,self.button_height),(0,255,0),2)
            cv2.putText(frame,tool.title(),x_start+10,45,cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),2)

        brush_ui_x = tool_starts_x + len(self.tools) * (self.tool_button_width + 5) + 20
        cv2.putText(frame,f"Size: {self.brush_thickness}",(brush_ui_x+30),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),2)
        cv2.rectangle(frame, (brush_ui_x, 40), (brush_ui_x+20, 50), (0,0,0), 2)
        cv2.putText(frame, "-", (brush_ui_x+5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
        cv2.rectangle(frame, (brush_ui_x+30, 40), (brush_ui_x+50, 50), (0,0,0), 2)
        cv2.putText(frame, "+", (brush_ui_x+35, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

        action_x = brush_ui_x +70 
        cv2.rectangle(frame,(action_x,10),(action_x+self.action_button_width,self.button_height),(100,100,255),-1)
        cv2.putText(frame,'clear',(action_x+20,45),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),2)

        action_x += self.action_button_width + 5
        cv2.rectangle(frame, (action_x, 10), (action_x + self.action_button_width, self.button_height), (100,255,100), -1)
        cv2.putText(frame, "Save", (action_x+20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

        fps = int(1 / (time.time() - self.prev_time + 1e-5))
        self.prev_time = time.time()
        cv2.putText(frame, f"FPS: {fps}", (10, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,100), 2)

        





































































    def run(self):
        while True:
            ret, frame = self.cap.read()   
            if not ret:
                break  

            cv2.imshow("Webcam Feed", frame)  

            if cv2.waitKey(1) & 0xFF == ord('q'):   
                break

        self.cap.release()  
        cv2.destroyAllWindows()   

if __name__ == "__main__":
    painter = VirtualPainter()
    painter.run()