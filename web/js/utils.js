var utils = {

    checkPin: function(pin, identificator, callback){
        var fail = true;
        if (identificator && identificator != ""){
            fail = false
            $.ajax({
                url: "/check_pin/" + identificator + "/" + pin + "/",
                dataType: "json",
                success: function(data){
                    $("#pin-modal .modal-body .list").empty();
                    if (Object.keys(data).length > 0){
                        for (var key in data) {
                            $("<div/>", {"style": "font-size: 1.2em; font-weight: bold;"}).html(data[key]).appendTo("#pin-modal .modal-body .list");
                        }
                        $("#pin-modal").modal('show');
                        fail = true;
                    }
                    else{
                        if (callback != null){
                            callback();
                        }
                    }
                }
            });
        }
        return fail;
    },

    flashMessage : function(message, options){
        //options.life = 3500;
        options = JSON.parse(options);

        options.position = "bottom-right";

        $.jGrowl(
            message,
            options
        );
    },

    validateForm : function(form_id, ignoreList){
    	var form = "form";
    	if (form_id){
    		if (form_id.indexOf("#") == -1)
    			form = "#" + form_id;
    		else
    			form = form_id
    	}
        $(form).on('submit', function(event){
            var fail = false;
            $("input:not(:disabled)", event.currentTarget).each(function(){
                if(ignoreList != undefined){
                    if ($.inArray($(this).attr('name'), ignoreList) == -1){
                        if ($(this).val() == ""){
                            $(this).parents(".form-group").addClass("has-error");
                            fail = true;
                        }
                        else{
                            $(this).parents(".form-group").removeClass("has-error");
                        }
                    }
                }
            });
            if (fail){
            	utils.flashMessage("Some inputs have been left blank!", '{ "theme" : "error" }');
            	return false;
            }
        });
    },

    checkIdentificator: function(identificator){
        var exists = false;
        $.ajax({
            url: "/sensors/check_identificator/",
            async: false,
            type: "POST",
            data: { identificator : identificator },
            dataType : "json"
        })
        .done(function(data){
            if (data['exists'] == true){
                utils.flashMessage("Sensor with same identificator exists!", '{ "theme" : "error" }');
                exists = true;
            }
        });

        return !exists;

    }
}


var delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();