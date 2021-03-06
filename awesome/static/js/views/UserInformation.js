App.Backbone.View.UserInformation = Backbone.View.extend({
    tagName: "div",
    sel: {
        SET_DESCRIPTION: "#SetUserDescriptionContainer",
        INPUT : "#UserDescriptionInput",
        SUBMIT : "#UserDescriptionSubmit",
        LENGTH: "#UserDescriptionLength",
        DESCRIPTION : "#UserDescription",
        NO_DESCRIPTION : "#NoUserDescription",
        FOLLOW_BUTTON: ".FollowButton",
        SHOW_FOLLOWS: ".Follows",
        SHOW_FOLLOWERS: ".Followers",

        SET_PICTURE_SWITCH: "#SetProfilePictureSwitch",
        SET_PICTURE_FORM: "#SetProfilePictureForm",
        SET_PICTURE_INPUT: "#PictureUploadInput",
        SET_PICTURE_SUBMIT: "#PictureUploadSubmit",
    },
    constant: {
        MAX_USER_DESCRIPTION_LENGTH : 200,

        DEFAULT_PROFILE_PICTURE: "https://s3.amazonaws.com/project-awesome-img/img/default-profile-picture.jpg",
    },
    initialize: function() {
        _.bindAll(this, "countDesc", "onMouseEnter", "onMouseLeave", "onClick",
                        "submitDesc", "setUserDescription",
                        "followButtonClick",
                        "showUserFollows", "showUserFollowers",
                        "toggleSetProfileForm", "pictureChange");
        this.model.bind("change", this.render, this);
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
        _events["click " + this.sel.FOLLOW_BUTTON] = "followButtonClick";
        _events["click " + this.sel.SHOW_FOLLOWS] = "showUserFollows";
        _events["click " + this.sel.SHOW_FOLLOWERS] = "showUserFollowers";

        _events["click " + this.sel.SET_PICTURE_SWITCH] = "toggleSetProfileForm";
        _events["change " + this.sel.SET_PICTURE_INPUT] = "pictureChange";
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
        var followButtonColor = "btn-primary";
        var followButtonVisibility = "Hidden";
        var followButtonText = "Follow";
        if (this.model.follow() != null &&
            this.model.userId() != USER.id) {
            followButtonVisibility = "";

            if (this.model.follow() == true) {
                followButtonText ="Unfollow";
                followButtonColor = "";
            }
        }

        var setProfilePictureVisibility = "Hidden";
        if (this.model.picture() == this.constant.DEFAULT_PROFILE_PICTURE &&
            App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.loggedInUserId() == App.Var.Model.currentUserId()) {
            setProfilePictureVisibility = "";
        }

        var variables = { 
            name: this.model.fullName(),
            desc: desc,
            descDisplay: descDisplay,
            noDescDisplay: noDescDisplay,
            picture: this.model.picture(),
            followCount: this.model.followCount(),
            followerCount: this.model.followerCount(),
            followButtonVisibility: followButtonVisibility,
            followButtonText: followButtonText,
            followButtonColor: followButtonColor,
            setProfilePictureVisibility: setProfilePictureVisibility,
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
    followButtonClick: function() {
        var follow = this.model.follow();
        if (follow != null) {
            if (follow == true) {
                this.model.unfollowUser();
            } else {
                this.model.followUser();
            }
        }
    },
    showUserFollows: function() {
        App.Var.View.showUserList(App.Const.UserList.FOLLOWS,
                                  this.model.userId());
    },
    showUserFollowers: function() {
        App.Var.View.showUserList(App.Const.UserList.FOLLOWERS,
                                  this.model.userId());
    },
    toggleSetProfileForm: function() {
        var form = $(this.el).find(this.sel.SET_PICTURE_FORM);
        if (form.is(':visible')) {
            $(this.el).find(this.sel.SET_PICTURE_FORM).hide("fast");
        } else {
            $(this.el).find(this.sel.SET_PICTURE_FORM).show("fast");
        }
    },
    pictureChange: function() {
        var filename = $(this.el).find(this.sel.SET_PICTURE_INPUT).val();
        if (filename != "") {
            $(this.el).find(this.sel.SET_PICTURE_SUBMIT).removeAttr("disabled");
        } else {
            $(this.el).find(this.sel.SET_PICTURE_SUBMIT).attr("disabled",
                                                              "disabled");
        }
    },
});

