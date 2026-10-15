from pathlib import Path
import matplotlib.pyplot as plt
from acp4.config.config import Config
config = Config()


mapping = {
    "camel": "CAMELS-DE",
    "agro_herxheimweyher": "Herxheimweyher (Agrometeo)",
    "agro_steinweiler": "Steinweiler (Agrometeo)",
}

months_abbreviations = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

seasons = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn",
    }

season_colors = {
        "Winter": "skyblue",
        "Spring": "lightgreen",
        "Summer": "gold",
        "Autumn": "sandybrown",
    }

percentile_mapping = {
    "daily": "Daily",
    "q05": "5th percentile",
    "q95": "95th percentile",
}


def save_plot(
    plot: plt.figure,
    name: str,
    ) -> None:
    
    plot.savefig(
        Path(config.plot_output_dir) / f"{name}.png",
        dpi=300,
        bbox_inches="tight",
    )