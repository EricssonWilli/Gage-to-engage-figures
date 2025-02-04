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
    df=pd.concat([pd.json_normalize(x["data"]).assign(year=x["year"]) for index,x in pd.read_json(INPUT_DIRECTORY/"size.json").iterrows()],ignore_index=True)
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


def alternate_gagefigure():
    import json
    pre_search_string = "Pre-questionnaire"
    post_search_string = "Self-estimates"

    with open(INPUT_DIRECTORY/"eerik_2021_2024.json",'r') as f:
        jsonobj = json.load(f)

    dataframes=[]
    # find the correct exercises
    for year,exercises in jsonobj.items():
        print("Going through year",year)
        for exercise_id,submissions in exercises.items():
            if len(submissions)==0:
                continue
            if pre_search_string in submissions[0]["Exercise"]:
                print("pre exercise for year",year,"found, submission count",len(submissions))
                dataframes+=[pd.json_normalize(submissions)[[f"row{i}" for i in range(1,21)]].astype(np.float64).assign(year=int(year)).assign(prepost="pre")]
            elif post_search_string in submissions[0]["Exercise"]:
                print("post exercise for year",year,"found, submission count",len(submissions))
                dataframes+=[pd.json_normalize(submissions)[[f"row{i}" for i in range(1,21)]].astype(np.float64).assign(year=int(year)).assign(prepost="post")]

    df = pd.concat(dataframes,ignore_index=True)
    # print(df)
    # print(df.dtypes)
    # return
    # dataframe now correct format and ready for further working

    # category order
    hardest_categories=df.drop(["prepost","year"],axis=1).agg("mean").sort_values()
    print("Categories from (averaged self reflects) hardest to easiest (combined pre/post)")
    print(hardest_categories)

    ordered_categories = np.array(hardest_categories.index)



    aggregate_values = df.groupby(["prepost","year"],dropna=False).agg(["mean","sem"])

    ordered_aggregate_values = aggregate_values[ordered_categories]
    print(ordered_aggregate_values)

    fig,ax = plt.subplots(layout="constrained")
    print(ordered_aggregate_values.keys())
    # return
    years=[2021,2022,2023,2024]
    for prepost,colormap in zip(["pre","post"],[plt.get_cmap("Blues"),plt.get_cmap("Reds")]):
        for year in years:
            ax.errorbar(ordered_categories,np.array([[y[cat]["mean"] for cat in ordered_categories] for x,y in ordered_aggregate_values.iterrows() if x[0]==prepost and x[1]==year]).transpose(),label=f"{prepost} {year}",color=colormap(float(year-2020)/5))

    ax.tick_params(axis="x",labelrotation=45)
    ax.set_xlabel("Categories from all time average harderst to easiest")
    ax.set_ylabel("Perceived difficulty")
    ax.set_ylim([1,5])

    ax.legend()
    plt.savefig(OUTPUT_DIRECTORY/"alternate_gagefigure.pdf")
    # print(aggregate_values)


def correlation():
    df=pd.concat([pd.json_normalize(x["data"]).assign(year=x["year"]) for index,x in pd.read_json(INPUT_DIRECTORY/"size_with_counts.json").iterrows()],ignore_index=True)

    df=df[["size","count","year"]]
    corr_method = "spearman"
    a = df.groupby("year").corr(method=corr_method)#.agg(["mean","sem"])
    b = df.drop("year",axis=1).corr(method=corr_method)

    print(f"Correlations per year (using {corr_method} correlation)")
    print(a)

    print(f"\nGeneral correlation (using {corr_method} correlation)")
    print(b)
    return

if __name__ == "__main__":
    # size_percentages_with_stats()
    # alternate_gagefigure()
    correlation()
