/** @jsx React.DOM */

var CheckboxMixin = {
    handleCheck: function(event){
        this.setState({checked: event.target.checked});
        if(this.hasOwnProperty('toggleCheckRows')){
            this.toggleCheckRows();
        }
    }
};
