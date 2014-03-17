var utils = {

    flashMessage : function(message, theme){
        $.jGrowl(
            message,
            { theme: theme, position: "bottom-right" }
        );
    },

    validateForm : function(form_id){
    	var form = "form";
    	if (form_id){
    		if (form_id.indexOf("#") == -1)
    			form = "#" + form_id;
    		else
    			form = form_id
    	}

    	$(form).on('submit', function(event){
            var fail = false;
            $("input", event.currentTarget).each(function(){
                if ($(this).val() == ""){
                    $(this).parents(".form-group").addClass("has-error");
                    fail = true;
                }
                else{
                    $(this).parents(".form-group").removeClass("has-error");
                }
            });
            if (fail){
            	utils.flashMessage("Some inputs have been left blank!", "error");
            	return false;
            }
        });
    }
}