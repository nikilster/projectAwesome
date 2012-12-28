App.Backbone.View.VisionDetailsRepostUser = Backbone.View.extend({
    tagName: "div",
    className: "VisionDetailsRepostUser",
    initialize: function() {
        this.urlTarget = this.options.urlTarget;
        this.render();
    },
    render: function() {
        var variables = { name : this.model.fullName(),
                          userId: this.model.userId(),
                          picture: this.model.picture(),
                          target: this.urlTarget };
        var template = _.template($("#VisionDetailsRepostUserTemplate").html(),
                                  variables);
        $(this.el).html(template);

        return this;
    },
});

App.Backbone.View.VisionDetails = Backbone.View.extend({
    tagName: "div",
    sel: {
        COMMENTS_CONTAINER : "#VisionDetailsCommentsContainer",
        REPOST_USERS_CONTAINER: "#VisionDetailsRepostUsersContainer",
        REPOST_USERS: "#VisionDetailsRepostUsers",
        ADD_COMMENT : "#VisionDetailsAddComment",
        TEXT_CONTAINER : "#VisionDetailsTextContainer",
        EDIT_TEXT : "#VisionDetailsEditText",
        EDIT_FORM : "#VisionDetailsEditForm",
        TEXT : "#VisionDetailsText",
        MODAL_BOX : "#VisionDetailsModalBox",
        CLOSE : "#VisionDetailsClose",
        TEXT_INPUT : "#VisionDetailsTextInput",
        PRIVACY_INPUT : "#VisionDetailsPrivacyInput",
        EDIT_SUBMIT : "#VisionDetailsEditSubmit",
        DELETE_BUTTON : "#VisionDeleteButton",
    },
    initialize: function() {
        _.bindAll(this, "toggleEditSubmit",
                        "ajaxCommentsSuccess",
                        "ajaxCommentsError",
                        "renderComments",
                        "renderComment",
                        "editSubmit",
                        "ajaxEditSuccess",
                        "ajaxEditError",
                        "deleteVision",
                        "ajaxDeleteVisionSuccess",
                        "ajaxDeleteVisionError",
                        "onAddCommentKeydown",
                        "currentVisionEditable",
                        "onTextMouseEnter",
                        "onTextMouseLeave",
                        "onEditClick",
                        "ignoreClick",
                        "closeModal"
        );
        this.model.comments().bind("add", this.renderComments, this);
        this.render();
    },
    events: function(){
        var _events = {};

        _events["click " + this.sel.EDIT_SUBMIT] = "editSubmit";

        _events["click " + this.sel.DELETE_BUTTON] = "deleteVision";
        _events["keydown " + this.sel.ADD_COMMENT] = "onAddCommentKeydown";
        _events["mouseenter " + this.sel.TEXT_CONTAINER] = "onTextMouseEnter";
        _events["mouseleave " + this.sel.TEXT_CONTAINER] = "onTextMouseLeave";
        _events["click " + this.sel.EDIT_TEXT] = "onEditClick";

        _events["change " + this.sel.PRIVACY_INPUT] = "toggleEditSubmit";
        _events["keyup " + this.sel.TEXT_INPUT] = "toggleEditSubmit";
        _events["cut " + this.sel.TEXT_INPUT] = "toggleEditSubmit";
        _events["paste " + this.sel.TEXT_INPUT] = "toggleEditSubmit";
        // Used to ignore clicks to modal box. On others, we close modal
        _events["click " + this.sel.MODAL_BOX] = "ignoreClick";
        _events["click " + this.sel.CLOSE] = "closeModal";

        return _events;
    },
    render: function() {
        var pageMode = App.Var.Model.pageMode();

        var userId = this.model.userId();
        var addCommentVisibility = "hide";
        var deleteVisibility = "hide";
        var isPublic = "";
        var closeVisibility = "";
        // All links from vision details modal view should go to new page
        var urlTarget = " target=\"_blank\""


        var parentUserVisibility = "Hidden";
        var parentUserId = "";
        var parentUserName = "";

        if (userLoggedIn()) {
            addCommentVisibility = "";

            if (pageMode == App.Const.PageMode.VISION_DETAILS &&
                App.Var.Model.loggedInUserId() ==
                    App.Var.Model.currentUserId()) {
                deleteVisibility = "";
            } else if (pageMode == App.Const.PageMode.VISION_PAGE) {
                closeVisibility = "hide";
                urlTarget = ""
            }
            if (this.model.isPublic()) {    
                isPublic = "checked";
            };
            if (this.model.hasParent()) {
                var parentUserVisibility = "";
                parentUserId = this.model.parentUser().userId();
                parentUserName = this.model.parentUser().fullName();
            }
        }
        // This is stored to be used when rendering comments
        this.urlTarget = urlTarget;

        var variables = {
            userId: userId,
            name : this.model.name(),
            picture : this.model.picture().largeUrl(),
            text : this.model.text(),
            userPicture : USER['picture'],
            addCommentVisibility: addCommentVisibility,
            deleteVisibility: deleteVisibility,
            isPublic: isPublic,
            closeVisibility: closeVisibility,
            urlTarget: urlTarget,
            parentUserVisibility: parentUserVisibility,
            parentUserId: parentUserId,
            parentUserName: parentUserName,
        }
        var template = _.template($("#VisionDetailsModalTemplate").html(),
                                  variables);
        $(this.el).html(template);

        this.toggleEditSubmit();

        doAjax("/api/vision/" + this.model.visionId() + "/comments",
                JSON.stringify({
                                'visionId' : this.model.visionId(),
                                }),
                this.ajaxCommentsSuccess,
                this.ajaxCommentsError
        );
        return this;
    },

    toggleEditSubmit: function(e) {
        var text = $.trim($(this.el).find(this.sel.TEXT_INPUT).val());
        var textLength = text.length;
        var isPublic = $(this.el).find(this.sel.PRIVACY_INPUT).is(":checked");
        var change = false;
        var invalid = false;
        if (text != this.model.text()) {
            change = true;
            if (textLength <= 0) {
                invalid = true;
            }
        }
        if (isPublic != this.model.isPublic()) {
            change = true;
        }
        if (true == change && false == invalid) {
            $(this.el).find(this.sel.EDIT_SUBMIT).removeAttr("disabled");
        } else {
            $(this.el).find(this.sel.EDIT_SUBMIT).attr("disabled", "disabled");
        }
    },

    ajaxCommentsSuccess: function(data, textStatus, jqXHR) {
        this.model.setComments(data.comments);
        this.renderComments();

        console.log("REPOST USERS: " + JSON.stringify(data.repostUsers));
        var reposts = data.repostUsers;
        if (reposts.length > 0) {
            var repostChildren = [];
            for (var i = 0 ; i < reposts.length ; i++) {
                var userModel = new App.Backbone.Model.User(reposts[i]);
                var userView = new App.Backbone.View.VisionDetailsRepostUser(
                                                { model: userModel,
                                                    urlTarget: this.urlTarget});
                repostChildren.push(userView.el);
            }
            $(this.el).find(this.sel.REPOST_USERS).append(repostChildren);
            $(this.el).find(this.sel.REPOST_USERS_CONTAINER).show();
        }
    },
    ajaxCommentsError: function(jqXHR, textStatus, errorThrown) {
        // still show comment container
        $(this.el).find(this.sel.COMMENTS_CONTAINER).show();
    },
    renderComments: function() {
        if (this.model != null) {
            if (DEBUG) console.log("Render comments in vision details.");
            var container = $(this.el).find(this.sel.COMMENTS_CONTAINER).first();
            container.empty();
            var commentList = this.model.comments();
            if (commentList.length > 0) {
                this.comments = [];
                commentList.each(this.renderComment);
                container.show();
                container.append(this.comments);

                // These few lines are a total hack to get the scroll to
                // work. I tried lots of tricks/hacks with scrollHeight but
                // nothing worked across browsers better than this so far.
                container.animate({scrollTop: "1000000px"});

                this.comments = [];
            }
            $(this.el).find(this.sel.ADD_COMMENT).val("");
        }
    },
    renderComment: function(comment, index) {
        if (comment.visionCommentId() > 0) {
            var c = new App.Backbone.View.VisionDetailsComment(
                                           { model: comment,
                                             urlTarget: this.urlTarget });
            this.comments.push(c.el);
        }
    },
    editSubmit: function() {
        assert (this.model != null, "Invalid current vision");

        if (DEBUG) console.log("EDIT");
        var text = $.trim($(this.el).find(this.sel.TEXT_INPUT).val());
        var isPublic = $(this.el).find(this.sel.PRIVACY_INPUT).is(":checked");

        doAjax("/api/vision/" + this.model.visionId() + "/edit",
                JSON.stringify({
                                'visionId' : this.model.visionId(),
                                'text'     : text,
                                'isPublic' : isPublic,
                                }),
                this.ajaxEditSuccess,
                this.ajaxEditError
              );
    },
    ajaxEditSuccess: function(data, textStatus, jqXHR) {
        if (this.model) {
            this.model.edit(data.text, data.isPublic);
            $(this.el).find(this.sel.TEXT).html(data.text);
            this.toggleEditSubmit();
            $(this.el).find(this.sel.EDIT_FORM).hide();
            $(this.el).find(this.sel.TEXT_CONTAINER).show();
        }
    },
    ajaxEditError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },

    deleteVision: function() {
        if (this.model!= null) {
            if (DEBUG) console.log("DELETE");
            doAjax("/api/user/" + USER['id'] + "/delete_vision",
                   JSON.stringify({
                                    'visionId' : this.model.visionId(),
                                  }),
                   this.ajaxDeleteVisionSuccess,
                   this.ajaxDeleteVisionError
            );
        }
    },
    ajaxDeleteVisionSuccess: function(data, textStatus, jqXHR) {
        if (DEBUG) console.log("REMOVED ID: " + data.removedId);
        App.Var.Model.deleteVision(data.removedId);
        App.Var.View.hideVisionDetails();
    },
    ajaxDeleteVisionError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },
    ignoreClick: function(e) {
        e.stopPropagation();
    },
    closeModal: function(e) {
        App.Var.View.hideVisionDetails();
    },

    onAddCommentKeydown: function(e) {
        if(e.keyCode == 13) {
            e.preventDefault();
            var text = $.trim($(this.sel.ADD_COMMENT).val());
            if (text.length > 0) {
                App.Var.View.addVisionComment(
                            App.Var.Model.currentVision().visionId(),
                            text);
            }
        }

    },
    currentVisionEditable: function() {
        return userLoggedIn() && this.model.userId() == USER['id'];
    },
    onTextMouseEnter: function() {
        if (this.currentVisionEditable()) {
            $(this.el).find(this.sel.EDIT_TEXT).show();
        }
    },
    onTextMouseLeave: function() {
        if (this.currentVisionEditable()) {
            $(this.el).find(this.sel.EDIT_TEXT).hide();
        }
    },
    onEditClick: function() {
        if (this.currentVisionEditable()) {
            $(this.el).find(this.sel.TEXT_CONTAINER).hide();
            $(this.el).find(this.sel.EDIT_FORM).show();
        }
    },
});

