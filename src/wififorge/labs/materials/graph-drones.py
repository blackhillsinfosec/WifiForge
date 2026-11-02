import itertools
import json
import sys
import time

_PLOTEXT_FIX = "    sudo pip install --break-system-packages 'plotext>=5.2,<6'"

try:
    import plotext as plt
except ImportError:
    sys.exit("plotext is not installed for this python3. Install it with:\n" + _PLOTEXT_FIX)

# plotext 6 dropped the 5.x plotting API (scatter, clear_figure, ...) this
# script uses; with it installed the graph died on its first frame.
if not all(hasattr(plt, name) for name in ("scatter", "clear_figure", "clear_terminal", "show")):
    sys.exit(
        f"This plotext ({getattr(plt, '__version__', 'unknown version')}) is not compatible "
        "with the drone tracker. Install the 5.x series with:\n" + _PLOTEXT_FIX
    )

DRONE_PATH = "/tmp/drone-info.json"


def read_drones(last):
    """Return the drone data, or the last good copy if the file is mid-write.

    control-drones.py rewrites the file on every key press; reading it at the
    wrong moment used to raise JSONDecodeError and kill the graph.
    """
    try:
        with open(DRONE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return last


def graph():

    # for cycling the color of each new drone
    colors = [
        "red", "green", "purple", "cyan", "white", "purple", "gray"
    ]

    data = None
    while data is None:
        data = read_drones(None)
        if data is None:
            print(f"Waiting for {DRONE_PATH} (is the Drone Hacking lab running?)...")
            time.sleep(1)

    while True:
        # pull the drone positions written by the drone_hacking lab / controller
        data = read_drones(data)

        # place coordinates and drone names into separate lists
        names = list(data.keys())
        x = [data[name]["position"][0] for name in names]
        y = [data[name]["position"][1] for name in names]

        plt.clear_figure()
        plt.clear_terminal()  # redraw in place instead of scrolling the pane

        # graph colors!!
        plt.canvas_color("black")
        plt.axes_color("black")
        plt.ticks_color("white")

        # iterate the drone color and plot the drones
        color_cycle = itertools.cycle(colors)

        for i, name in enumerate(names):
            color = next(color_cycle)
            plt.scatter([x[i]], [y[i]], label=name, color=color, marker="#")

        # graph X and Y max values
        plt.title("Drone Tracker")

        # axes labels - this maximum is also specified in the drone controller
        plt.xlim(0, 30)
        plt.ylim(0, 30)

        # load the graph, refresh interval
        plt.show()
        time.sleep(0.5)

if __name__ == '__main__':
    try:
        graph()
    except KeyboardInterrupt:
        pass
