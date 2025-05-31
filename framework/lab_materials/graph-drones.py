import plotext as plt
import json
import time
import itertools

def graph():

    # for cycling the color of each new drone
    colors = [
        "red", "green", "purple", "cyan", "white", "purple", "gray"
    ]

    while True:
        # pull the drone positions written by the drone_hacking script
        with open("/tmp/drone_positions.json") as f:
                data = json.load(f)

        # place coordinates and drone names into separate lists
        names = list(data.keys())
        x = [n[0] for n in data.values()]
        y = [n[1] for n in data.values()]

        plt.clear_figure()

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
    graph()