/** @jsx React.DOM */

var CheckboxMixin = {
    handleCheck: function(event){
        this.setState({checked: event.target.checked});
        if(this.hasOwnProperty('toggleCheckRows')){
            this.toggleCheckRows();
        }
    }
};

var GoToBundleMixin = {
    capture_keys: function(e){
         Mousetrap.bind(['enter'], function(e){
            this.goToBundlePage();
        }.bind(this), 'keydown');
    },
    goToBundlePage: function(){
        var bundleUUID = this.props.item.state.bundle_info.uuid;
        window.open('/bundles/' + bundleUUID, '_blank');
    },
};

