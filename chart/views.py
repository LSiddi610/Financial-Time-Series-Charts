from lib2to3.pytree import convert
from django.shortcuts import render
from pandas import DataFrame,concat
from bokeh.plotting import figure
from bokeh.plotting import ColumnDataSource
from bokeh.embed import components
from bokeh.layouts import row,column,gridplot
from bokeh.palettes import Category10,Category20
from bokeh.models import (
Span,HoverTool,NumeralTickFormatter,DataTable,TableColumn,
 HTMLTemplateFormatter, DateFormatter,Tabs, Panel,Div,Slider,
 MultiChoice,CheckboxButtonGroup,RadioButtonGroup,TextInput,Select)
from chart.technical_indicators import bollinger_bands,relative_strength_index,stochastic_oscillator
from chart.callback import (Bollinger_band_lags,oscillator_callback,Swap_quantile_stacked,
Stacked_features,Swap_quantile_continuation,risk_reward )
import numpy as np
# Create your views here.



screen_width = 1920#tk_screen.winfo_screenwidth()
screen_height = 1080#tk_screen.winfo_screenheight()

plot_width               = int(0.9*screen_width)
plot_height_settle       = int(.65*screen_height)
plot_height_indicator    = int(.35*screen_height)
min_border_left          = 10
min_border_top_rsi       = 0
min_border_bottom_settle = 0


font_size                     = "12pt"
title_font_size               = "14pt"



def set_font_n_ticker_size(plot):
    plot.yaxis.axis_label_text_font_size = font_size
    plot.yaxis.major_label_text_font_size = font_size
    plot.xaxis.axis_label_text_font_size = font_size
    plot.xaxis.major_label_text_font_size = font_size
    plot.title.text_font_size = title_font_size
    

    return plot

def dashboard(request):

    tabs = []
    tabs.append(first_panel())
    tabs.append(second_panel())
    tabs.append(third_panel())

    tabs = Tabs(tabs=tabs)
    script, div = components(tabs)
    
    content     = {'script':script,'div':div}
    template    = 'chart/dashboard.html'

    return render(request,template,content)



def first_panel():

    n = 1000
    t = np.linspace(0,5,n,endpoint=True)

    last = .5

    df = DataFrame({'Spread':np.exp(np.cos(2*np.pi*t)+0.1*np.random.normal()),'Trend':np.sin(2*np.pi*t),'Date':t})
    df = concat([df,bollinger_bands(df["Spread"])],axis=1)
    df.loc[:,'Oscillator1'] = relative_strength_index(df["Spread"],period=14)
    df.loc[:,'Oscillator2'] = stochastic_oscillator(df["Spread"],14)
    
    df_oscillator1 = bollinger_bands(df[["Oscillator1"]])
    df_oscillator1.rename(columns={xx:"_".join(['Oscillator1',xx]).replace(" ","_") for xx in list(df_oscillator1.columns)},inplace=True)
    df_oscillator2 = bollinger_bands(df[["Oscillator2"]])
    df_oscillator2.rename(columns={xx:"_".join(['Oscillator2',xx]).replace(" ","_") for xx in list(df_oscillator2.columns)},inplace=True)

    df = concat([df,df_oscillator1,df_oscillator2],axis=1)
    
    df.rename(columns={"Rolling Mean":"Rolling_Mean", "Upper Band":"Upper_Band","Lower Band":"Lower_Band"},inplace=True)
    dictionary_bb_callback_name={"Rolling_Mean":"Rolling_Mean", "Upper_Band":"Upper_Band","Lower_Band":"Lower_Band","Spread":"Spread"}
    
    dh = df.iloc[1:] 
    dh['Left'] = df.index[:-1]
    dh['Right'] = df.index[1:]


    dg_positive = DataFrame({'Year':[str(xx) for xx in range(2010,2015)],'Positive':[10,np.nan,12,14,np.nan]})
    dg_positive2 = DataFrame({'Year':[str(xx) for xx in range(2010,2015)],'Positive':[10,np.nan,12,14,np.nan]})
    dg_negative = DataFrame({'Year':[str(xx) for xx in range(2010,2015)],'Negative':[np.nan,-20,np.nan,np.nan,-30]})
    dg_negative2 = DataFrame({'Year':[str(xx) for xx in range(2010,2015)],'Negative':[-5,-22,-1,0,-30]})

    gauss1 = np.random.normal(0,1,500)
    hist, edges = np.histogram(gauss1, density=False, bins=50)
    dg_hist = DataFrame({'Last 15 Years':hist})
    dg_hist['Left'] = edges[:-1]
    dg_hist['Right'] = edges[1:]


    gauss2 = np.random.normal(0.1,2,500)
    hist, edges = np.histogram(gauss2, density=False, bins=50)
    dg_hist2 = DataFrame({'Last 10 Years':hist})
    dg_hist2['Left'] = edges[:-1]
    dg_hist2['Right'] = edges[1:]

    actual_price = 2


    dict_data_return = {'x_axis':list(dg_positive['Year']),'Positive Mean':np.mean(dg_positive["Positive"].dropna()),
    'Negative Mean':np.mean(dg_negative["Negative"].dropna()),'Positive Size':dg_positive.dropna().shape[0],
    'Negative Size':dg_negative.dropna().shape[0],'title':'Returns',}



    dict_data_return2 = {'x_axis':list(dg_positive2['Year']),'Positive Mean':np.mean(dg_positive2["Positive"].dropna()),
    'Negative Mean':np.mean(dg_negative2["Negative"].dropna()),'Positive Size':dg_positive2.dropna().shape[0],
    'Negative Size':dg_negative2.dropna().shape[0],'title':'Best & Worst',
    'Percentiles Positive':{'{}'.format("".join([str(int(xx*100)),'%'])):np.quantile(list(dg_positive2["Positive"].dropna()),xx) for xx in [0.9,0.75,0.5,0.25,0.1] },
    'Percentiles Negative':{'{}'.format("".join([str(int(xx*100)),'%'])):np.quantile(list(dg_negative2["Negative"].dropna()),xx) for xx in [0.01,0.025,0.05,0.1,0.15]},
    'Position':1,'Unit Move':10,'Actual':0.5}

    df = ColumnDataSource(df)
    dh = ColumnDataSource(dh)
    dg_positive = ColumnDataSource(dg_positive.dropna())
    dg_negative = ColumnDataSource(dg_negative.dropna())
    dg_positive2 = ColumnDataSource(dg_positive2.dropna())
    dg_negative2 = ColumnDataSource(dg_negative2.dropna())

    df_dict = {'df':df}
    df_dict_oscillator1 = {'df':df}
    df_dict_oscillator2 = {'df':df}
    df_hist = {'df':dg_hist,'dg':dg_hist2}
    df_volume = {'df':dh}

    df_hist_label = {'df':["Last 15 Years"],'dg':["Last 10 Years"]}
    df_positive_negative = {'Positive':dg_positive,'Negative':dg_negative}
    df_positive_negative2 = {'Positive':dg_positive2,'Negative':dg_negative2}
    label_dict_positive_negative = {'Positive':"Positive",'Negative':"Negative"}
    label_dict_positive_negative2 = {'Positive':"Positive",'Negative':"Negative"}    

    label_dict = {'df':["Spread","Trend","Rolling_Mean", "Upper_Band","Lower_Band"]}
    oscillator_label_dict1 = {'df':["Oscillator1","Oscillator1_Rolling_Mean", "Oscillator1_Upper_Band","Oscillator1_Lower_Band"]}
    oscillator_label_dict2 = {'df':["Oscillator2","Oscillator2_Rolling_Mean", "Oscillator2_Upper_Band","Oscillator2_Lower_Band"]}

    slider_bb = Slider(start=5, end=50, value=20, step=1, title="Bollinger Band")
    select_oscillator1 = Select(title="", value="RSI", options=["RSI","Stochastic"], width=180)
    slider_oscillator1 = Slider(start=5, end=50, value=14, step=1, title="Oscillator 1")
    select_oscillator2 = Select(title="", value="Stochastic", options=["RSI","Stochastic"], width=180)
    slider_oscillator2 = Slider(start=5, end=50, value=14, step=1, title="Oscillator 2")


    callback_bb = Bollinger_band_lags(df, slider_bb,dictionary_bb_callback_name)

    slider_bb.js_on_change('value', callback_bb)
    
    plots = [row(slider_bb,select_oscillator1,slider_oscillator1,select_oscillator2,slider_oscillator2)]

    widgets1 = {'Select':select_oscillator1,'Slider':slider_oscillator1}
    widgets2 = {'Select':select_oscillator2,'Slider':slider_oscillator2}


    list_selection_risk = ["1%","2%","5%","10%","15%"]
    list_selection_reward = ["10%","25%","50%","75%","90%"]

    reward_select = Select(title="Reward - Quantile:", value=list_selection_reward[2], options=list_selection_reward, width=180)
    risk_select   = Select(title="Risk - Quantile:", value=list_selection_risk[1], options=list_selection_risk, width=180)
    input_price   = TextInput(title="Entry Price", value=str(round(last,4)), width=180)
    widgets3      = {'Reward':reward_select,'Risk':risk_select,'Price':input_price}
    main_chart = main_graph(df_dict,label_dict,dict_data_return2,None,'Settlement Price')
    plots.append(main_chart['Main Plot'])
    plots.append(oscillators(df_dict_oscillator1,oscillator_label_dict1,widgets1,None,''))
    plots.append(oscillators(df_dict_oscillator2,oscillator_label_dict2,widgets2,'below',''))
    plots.append(barchart(df_volume,{'df':["Spread"]},{'x_axis':'below','title':'Volume'}))




    plots.append(plot_histogram(df_hist,df_hist_label,actual_price,x_axis='below',title='Price Distribution'))
    returns = barchart_with_sign(df_positive_negative,label_dict_positive_negative, {}, dict_data_return)
    returns2 = barchart_with_sign(df_positive_negative2,label_dict_positive_negative2,widgets3, dict_data_return2,main_chart['Lines'])

    
    plots.append( gridplot([[None, row(reward_select,risk_select,input_price,align="center")], [returns,  returns2]] ) )
    #plots.append(row(returns,returns2))

    return (Panel(child = column(plots),title='Settle'))


def second_panel():

    n = 200
    t = np.linspace(0,5,n,endpoint=True)
    df = DataFrame(.1*np.random.normal(0,1,(n,10)))
    df = df.apply(lambda xx:xx+np.cos(2*np.pi*t))
    df.columns = [str(ii+1) for ii in range(2000,2010)]
    df['Date'] = t

    columns_name = [xx for xx in list(df.columns) if xx.isnumeric()]
    columns_name.sort()
    dg = df[columns_name]
    df_stacked      = dg.copy()
    df_normalized   = (dg-dg.min())/(dg.max()-dg.min())
    df_standardized = (dg-dg.mean())/dg.std()
    df_returns = dg.pct_change()
    df_volatility30 = df_returns.rolling(window=30,center=False).std()
    df_volatility60 = df_returns.rolling(window=60,center=False).std()

    df_stacked.rename(columns={xx:" ".join(["Stacked",xx]) for xx in columns_name},inplace=True)
    df_normalized.rename(columns={xx:" ".join(["Stacked Normalized",xx]) for xx in columns_name},inplace=True)
    df_standardized.rename(columns={xx:" ".join(["Stacked Standardized",xx]) for xx in columns_name},inplace=True)
    df_volatility30.rename(columns={xx:" ".join(["Rolling Volatility 30 days",xx]) for xx in columns_name},inplace=True)
    df_volatility60.rename(columns={xx:" ".join(["Rolling Volatility 60 days",xx]) for xx in columns_name},inplace=True)

    df = concat([df,df_stacked,df_normalized,df_standardized,df_volatility30,df_volatility60],axis=1)
    df_dict = {'df':ColumnDataSource(df),'Lower Percentile 15Y':np.quantile(df[columns_name],0.1),'Upper Percentile 15Y':np.quantile(df[columns_name],0.90),
    'Lower Percentile 5Y':np.quantile(df[columns_name[-5:]],0.1),'Upper Percentile 5Y':np.quantile(df[columns_name[-5:]],0.90)}

    label_dict = {'df':columns_name}
    
    list_selection_stacked = ["Stacked","Stacked Normalized","Stacked Standardized","Rolling Volatility 30 days","Rolling Volatility 60 days"]
    dropdown = Select(title="", value=list_selection_stacked[0], options=list_selection_stacked, width=180)
    radiobutton = RadioButtonGroup(labels = ["Percentiles Last 15 Years", "Percentiles Last 5 Years"], active = 0)
    checkbox_button_group = CheckboxButtonGroup(labels=["Hide Lines"], active=[0, 1])

    plots = [row(dropdown,radiobutton,checkbox_button_group)]
    plots.append(stacked_graph(df_dict,label_dict,{'radiobutton':radiobutton,'select':dropdown,'hide':checkbox_button_group},title='Stacked'))
    text,table = plot_table(df[columns_name])
    plots.append(text)
    plots.append(table)

    return Panel(child = column(plots),title='Stacked')


def third_panel():

    n = 1000
    t = np.linspace(0,10,n,endpoint=True)
    df = DataFrame(.1*np.random.normal(0,1,(n))+np.cos(2*np.pi*t))
    df.iloc[500:] = np.nan
    for ii in range(9):
        df[str(ii)] = df.iloc[:,0].shift((ii+1)*10)

    df.columns = [str(ii+1) for ii in range(10)]
    
    df['Date'] = t
    columns_name = [xx for xx in list(df.columns) if xx.isnumeric()]
    columns_name.sort()
    df_dict = {'df':ColumnDataSource(df),'Lower Percentile 15Y':np.nanquantile(df[columns_name],0.1),'Upper Percentile 15Y':np.nanquantile(df[columns_name],0.90),
    'Lower Percentile 5Y':np.nanquantile(df[columns_name[-5:]],0.1),'Upper Percentile 5Y':np.nanquantile(df[columns_name[-5:]],0.90)}

    label_dict = {'df':[str(ii+1) for ii in range(10)]}

    radiobutton = RadioButtonGroup(labels = ["Percentiles Last 15 Years", "Percentiles Last 5 Years"], active = 0)
    plots = [row(radiobutton)]
    plots.append(continuation_graph(df_dict,label_dict,{'radiobutton':radiobutton},title='Continuation'))
    plots.append(continuation_graph(df_dict,label_dict,{},title='COT'))
    

    return Panel(child = column(plots),title='Continuation & COT')

def plot_table(df):
    df = df.round(3)
    template = """
    <div style="font-size:11pt";>
    <%= value %></div>
    """
    formatter = HTMLTemplateFormatter(template=template)
    columns = [ TableColumn(field=col, title=col,formatter=formatter) for col in list(df.columns)]
    table = DataTable(source=ColumnDataSource(data=df),columns=columns, width=plot_width)
    string = """<div><b>Correlation: </b></div>"""
    text = Div(text=string, style={'font-size': '120%'}, width=500)
    return text,table



def continuation_graph(df_dict,label_dict,widgets,title=''):


    plot = figure( title= title,
                 x_axis_label = 'Date',
                 plot_width = plot_width,
                 plot_height = plot_height_indicator,
                 min_border_bottom=min_border_bottom_settle,
                 toolbar_location="above",
                 x_axis_location='below',
                 tools = ["pan,box_zoom,zoom_in,zoom_out,wheel_zoom,reset,save"],
                 sizing_mode="fixed"
                 )
    
    source_df = {}
    plot_dict = {}

    for df_item,labels_item in zip(df_dict,label_dict):
        source_df[labels_item] = df_dict[df_item]
        colors = Category20[max(len(label_dict[labels_item]),3)]

        for color,label in zip(colors,label_dict[labels_item]):
            plot_dict[label] = plot.line('Date', label, source=source_df[labels_item], color=color, line_width=3, legend_label=label.title(),name=label.title())

    plot = set_font_n_ticker_size(plot)
    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"
    plot.legend.orientation = "horizontal"

    if len(widgets)>0:

        percentile_limit_lower = Span(location=df_dict['Lower Percentile 15Y'],dimension='width', line_color='firebrick',line_dash='dashed', line_width=3)
        percentile_limit_upper = Span(location=df_dict['Upper Percentile 15Y'],dimension='width', line_color='firebrick',line_dash='dashed', line_width=3)

        percentiles15 = [df_dict['Lower Percentile 15Y'],df_dict['Upper Percentile 15Y']] 
        percentiles05 = [df_dict['Lower Percentile 5Y'],df_dict['Upper Percentile 5Y']] 

        percentiles_span = [percentile_limit_lower,percentile_limit_upper]
        callback_radiobutton = Swap_quantile_continuation(percentiles_span,percentiles05,percentiles15,widgets['radiobutton'])
        widgets['radiobutton'].js_on_click(callback_radiobutton)

        plot.add_layout(percentile_limit_lower)
        plot.add_layout(percentile_limit_upper)
    
    return plot

def stacked_graph(df_dict,label_dict,widgets,title=''):

    plot = figure( title= title,
                 x_axis_label = 'Date',
                 plot_width = plot_width,
                 plot_height = plot_height_settle,
                 min_border_bottom=min_border_bottom_settle,
                 toolbar_location="above",
                 x_axis_location='below',
                 tools = ["pan,box_zoom,zoom_in,zoom_out,wheel_zoom,reset,save"],
                 sizing_mode="fixed"
                 )
    
    source_df = {}
    plot_dict = {}

    for df_item,labels_item in zip(df_dict,label_dict):
        source_df[labels_item] = df_dict[df_item]
        colors = Category20[max(len(label_dict[labels_item]),3)]

        for color,label in zip(colors,label_dict[labels_item]):
            plot_dict[label] = plot.line('Date', label, source=source_df[labels_item], color=color, line_width=3, legend_label=label.title(),name=label.title())

    plot = set_font_n_ticker_size(plot)
    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"
    plot.legend.orientation = "horizontal"

    percentile_limit_lower = Span(location=df_dict['Lower Percentile 15Y'],dimension='width', line_color='firebrick',line_dash='dashed', line_width=3)
    percentile_limit_upper = Span(location=df_dict['Upper Percentile 15Y'],dimension='width', line_color='firebrick',line_dash='dashed', line_width=3)
    
    dictionary = {'Lower Percentile 15Y':df_dict['Lower Percentile 15Y'],'Lower Percentile 5Y':df_dict['Lower Percentile 5Y'],
    'Upper Percentile 15Y':df_dict['Upper Percentile 15Y'],'Upper Percentile 5Y':df_dict['Upper Percentile 5Y']}

    df_dict_copy = df_dict.copy()
    percentiles15 = [df_dict['Lower Percentile 15Y'],df_dict['Upper Percentile 15Y']]
    percentiles05 = [df_dict['Lower Percentile 5Y'],df_dict['Upper Percentile 5Y']]
#Stacked_feature(span_percentiles_stacked,source, source_stacked,plot,title,checkbox_hide, selection_stacked,radio_button_stacked)
    callback_dropdown = Stacked_features([percentile_limit_lower,percentile_limit_upper],df_dict['df'],df_dict_copy['df'],
    percentiles05,percentiles15,label_dict['df'],plot,widgets)
    callback_radiobutton = Swap_quantile_stacked([percentile_limit_lower,percentile_limit_upper],dictionary,widgets['radiobutton'])
    widgets['radiobutton'].js_on_click(callback_radiobutton)
    widgets['select'].js_on_change('value',callback_dropdown)

    plot.add_layout(percentile_limit_lower)
    plot.add_layout(percentile_limit_upper)

    
    return plot

def main_graph(df_dict,label_dict,risk_reward_dict,x_axis=None,title=''):


    plot = figure( title= title,
                 x_axis_label = 'Date',
                 plot_width = plot_width,
                 plot_height = plot_height_indicator,
                 #plot_height = plot_height_settle,
                 min_border_bottom=min_border_bottom_settle,
                 toolbar_location="above",
                 x_axis_location=x_axis,
                 tools = ["pan,box_zoom,zoom_in,zoom_out,wheel_zoom,reset,save"],
                 sizing_mode="fixed"
                 )
    
    plot_dict = {}

    for df_item,labels_item in zip(df_dict,label_dict):
        source_df = df_dict[df_item]
        colors = Category10[max(len(label_dict[labels_item]),3)]

        for color,label in zip(colors,label_dict[labels_item]):
            plot_dict[label] = plot.line('Date', label, source=source_df, color=color, line_width=3, legend_label=label.title(),name=label.title())

    plot = set_font_n_ticker_size(plot)
    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"
    plot_dict["Rolling_Mean"].visible = False
    plot_dict["Upper_Band"].visible = False
    plot_dict["Lower_Band"].visible = False

    limit = risk_reward_dict['Actual'] + risk_reward_dict['Percentiles Positive']['50%']/risk_reward_dict['Unit Move'];
    stop = risk_reward_dict['Actual'] + risk_reward_dict['Percentiles Negative']['1%']/risk_reward_dict['Unit Move'];

    limit_line = Span(location=limit,dimension='width', line_color='green',line_dash='dashed', line_width=3)
    stop_line  = Span(location=stop,dimension='width', line_color='firebrick',line_dash='dashed', line_width=3)
    plot.add_layout(limit_line)
    plot.add_layout(stop_line)
    return {'Main Plot':plot,'Lines':[limit_line,stop_line]}


def oscillators(df_dict,label_dict,widgets,x_axis=None,title=''):


    plot = figure( title= title,
                x_axis_label = 'Date',
                plot_width = plot_width,
                plot_height = plot_height_indicator,
                min_border_bottom=0,
                toolbar_location="above",
                x_axis_location=x_axis,
                sizing_mode="fixed"
                )
    
    plot_dict = {}

    for df_item,labels_item in zip(df_dict,label_dict):
        source_df = df_dict[df_item]#ColumnDataSource(df_dict[df_item])
        colors = Category10[max(len(label_dict[labels_item]),3)]

        for color,label in zip(colors,label_dict[labels_item]):
            plot_dict[label] = plot.line('Date', label, source=source_df, color=color, line_width=3, legend_label=label.title().replace("_"," "),name=label.title())

    callback_rsi= oscillator_callback(df_dict['df'], widgets,label_dict['df'],{"Spread":"Spread"})
    widgets['Slider'].js_on_change('value', callback_rsi)
    widgets['Select'].js_on_change('value', callback_rsi)

    plot = set_font_n_ticker_size(plot)
    plot.legend.click_policy = "hide"
    plot.legend.location = "top_left"
    plot.toolbar_location = None
    plot.toolbar.logo = None

    
    return plot



def barchart(df_dict,label_dict,dictionary):

    plot = figure( title= dictionary['title'],
                x_axis_label = 'Date',
                plot_width = plot_width,
                plot_height = plot_height_indicator,
                min_border_bottom=min_border_bottom_settle,
                toolbar_location="above",
                x_axis_location=dictionary['x_axis'],
                sizing_mode="fixed"
                )
    
    plot_dict = {}

    plot.min_border_top = 50
    for df_item,labels_item in zip(df_dict,label_dict):
        source_df = df_dict[df_item]
        colors = Category10[max(len(label_dict[labels_item]),3)]

        for color,label in zip(colors,label_dict[labels_item]):
            plot_dict[label] = plot.quad(top=label,bottom=0, left='Left', right='Right',source=source_df,color=color, alpha=0.8, legend_label=label.title())

    plot = set_font_n_ticker_size(plot)
    plot.legend.click_policy = "hide"
    plot.legend.location = "top_left"
    plot.toolbar_location = None
    plot.toolbar.logo = None
    liquid_limit = Span(location=.5,dimension='width', line_color='firebrick',line_dash='dashed', line_width=3)

    plot.add_layout(liquid_limit)

    
    return plot


def barchart_with_sign(df_dict,label_dict,widgets,dictionary,main_plot=None):

            plot = figure(
              title = dictionary['title'],
              plot_width = plot_width//2,
              sizing_mode='scale_width',
              x_range=dictionary['x_axis'],
              plot_height = plot_height_indicator,
              min_border_left=min_border_left,
              min_border_top=min_border_top_rsi,
              toolbar_location=None#'below',

          )

            
            plot_dict = {}
            average   = {}
            radius    = 1.0e-12

            colors = ["#718dbf","#e84d60"]
            colors_mean = ['green','red']
            labels = ['Mean Gain','Mean Loss']
            span_average = {}
            for df_item,labels_item,color,color_mean,label in zip(df_dict,label_dict,colors,colors_mean,labels):
                #df_temp = df_dict[df_item]
                source_df = df_dict[df_item]
                #df_temp.dropna(inplace=True)
                #source_df = ColumnDataSource(df_temp)

                if dictionary[' '.join([df_item,'Size'])]>0:
                    plot_dict[labels_item] = plot.vbar(x='Year',top=labels_item,width=0.4,source=source_df,color=color, alpha=0.8)
                    average[labels_item] = dictionary[' '.join([df_item,'Mean'])]
                    plot.circle(x=dictionary['x_axis'][0], y=average[labels_item], radius=radius, color=color_mean, legend_label=label)
                    span_average[df_item] = Span(location=average[labels_item], dimension='width', line_color=color_mean, line_dash='dashed',line_width=2)
                    plot.add_layout(span_average[df_item])
            plot = set_font_n_ticker_size(plot)

            if len(widgets)>0:
                #for df_item in label_dict:
                #    print(dictionary[" ".join(['Percentiles',df_item])])
                #callback_risk_reward = risk_reward_feature(plot,span_average_gain, span_average_loss, reward, risk,
                #list_selection_reward, list_selection_risk, unit_move,-np.cos(np.pi*uptrend), widgets['Price'], widgets['Reward'], widgets['Risk'])

                callback_risk_reward = risk_reward(dictionary, widgets,plot,main_plot)
                widgets['Reward'].js_on_change('value', callback_risk_reward)
                widgets['Risk'].js_on_change('value', callback_risk_reward)
                widgets['Price'].js_on_change('value', callback_risk_reward)


            plot.legend.location = "top_left"
            plot.legend.orientation = "horizontal"

            #plot.yaxis[0].formatter = NumeralTickFormatter(format=spread.get_currency_unit() + " 0.")
            return plot



def plot_histogram(df_dict,label_dict,actual_price,x_axis=None,title=''):

    plot = figure( title= title,
                x_axis_label = 'Price',
                y_axis_label = 'Pr(x)',
                plot_width = plot_width,
                plot_height = plot_height_indicator,
                min_border_bottom=min_border_bottom_settle,
                toolbar_location="above",
                x_axis_location=x_axis,
                sizing_mode="fixed"
                )
    
    plot_dict = {}
    color_actual = 'green'
    radius    = 1.0e-12
    plot.min_border_top = 50
    colors = Category10[3]
    for df_item,labels_item,color in zip(df_dict,label_dict,colors):
        source_df = ColumnDataSource(df_dict[df_item])
        for label in label_dict[labels_item]:
            plot_dict[label] = plot.quad(top=label,bottom=0, left='Left', right='Right',source=source_df,color=color, alpha=0.8, legend_label=label.title())


    plot.circle(x=actual_price, y=0, radius=radius, color=color_actual, legend_label='Actual Price')
    plot = set_font_n_ticker_size(plot)
    plot.legend.click_policy = "hide"
    plot.legend.location = "top_left"
    plot.toolbar_location = None
    plot.toolbar.logo = None
    actual = Span(location=actual_price,dimension='height', line_color=color_actual,line_dash='dashed', line_width=3,)

    plot.add_layout(actual)

    
    return plot