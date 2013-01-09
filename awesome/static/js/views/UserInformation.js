App.Backbone.View.UserInformation = Backbone.View.extend({
    tagName: "div",
    sel: {
        SET_DESCRIPTION: "#SetUserDescriptionContainer",
        INPUT : "#UserDescriptionInput",
        SUBMIT : "#UserDescriptionSubmit",
        LENGTH: "#UserDescriptionLength",
        DESCRIPTION : "#UserDescription",
        NO_DESCRIPTION : "#NoUserDescription",
    },
    constant: {
        MAX_USER_DESCRIPTION_LENGTH : 200,
    },
    initialize: function() {
        _.bindAll(this, "countDesc", "onMouseEnter", "onMouseLeave", "onClick",
                        "submitDesc", "setUserDescription");
        this.render();
    },
    events: function() {
        var _events = {};
        _events["mouseenter " + this.sel.NO_DESCRIPTION] = "onMouseEnter";
        _events["mouseleave " + this.sel.NO_DESCRIPTION] = "onMouseLeave";
        _events["click " + this.sel.NO_DESCRIPTION] = "onClick";
        _events["keyup " + this.sel.INPUT] = "countDesc";
        _events["cut " + this.sel.INPUT] = "countDesc";
        _events["paste " + this.sel.INPUT] = "countDesc";
        _events["click " + this.sel.SUBMIT] = "submitDesc";
        return _events;
    },
    render: function() {
        var desc = linkify(this.model.description());
        var descDisplay = "";
        var noDescDisplay = "hide";
        if (desc == "" && this.model.userId() == USER.id) {
            descDisplay = "hide";
            noDescDisplay = "";
        }

        var variables = { 
            name: this.model.fullName(),
            desc: desc,
            descDisplay: descDisplay,
            noDescDisplay: noDescDisplay,
            picture: this.model.picture(),
        };
        var template = _.template($("#UserInformationTemplate").html(),
                                  variables);
        $(this.el).html(template);

        return this;
    },
    onMouseEnter: function() {
        $(this.el).find(this.sel.NO_DESCRIPTION).removeClass("NoUserDescriptionNotActive");
        $(this.el).find(this.sel.NO_DESCRIPTION).addClass("NoUserDescriptionActive");
    },
    onMouseLeave: function() {
        $(this.el).find(this.sel.NO_DESCRIPTION).removeClass("NoUserDescriptionActive");
        $(this.el).find(this.sel.NO_DESCRIPTION).addClass("NoUserDescriptionNotActive");
    },
    onClick: function() {
        $(this.el).find(this.sel.NO_DESCRIPTION).hide();
        $(this.el).find(this.sel.SET_DESCRIPTION).show();
        $(this.el).find(this.sel.INPUT).text("").focus();
        this.countDesc();
    },
    countDesc: function() {
        var desc = $.trim($(this.el).find(this.sel.INPUT).val());
        var left = this.constant.MAX_USER_DESCRIPTION_LENGTH - desc.length;

        if (left >= 0) {
            $(this.el).find(this.sel.SUBMIT).removeAttr("disabled");
        } else {
            $(this.el).find(this.sel.SUBMIT).attr("disabled", "disabled");
        }
        $(this.el).find(this.sel.LENGTH).html(left);
    },
    submitDesc: function() {
        if (DEBUG) console.log("SUBMIT DESC");
        var desc = $.trim($(this.sel.INPUT).val());
        doAjax("/api/user/" + USER['id'] + "/set_description",
                JSON.stringify({'description' : desc }),
                // success
                this.setUserDescription,
                // error
                function(jqXHR, textStatus, errorThrown) {
                    console.log("Error");
                }
        );
    },
    setUserDescription: function(data, textStatus, jqXHR) {
        var description = data.description;
        if (description.length > 0 &&
            App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.loggedInUserId() == App.Var.Model.currentUserId()) {
            $(this.el).find(this.sel.NO_DESCRIPTION).hide();
            $(this.el).find(this.sel.SET_DESCRIPTION).hide();
            $(this.el).find(this.sel.DESCRIPTION).html(description).show();
        }
    },
});

