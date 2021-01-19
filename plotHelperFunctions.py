

def reduceToOnePositions(preflopLines, position):
    #limit Preflop raise hands by position in the table
    df = preflopLines.copy()
    df = df.reset_index()
    position ='Dealer'
    df = df[df['Positions'] == position]

    return df


def createIndividualCardData(df):

    #create individual card values
    df[['card0','card1']] = pd.DataFrame(df['Hand'].tolist(), index=df.index)
    df['card0_value'] = df['card0'].str[0]
    df['card1_value'] = df['card1'].str[0]

    #create suited column
    df['suited'] = df['card0'].str[1] == df['card1'].str[1]

    return df

def createPivot(df, suited = False):

    #limit field to suited or unsuited
    df = df[df['suited'] == suited]

    #reduce to just a Dataframe with the cards
    reduceddf = df[['card0_value','card1_value']].copy()

    #convert to value so these can be sorted
    reduceddf['card0_value'], reduceddf['card1_value'] = reduceddf['card0_value'].map(CardValuedict) , reduceddf['card1_value'].map(CardValuedict)

    #sort all small values onto one side so we can make our stair case figure
    #     1 x - -
    #     3 x x x
    #     2 x x -
    ###     3 2 1
    reduceddf['card0_value'], reduceddf['card1_value'] = reduceddf.min(axis=1), reduceddf.max(axis=1)

    #inverse the dictionary
    inv_CardValuedict = {v: k for k, v in CardValuedict.items()}

    #convert back to card value
    reduceddf['card0_value'], reduceddf['card1_value'] = reduceddf['card0_value'].map(inv_CardValuedict) , reduceddf['card1_value'].map(inv_CardValuedict)

    reduceddf.reset_index()
    #set value so that we can count occasions in a pivot
    reduceddf['value'] = 1

    #create pivot table

    if suited:
        df_piv = reduceddf.pivot_table(index = ['card1_value'], columns = 'card0_value',aggfunc = 'count', values = 'value')
        df_piv = df_piv.reindex(CardValues, columns=CardValues)
    else:
        df_piv = reduceddf.pivot_table(index = ['card0_value'], columns = 'card1_value',aggfunc = 'count', values = 'value')
        df_piv = df_piv.reindex(CardValues, columns=CardValues)

    return df_piv

def createHandChartLabels():
    FullHandChartLables = np.empty((len(CardValues),len(CardValues)),dtype= 'object')

    for i in range(len(CardValues)):
        for j in range(len(CardValues)):
            if j < i:
                FullHandChartLables[i][j] = str(CardValues[i] + CardValues[j] +'o')
            elif j==i:
                FullHandChartLables[i][j] = str(CardValues[i]) + str(CardValues[j])
            else:
                FullHandChartLables[i][j] = str(CardValues[i] + CardValues[j] +'s')
    return FullHandChartLables


def createHandRangeFig(df, cmap = 'coolwarm', threshold = 0):
    #create the suited hands and off suited, then merge into one figure
    df_piv_offsuit = createPivot(df, False)
    df_piv_suited = createPivot(df, True)

    #replace Nan with zeros so the figures can be added
    df_piv_offsuit = df_piv_offsuit.fillna(0)
    df_piv_suited = df_piv_suited.fillna(0)

    df_piv_combined = df_piv_suited + df_piv_offsuit



    fig, ax = plt.subplots()
    ax.set_xticks(np.arange(len(CardValues)))
    ax.set_yticks(np.arange(len(CardValues)))

    ax.set_xticklabels(CardValues)
    ax.set_yticklabels(CardValues) #set to the poker range convention

    ax.xaxis.tick_top()


    df_piv_combined = df_piv_combined > threshold

    ax.imshow(df_piv_combined, cmap='coolwarm')

    FullHandChartLables = createHandChartLabels()
    for i in range(len(CardValues)):
        for j in range(len(CardValues)):
            text = ax.text(j, i, FullHandChartLables[i, j],
                           ha="center", va="center", color="k")
