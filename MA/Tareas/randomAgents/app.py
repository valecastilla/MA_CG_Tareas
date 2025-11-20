from random_agents.agent import RandomAgent, ObstacleAgent, TrashAgent, ChargingStationAgent
from random_agents.model import RandomModel

from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
    make_plot_component,
)

from mesa.visualization.components import AgentPortrayalStyle


def random_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
    )

    if isinstance(agent, RandomAgent):
        portrayal.color = "red"
    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "gray"
        portrayal.marker = "s"
        portrayal.size = 100
    elif isinstance(agent, TrashAgent):
        portrayal.color = "green"
        portrayal.marker = "s"
        portrayal.size = 50
    elif isinstance(agent, ChargingStationAgent):
        portrayal.color = "blue"
        portrayal.marker = "s"
        portrayal.size = 50

    return portrayal

def post_process(ax):
    ax.set_aspect("equal")

model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "num_agents": Slider("Number of agents", 1, 1, 50),
    "num_obstacles": Slider("Number of obstacles", 5, 1, 100), # For obstacle min 0 max 100 and default 10 
    "num_trash": Slider("Number of trash", 10, 1, 100), # For trash min 0 max 100 and default 10
    "width": Slider("Grid width", 28, 1, 50),
    "height": Slider("Grid height", 28, 1, 50),
}

def post_process_space(ax):
    ax.set_aspect("equal")

def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))

lineplot_component = make_plot_component(
    {"RandomAgent": "tab:red", "TrashAgent": "tab:green"},
    post_process=post_process_lines
)

# Create the model using the initial parameters from the settings
model = RandomModel(
    num_agents=model_params["num_agents"].value,
    num_obstacles=model_params["num_obstacles"].value,
    num_trash=model_params["num_trash"].value,
    width=model_params["width"].value,
    height=model_params["height"].value,
    seed=model_params["seed"]["value"]
)

space_component = make_space_component(
        random_portrayal,
        draw_grid = False,
        post_process=post_process
)

page = SolaraViz(
    model,
    components=[space_component, lineplot_component],
    model_params=model_params,
    name="Random Model",
)
