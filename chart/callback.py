from bokeh.models import CustomJS

def oscillator_callback(source,widgets,label_dict,dictionary):

    code = """
                            var data     = source.data;
                                                        
                            let   frequency= widgets['Slider'].value;
                            let   type = widgets['Select'].value;
                            const z    = data[dictionary['Spread']];
                            const N    = z.length;
                            
                            var u        = new Array(N).fill(0);
                            var v        = new Array(N).fill(0);
                            var y        = data[label_dict[0]];
                            if (type==='RSI')
                            {
                ////### RSI

                                u[0] = NaN;
                                v[0] = NaN;

                                for (let i=1;i<N;i++){
                                        let tmp  = z[i]-z[i-1];

                                        if (tmp>0){
                                                    u[i] = tmp;
                                                    
                                        } else if (tmp<0){
                                                    v[i] = Math.abs(tmp);}
                                }
                                
                                var tmpU = u[1];
                                var tmpV = v[1];       
                                y[0]        = NaN;
                                y[1]        = 100*(tmpU/(tmpU+tmpV));

                                
                                let alpha = 1.0 / frequency;
                                
                ////            Esponential Mean
                
                                let beta  = 1.0-alpha;
                
                                for (let i=2;i<N;i++)
                                {
                                    tmpU = alpha*u[i] + beta*tmpU;
                                    tmpV = alpha*v[i] + beta*tmpV;        
                                    
                                    y[i]  = 100*(tmpU/(tmpU+tmpV));
                                    
                                    if (tmpU===NaN){
                                                tmpU = u[i];
                                    } 
                                    if (tmpV===NaN){
                                                tmpV = v[i];
                                    } 
                                    
                                }
                        }

                        else if (type==='Stochastic')
                        {
                            // Stochastic
                            const smooth = 3;
                            for (let i=frequency-1;i<N;i++){
                                    var max_el = z[i];
                                    var min_el = z[i];

                                    for (let j=1;j<frequency;j++)
                                    {
                                        min_el = Math.min(min_el,z[i-j]);
                                        max_el = Math.max(max_el,z[i-j]);
                                    }

                                    y[i] = 100*(z[i]-min_el)/(max_el-min_el);

                            }

                            for (let i=frequency+smooth-1;i<N;i++){
                                let mean_value = 0;
                                for (let j=0;j<smooth;j++)
                                {
                                    mean_value = mean_value + y[i-j];
                                }

                                mean_value /= smooth;
                                u[i] = mean_value;
                            }

                            for (let j=0; j<frequency+smooth-1;j++){
                                u[j] =NaN;
                            }

                            for (let i=0;i<N;i++){
                                y[i] = u[i];
                            }

                        }
                


                        const sigma = 2;
                        const f     = 20;

                        //const uband_name = [type,"Upper_Band"].join("_");
                        //const lband_name = [type,"Lower_Band"].join("_");
                        //const rmean_name = [type,"Rolling_Mean"].join("_");

                        var rmean_rsi = data[label_dict[1]];
                        var uband_rsi = data[label_dict[2]];
                        var lband_rsi = data[label_dict[3]];

                        for (var i=f-1;i<N;i++)
                        {
                            var mean=0;
                            var std =0;
                            
                            for (var j=0;j<f;j++)
                            {
                                    mean += y[i-j];
                                    std  += Math.pow(y[i-j],2);
                            } 
                            mean/= f ;
                            std  = sigma*Math.sqrt( ( std/(f) - Math.pow(mean,2) ) );
                            
                            rmean_rsi[i] = mean;
                            lband_rsi[i] = rmean_rsi[i] - std;
                            uband_rsi[i] = rmean_rsi[i] + std;

                        }
                            
                        for (var j=0; j<f-1;j++){
                                rmean_rsi[j] =NaN;
                                lband_rsi[j] =NaN;
                                uband_rsi[j] =NaN;
                                }


                        source.change.emit();            """

    return CustomJS(args=dict(source=source,widgets=widgets,label_dict=label_dict,dictionary=dictionary), code=code)



def Swap_quantile_stacked(span_percentiles_stacked,dict_percentiles,radio_button_stacked):

    code = """
                                
                var f = radio_button.active;
                
                for (var i = 0; i < span.length; ++i) {
                            span[i].location = NaN;
                        }
                const percentiles15 = [dict_percentiles["Lower Percentile 15Y"],dict_percentiles["Upper Percentile 15Y"]];
                const percentiles5 = [dict_percentiles["Lower Percentile 5Y"],dict_percentiles["Upper Percentile 5Y"]];

                if (f === 0){
                    for (var i = 0; i < span.length; ++i) {
                        span[i].location = percentiles15[i];
                    }
                    
                }
                else if (f === 1){
                    for (var i = 0; i < span.length; ++i) {
                        span[i].location = percentiles5[i];
                    }
                    
                }       
                
                """

    return CustomJS(args=dict(span=span_percentiles_stacked,dict_percentiles=dict_percentiles,radio_button=radio_button_stacked), code=code)


def Swap_quantile_continuation(percentiles_span,perc5,perc15, radio_button_continuation):

    code = """

                                var f = radio_button.active;
                                
                                if (f === 0){
                                    for (var i = 0; i < span.length; ++i) {
                                        span[i].location = percentiles15[i];
                                    }
                                    
                                }
                                else if (f === 1){
                                
                                    for (var i = 0; i < span.length; ++i) {
                                        span[i].location = percentiles5[i];
                                    }
                                    
                                }
                                         
                                """

    return CustomJS(args=dict(span=percentiles_span,percentiles5=perc5,percentiles15=perc15,radio_button=radio_button_continuation), code=code)



def Bollinger_band_lags(source_df,slider_window,dictionary):

    code =  """
                var data = source.data;
                var y = data[dictionary['Upper_Band']];
                var w = data[dictionary['Lower_Band']];
                var u = data[dictionary['Rolling_Mean']];

                const sigma = 2;
                const f     = window.value;
                const z     = data[dictionary['Spread']];
                const N     = z.length;

                for (var i=f-1;i<N;i++)
                {
                     var mean=0;
                     var std =0;
                     
                     for (var j=0;j<f;j++)
                     {
                             mean += z[i-j];
                             std  += Math.pow(z[i-j],2);
                     } 
                     mean/= f ;
                     std  = sigma*Math.sqrt( ( std/(f) - Math.pow(mean,2) ) );
                     
                     u[i] = mean;
                     w[i] = u[i] - std;
                     y[i] = u[i] + std;
                }
                     
                for (var j=0; j<f-1;j++){
                        u[j] =NaN;
                        y[j] =NaN;
                        w[j] =NaN;}

                source.change.emit();            
                """ 
    return CustomJS(args=dict(source=source_df,window=slider_window,dictionary = dictionary), code=code)



def Stacked_features(span_percentiles_stacked,source,source_stacked,percentiles05,percentiles15,list_columns,plot,widgets):
    
    
    code = """

                    var data            = source.data;
                    const data_stacked  = source_stacked.data;
                    const check_feature = widgets['select'].value;
                    const perc_type     = widgets['radiobutton'].active;
                    const hide_flag     = widgets['hide'].active[0];
                    const columns     = list_columns;

                    //var ii_title= 0;
                    var feature = "Spread";
                    var ylabel  = "Unit Move";
                    
                    for (var i = 0; i < span_element.length; ++i) {
                                span_element[i].location  = NaN;
                    }
                    
                     
                    for (var key in columns){

                        let new_col = [check_feature,columns[key]].join(" ");
                        if (check_feature === "Stacked")
                        {
                            if (perc_type===0){
                                for (var i = 0; i < span_element.length; ++i) {
                                    span_element[i].location  = percentiles15[i];
                                }
                            }
                            else if(perc_type===1){
                                for (var i = 0; i < span_element.length; ++i) {
                                            span_element[i].location  = percentiles05[i];
                                }
                            }
                        }

                        console.log(new_col);
                        console.log(columns[key]);
                        for (var i = 0; i < data["Date"].length; ++i) {
                            data[columns[key]][i] = data_stacked[new_col][i];
                        }
                    }
                    

                    //for (var key in line_stacked){
                    //    line_stacked[key].visible=(hide_flag===0);
                    //}
                    
                    //plot_data.title.text = title[ii_title];
                    plot_data.left.axis_label = ylabel;
                    source.change.emit();
                    plot_data.change.emit();
                                                        """
    
    return CustomJS(args=dict(span_element=span_percentiles_stacked,source=source,source_stacked= source_stacked,
    percentiles05=percentiles05,percentiles15=percentiles15,list_columns=list_columns,plot_data=plot,widgets=widgets), code=code)


def risk_reward(dictionary,widgets,plot,main_plot):
    code = """      
                    Number.prototype.countDecimals = function () {
                    if(Math.floor(this.valueOf()) === this.valueOf()) return 0;
                    return this.toString().split(".")[1].length || 0; 
                    }

                    const price = Number(widgets['Price'].value);
                    const risk  = widgets['Risk'].value;
                    const reward  = widgets['Reward'].value;
                    const unit_move = dictionary['Unit Move'];
                    const position = dictionary['Position'];
                    const p_neg = dictionary['Percentiles Negative'];
                    const p_pos = dictionary['Percentiles Positive'];
                    var countDecimals = function (value) {
                        if(Math.floor(value) === value) return 0;
                        return value.toString().split(".")[1].length || 0; 
                    }

                    const ndecimals = price.countDecimals();

                    const estimatied_risk   = p_neg[risk];
                    const estimatied_reward = p_pos[reward];

                    const stop   = price+estimatied_risk/unit_move;
                    const limit = price+estimatied_reward/unit_move;
                    
                    main_plot[0].location = limit;
                    main_plot[1].location = stop;

                    var ratio = Math.abs(estimatied_risk/estimatied_reward);
                    var title = "Best & Worst | Risk: ";
                    title = title.concat(Math.round(estimatied_risk,1).toString(), " $ | Reward: ",Math.round(estimatied_reward,1).toString());
                    title = title.concat(" $ | Ratio: ",ratio.toFixed(2).toString()," | Stop Loss: ",stop.toFixed(ndecimals).toString()," |  Limit: ", limit.toFixed(ndecimals).toString() );
                    plot.title.text = title;
                    plot.change.emit();  
                    """

    return CustomJS(args=dict(dictionary=dictionary,widgets=widgets,plot=plot,main_plot=main_plot), code=code)