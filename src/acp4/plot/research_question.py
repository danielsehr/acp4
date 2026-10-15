import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cmcrameri.cm as cmc


def plot_cross_correlation(
    df: pd.Series,
    max_lag: int = 10,
    ) -> plt.figure:
    
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(
        df,
        marker="o"
    )

    ax.set_xlabel("Precipitation lead time (days)")
    ax.set_ylabel("Pearson correlation (r)")
    ax.set_title("Cross-correlation of precipitation and discharge, CAMELS-DE")
    
    ax.set_xticks(range(max_lag + 1))
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

    print("Lag with highest correlation:", df.idxmax(), "days")
    print("Maximum correlation:", df.max().round(3))
    
    return fig
    
    

def plot_correlation_heatmap(df: pd.DataFrame) -> plt.figure:

    fig, ax = plt.subplots(figsize=(10, 4))

    sns.heatmap(
        df,
        annot=True,
        fmt=".2f",
        cmap=cmc.vik,
        vmin=-1,
        vmax=1,
        center=0,
        ax=ax,
        cbar_kws={"label": "Pearson correlation coefficient (r)"},
    )
    
    ax.invert_yaxis()
    ax.set_xlabel("Lag [days]")
    ax.set_ylabel("Season of precipitation")
    ax.set_title("Seasonal precipitation–discharge cross-correlation, CAMELS-DE")

    fig.tight_layout()
    plt.show()
    
    return fig