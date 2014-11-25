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
    keysToHandle: function(){
        return['enter'];
    },
    handleKeydown: function(e){
        var key = keyMap[event.keyCode];
        if(typeof key !== 'undefined'){
            event.preventDefault();
            switch (key) {
                case 'enter': // go to highlighted bundle's detail page
                    event.preventDefault();
                    this.goToBundlePage();
            }
        }
    },
    goToBundlePage: function(){
        var bundleUUID = this.props.item.state.bundle_info.uuid;
        window.open('/bundles/' + bundleUUID, '_blank');
    },
}
