import matplotlib.pyplot as plt
import fastf1

from proton import session


session = fastf1.get_session(2025, 'Belgium', 'Q')
session.load()

ver_lap = session.laps.pick_drivers('VER').pick_fastest()

# Get position data
pos_data = ver_lap.get_pos_data()

# Plot track shape
fig, ax = plt.subplots(figsize=(10, 10))
ax.plot(pos_data['X'], pos_data['Y'], linewidth=5)
ax.set_aspect('equal')
ax.set_xlabel('X Position')
ax.set_ylabel('Y Position')
ax.set_title('Track Layout')
plt.show()