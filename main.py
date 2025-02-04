import numpy as np
import pandas as pd
import matplotlib as mpl
import colorcet as cc
from pathlib import Path
if __name__ == "__main__":
    mpl.use('TkAgg')
from matplotlib import pyplot as plt

INPUT_DIRECTORY=Path("./data/")
OUTPUT_DIRECTORY=Path("./figures")


def size_percentages_with_stats():
    df=pd.concat([pd.json_normalize(x["data"]).assign(year=x["year"]) for index,x in pd.read_json(INPUT_DIRECTORY/"size.json").iterrows()])
    for i in range(1,4):
        df=df.drop(f"rationale{i}",axis=1)
    a = df.groupby("year").agg(["mean","sem"])

    # each different likert value box heights (in percent) in dataframes
    stacked_box_plot_objects = []

    # for percentages, calculate total number of responses
    totals = df.groupby(["year"]).agg("count")
    for value in np.sort(np.array(df["size"].unique())):

        stacked_box_plot_objects+=[df[df["size"]==value].groupby(["year"]).agg("count")/df.groupby(["year"]).agg("count")*100]

    print(stacked_box_plot_objects)


    print(a)


    fig, ax = plt.subplots(layout="constrained")

    # stacked bar plot:
    colormap = plt.get_cmap('Blues')

    bottoms=np.zeros(len(a.index),dtype=np.float64)
    for i,(value,data) in enumerate(zip(np.sort(np.array(df["size"].unique())),stacked_box_plot_objects)):
        ax.bar(x=np.array(data.index),height=np.array([x[0] for x in data.values]),bottom=bottoms,color=colormap(float(value)/(len(stacked_box_plot_objects))), label=f"{value}")
        bottoms+=np.array([x[0] for x in data.values])

    ax.set_ylabel(r"% of responses")
    ax.set_xticks(np.array(a.index))
    ax.set_ylim([0,100])

    # legend for likert
    ax.legend(title="Group Size",loc="lower left",ncol=len(stacked_box_plot_objects),bbox_to_anchor=(0, -0.2))



    # mean with errorbars
    ax2 = ax.twinx()
    ax2.set_ylabel("Mean")
    ax2.set_ylim([1,5])
    ax2.set_yticks([1,2,3,4,5])
    years = np.array(a.index)
    means = np.array([x[0] for x in a.values])
    meancolor = "red"
    ax2.errorbar(x=years,y=means,yerr=np.array([x[1] for x in a.values]),linestyle="",color=meancolor,capsize=10, marker=".",markersize=10,label="Mean")
    for year,mean in zip(years,means):
        ax2.text(year+0.1,mean,"{:.1f}".format(mean),color=meancolor,verticalalignment="center")

    # legend for mean
    ax2.legend(loc="lower right",bbox_to_anchor=(1.0, -0.2))



    plt.savefig(OUTPUT_DIRECTORY/"size_percentages_with_stats_new.pdf")


if __name__ == "__main__":
    size_percentages_with_stats()