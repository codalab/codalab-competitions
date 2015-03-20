// Lightweight global event binding system
ws_broker = {};
ws_broker.fire = function(name, e){
    if(!ws_broker[name]){
        return false;
    }
    for(var i = 0; i < ws_broker[name].length; i++){
        ws_broker[name][i](e);
    }
};
ws_broker.register = function(name, f){
    if(name == "fire" || name == "register"){
        console.error("Cannot register event with reserved name \"" + name + "\"");
        return false;
    }
    ws_broker[name] = ws_broker[name] || [];
    ws_broker[name].push(f);
};
ws_broker.unregister = function(name){
    if(ws_broker.hasOwnProperty(name)){
        delete ws_broker[name];
    }else {
        return false;
    }
};