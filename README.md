#  Virtual Painter

A professional-grade virtual painting application that transforms your webcam into an interactive canvas, enabling you to create digital art using hand gestures or mouse controls.

![Virtual Painter Demo](/screenshots/v.png)
![Virtual Painter Demo](/screenshots/v2.png)
![Virtual Painter Demo](/screenshots/v1.png)

## ✨ Features

- **Intuitive Controls** - Paint using either hand gestures (via webcam) or traditional mouse input
- **Multiple Tools** - Express your creativity with various drawing tools:
  - Brush
  - Eraser
  - Rectangle (outline and filled)
  - Circle (outline and filled)
  - Line tool
- **Color Palette** - Choose from 12 vibrant colors
- **Adjustable Brush Sizes** - Customize your brush thickness for precise control
- **Gesture Recognition** - Uses MediaPipe hand tracking for pinch-to-draw functionality
- **Canvas Manipulation** - Clear canvas option to start fresh
- **Smooth Drawing** - Point averaging for smoother lines and reduced jitter
- **Professional UI** - Clean, intuitive interface with visual feedback

## 🖥️ Requirements

- Python 3.6+
- OpenCV (`cv2`)
- NumPy
- MediaPipe
- Webcam (for hand gesture functionality)

## 📋 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/sayyedrabeeh/virtual-painter.git
   cd virtual-painter
   ```

2. Install the required packages:
   ```bash
   pip install opencv-python numpy mediapipe
   ```

3. Run the application:
   ```bash
   python virtual_painter.py
   ```

## 🎮 How to Use

### Mouse Controls
- **Select Colors/Tools**: Click on the buttons at the top of the screen
- **Draw**: Click and drag on the canvas area
- **Create Shapes**: Click to set the starting point, drag to adjust size/position, and release to place the shape

### Hand Gesture Controls
- **UI Interaction**: Move your index finger to the top of the screen to select tools and colors
- **Drawing**:
  - Make a pinching gesture with your index and middle fingers to start drawing
  - Release the pinch to stop drawing
  - For shapes, pinch at the starting point, move to adjust size, and release to place

### Buttons and Functions
- **Color Selection**: Choose from 12 vibrant colors (top left)
- **Tool Selection**: Select your desired drawing tool (middle top)
- **Brush Size Control**: Adjust the thickness of your brush using + and - buttons (top right)
- **Clear Canvas**: Reset your entire canvas to start over

## 🔧 Technical Details

The application uses:
- **OpenCV** for image processing and UI rendering
- **MediaPipe** for hand landmark detection and tracking
- **NumPy** for efficient array operations
- **Collections.deque** for smooth point tracking and interpolation

Hand detection tracks your index finger for pointing and detects "pinch" gestures (index finger and middle finger proximity) for drawing actions.

## 🛠️ Customization

You can easily customize the application by modifying these parameters in the code:

- Add more colors to the `colors` list
- Adjust brush sizes in the `brush_size` list
- Add new tools to the `tools` list (requires implementing corresponding drawing functions)
- Change UI dimensions in the initialization section


## 🙏 Acknowledgements

- [OpenCV](https://opencv.org/) - The backbone of our computer vision functionality
- [MediaPipe](https://mediapipe.dev/) - For the amazing hand tracking capabilities
- [NumPy](https://numpy.org/) - For efficient numerical operations

---

Developed with ❤️ by [sayyed rabeeh]

## Happy Coding 