import json

import numpy as np
import pandas as pd

try:
    # prefer Jupyter (i.e. IPyhton 4.x)
    from traitlets import (
        Instance,
        Unicode,
    )    
    from ipywidgets import widgets
except ImportError:
    from IPython.utils.traitlets import (
        Instance,
        Unicode,
    )
    from IPython.html import widgets # Widget definitions

from IPython.display import display # Used to display widgets in the notebook
from IPython.display import Javascript # Used to insert javascript in the notebook


# Thank you to thoses to shared their code online

# Originally from http://nbviewer.ipython.org/gist/rossant/9463955
SCRIPT = """
            requirejs.undef("handsontable_view");
            console.log("handsontablejs requirejs module loaded...")
            define(
            "handsontable_view",
            [
                "jquery",
                "underscore",
                "widgets/js/widget",
                "base/js/namespace",

                // this silently upgrades jquery
                "https://cdn.jsdelivr.net/handsontable/0.20.2/handsontable.full.min.js"
            ],
            function($, _, widget, IPython){
                "use strict";
                console.log("was required");
                // Define the HandsonTableView
                var HandsonTableView = widget.DOMWidgetView.extend({
                    render: function(){           
                        _.bindAll(this, "update", "resizeHolder", "afterChange"); 
                        this.initStyle();
                        _.delay(this.update, 300);

                        //this.resizeHolder();
                    },

                    initStyle: function(){
                        var styleUrl = "https://cdn.jsdelivr.net/handsontable/0.20.2/handsontable.full.min.css";

                        if(!$('link[href="' + styleUrl + '"]').length){
                            $("<link/>", {href: styleUrl, rel: "stylesheet"})
                                .appendTo($("head"));
                        }
                    },

                    resizeHolder : function(){
                        // TODO: kill with fire
                        this.$el.find(".wtHolder")
                            .css({width: "", height: ""});
                        if(this.model.comm_live){
                            setTimeout(this.resizeHolder, 1000);
                        }
                    },

                    ensureTable: function(){
                        if(this.ht){
                            return;
                        }

                        this.ht = new Handsontable(this.$el[0], {
                            height: 300,
                            stretchH: 'all'
                        });

                        $(this.$el).width('100%');

                        this.ht.addHook("afterRender", this.afterChange);
                        IPython.keyboard_manager.register_events(this.$el);
                    },

                    update: function() {
                        this.ensureTable();
                        var value = this.model.get("value");
                        this.ht.updateSettings({
                            colHeaders: value.columns,
                            rowHeaders: value.index,
                            contextMenu: true,
                        })
                        this.ht.loadData(value.data);

                        console.log("was updated");
                    },

                    afterChange: function(event) {
                        var data = this.ht.getData(),
                            oldValue = this.model.get("value"),
                            newValue = {
                                columns: this.ht.getColHeader(),
                                index: this.ht.getRowHeader(),
                                data: data
                            };

                        if(true || !_.isEqual(oldValue, newValue)){
                            console.log("changed from client", newValue);
                            this.model.set({value: newValue});
                            this.touch();
                        }
                    },
                });

                return {
                    HandsonTableView: HandsonTableView
                };
            });"""

Javascript(SCRIPT)

# the following stolen from https://github.com/bloomberg/bqplot/blob/2ab2335d56d8c099398c70114920e6ab01a2cbf7/bqplot/traits.py#L202

class PandasDataFrame(Instance):
    """A pandas Dataframe trait type.
    The json representation is an array of dicts which is amenable for
    consumption by JavaScript. also note that index name is ignored and when
    deserializing will use the 'index' attribute as an index for the df. This
    means if the data frame cannot have a column called 'index'.
    """
    klass = pd.DataFrame
    info_text = 'a pandas DataFrame'
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('from_json', self._from_json)
        kwargs.setdefault('to_json', self._to_json)
        kwargs.setdefault('args', ())
        super(PandasDataFrame, self).__init__(*args, **kwargs)

    def _from_json(self, value, obj=None):
        if value is not None:
            df = pd.read_json(json.dumps(value), orient="split")
        else:
            df = pd.DataFrame()
        return df

    def _to_json(self, df, obj=None):
        if df is not None:
            return json.loads(df.to_json(orient='split'))
        else:
            return {"columns": [], "index": [], "data": []}

    def validate(self, obj, value):
        value = super(PandasDataFrame, self).validate(obj, value)
        if self.get_metadata('lexsort'):
            if isinstance(value.columns, pd.MultiIndex):
                value = value.sortlevel(0, axis=1)
        return value
    
    _cast = _from_json

    
class HandsonTable(widgets.DOMWidget):
    _view_module = Unicode('handsontable_view', sync=True)
    _view_name = Unicode('HandsonTableView', sync=True)
    value = PandasDataFrame(sync=True)