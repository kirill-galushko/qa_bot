(function(global) { 
    
    function init() {

        setupEvents();

        visualizeView($('script[src*="/static/js/app.js"]').attr('inner_json'));


    }


    function setupEvents() {

        $('#visualizeButton').click(visualizeView);
        $('#sendButton').click(sendToServer);
    
    }

    function sendToServer() {
        socket.emit('receive answer', JSV.callback);
    }

    function resetToolbar() {
        $('#app-toolbar button').attr("class", "btn btn-default");
    }
    
    function visualizeView(this_script) {
        
        var schema = {};
        try {
            schema = JSON.parse(this_script);
        } catch (e) {
            alert(e.toString());
            return;
        }
        
        NProgress.start();
        
        resetToolbar();
        
        $('#visualizeButton').attr("class", "btn btn-primary active");
        
        $('#editor').css('display', 'none');
        
        $('#main-body').empty();
        
        $RefParser.dereference(schema).then(function(resolvedSchema) {
              //Prevent circular references.
              resolvedSchema = JSON.parse(stringify(resolvedSchema));
              JSV.init({
                plain: true,
                schema: resolvedSchema,
                viewerHeight: $('#main-body').height(),
                viewerWidth: $('#main-body').width(),
                callback: ''
            }, function() {
                $('#jsv-tree').css('width', '100%');
                JSV.resizeViewer();
            });
            NProgress.done();
        }).catch(function(err) {
            alert(err);
            NProgress.done();
        });
        
    }
    
    /* json-stringify-safe*/
    function stringify(obj, replacer, spaces, cycleReplacer) {
  return JSON.stringify(obj, serializer(replacer, cycleReplacer), spaces)
}

    function serializer(replacer, cycleReplacer) {
  var stack = [], keys = []

  if (cycleReplacer == null) cycleReplacer = function(key, value) {
    if (stack[0] === value) return "[Circular ~]"
    return "[Circular ~." + keys.slice(0, stack.indexOf(value)).join(".") + "]"
  }

  return function(key, value) {
    if (stack.length > 0) {
      var thisPos = stack.indexOf(this)
      ~thisPos ? stack.splice(thisPos + 1) : stack.push(this)
      ~thisPos ? keys.splice(thisPos, Infinity, key) : keys.push(key)
      if (~stack.indexOf(value)) value = cycleReplacer.call(this, key, value)
    }
    else stack.push(value)

    return replacer == null ? value : replacer.call(this, key, value)
  }
}

    var socket = io.connect('http://localhost:' + location.port + '/socket');
    socket.on('update json', function(json_obj) {
        visualizeView(json_obj);
    });

    $(init);
    
})(window);
