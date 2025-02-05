import numpy as np
from vpython import *

# Set up the scene
scene = canvas(title="DNA Helix Visualization", width=800, height=600, background=color.white)

# Define DNA parameters
radius = 10
pitch = 34
num_base_pairs = 20

# Create the DNA backbone
helix1 = curve(color=color.blue, radius=0.5)
helix2 = curve(color=color.red, radius=0.5)

# Generate helix points
t = np.linspace(0, num_base_pairs * pitch, num_base_pairs * 10)
x = radius * np.cos(2 * np.pi * t / pitch)
y = radius * np.sin(2 * np.pi * t / pitch)
z = t

# Add points to the helices
for i in range(len(t)):
    helix1.append(vec(x[i], y[i], z[i]))
    helix2.append(vec(-x[i], -y[i], z[i]))

# Add base pairs
for i in range(0, len(t), 10):
    cylinder(pos=vec(x[i], y[i], z[i]), axis=vec(-2*x[i], -2*y[i], 0), radius=0.3, color=color.green)

# Add labels
label(pos=vec(0, radius + 5, 0), text="DNA Helix", height=16, color=color.black)

# Run the visualization
while True:
    rate(30)
    scene.camera.rotate(angle=0.01, axis=vec(0, 1, 0))
