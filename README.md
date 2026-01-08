# Python Solar System Simulator 🪐🔭

A high-performance N-Body gravity simulation built with Python and Pygame. This application simulates the orbits of the 8 planets around the Sun using Newton's Law of Universal Gravitation, with optional General Relativity corrections for Mercury.

**🔗 [View the Repository]([https://github.com/WhiteSkyTK/Orbit-Sumulation])**

## 🚀 Features

* **Real-time N-Body Physics:** Every planet attracts every other planet.
* **Interactive Camera:** Pan and Zoom (Scroll Wheel) to explore the vast distances of space.
* **Simulation Controls:**
    * **Adjust Gravity (G):** See what happens to orbits when gravity is doubled.
    * **Time Step:** Speed up or slow down time.
    * **Relativity Mode:** Toggles a simulation of Einstein's General Relativity (causes Mercury's orbit to precess).
    * **Sun Lock:** Unlock the Sun to see how the planets' gravity pulls the Sun off-center (Wobble effect).
* **Live Data:** Click on any planet to see its current Velocity, Distance from Sun, and Mass.

## 🛠️ Installation & Run

### Prerequisites
* Python 3.x
* Pygame

### 1. Install Dependencies
Open your terminal and install Pygame:

```bash
pip install pygame

Clone the repo and run the script:

Bash

python main.py

🎮 ControlsInputActionMouse DragPan the CameraScroll WheelZoom In / OutLeft ClickSelect a Planet (View Stats)UI SlidersChange Gravity or Time SpeedButtonsReset, Toggle Relativity, Unlock Sun🧠 The Physics Behind ItThe simulation calculates the force applied to every body by every other body using Newton's Law of Universal Gravitation:
![licensed-image](https://github.com/user-attachments/assets/35e61760-d153-411b-8d15-815b583398ca)

Where:

F is the force between the masses.

G is the gravitational constant (adjustable in the UI).

m1 and m2 are the masses.

r is the distance between them.

General Relativity (Mercury)
When "Relativity" is enabled, a small perturbation force is added to the simulation based on the Post-Newtonian Expansion. This allows us to visualize the Precession of the Perihelion of Mercury, a phenomenon Newton's laws alone cannot explain!

🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

📜 License
Open Source. Free to use for educational purposes.
