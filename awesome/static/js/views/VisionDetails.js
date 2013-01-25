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

App.Backbone.View.VisionPreview = Backbone.View.extend({
    tagName: "div",
    className: "VisionPreview",
    initialize: function() {
        this.urlTarget = this.options.urlTarget;
        this.render();
    },
    render: function() {
        var variables = { target: this.urlTarget,
                          visionId: this.model.visionId(),
                          picture: this.model.picture().smallUrl()
                        };
        var template = _.template($("#VisionPreviewTemplate").html(),
                                  variables);
        $(this.el).html(template);

        return this;
    },
});

App.Backbone.View.VisionDetailsRootUserBox = Backbone.View.extend({
    tagName: "div",
    initialize: function() {
        this.urlTarget = this.options.urlTarget;
        this.visions = this.options.visions;

        this.render();
    },
    render: function() {
        var variables = { name : this.model.fullName(),
                          userId: this.model.userId(),
                          picture: this.model.picture(),
                          target: this.urlTarget };
        var template = _.template($("#VisionDetailsRootUserTemplate").html(),
                                  variables);
        $(this.el).html(template);

        var visionViews = []
        for (var i = 0 ; i < this.visions.length ; i++) {
            var vision = this.visions.at(i);
            var view = new App.Backbone.View.VisionPreview(
                                        { model: vision,
                                          urlTarget: this.urlTarget });
            visionViews.push(view.el);
        }
        var container = $(this.el).find("#VisionDetailsRootUserVisions");
        container.empty().append(visionViews);
        
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
        EDIT_ERROR : "#VisionDetailsEditError",
        TEXT : "#VisionDetailsText",
        MODAL_BOX : "#VisionDetailsModalBox",
        CLOSE : "#VisionDetailsClose",
        TEXT_INPUT : "#VisionDetailsTextInput",
        PRIVACY_INPUT : "#VisionDetailsPrivacyInput",
        EDIT_SUBMIT : "#VisionDetailsEditSubmit",
        DELETE_BUTTON : "#VisionDeleteButton",
        DELETE_CONFIRMATION: "#VisionDeleteConfirmation",
        REALLY_DELETE: "#VisionReallyDeleteButton",
        DELETE_CLOSE: "#VisionDeleteCloseButton",
        LIKE: ".VisionLikeInfo",
        LOCK: ".VisionDetailsLock",
    },
    initialize: function() {
        _.bindAll(this, "toggleEditSubmit",
                        "ajaxCommentsSuccess",
                        "ajaxCommentsError",
                        "renderComments",
                        "renderComment",
                        "renderRootUserBox",
                        "editSubmit",
                        "ajaxEditSuccess",
                        "ajaxEditError",
                        "toggleDeleteConfirmation",
                        "deleteVision",
                        "ajaxDeleteVisionSuccess",
                        "ajaxDeleteVisionError",
                        "onAddCommentKeydown",
                        "currentVisionEditable",
                        "onTextMouseEnter",
                        "onTextMouseLeave",
                        "onEditClick",
                        "ignoreClick",
                        "closeModal",
                        "privacyChange",
                        "onNewComment",
                        // Called from like view
                        "showLikes"
        );
        this.model.bind("new-comment", this.onNewComment, this);

        this.model.comments().bind("add", this.renderComments, this);
        this.model.bind("change:privacy", this.privacyChange, this);
        this.render();
    },
    events: function(){
        var _events = {};

        _events["click " + this.sel.EDIT_SUBMIT] = "editSubmit";

        _events["click " + this.sel.DELETE_BUTTON] = "toggleDeleteConfirmation";
        _events["click " + this.sel.DELETE_CLOSE] = "toggleDeleteConfirmation";
        _events["click " + this.sel.REALLY_DELETE] = "deleteVision";
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
        var closeVisibility = "";
        // All links from vision details modal view should go to new page
        var urlTarget = " target=\"_blank\""


        var parentUserVisibility = "Hidden";
        var parentUserId = "";
        var parentUserName = "";

        var isPrivate = "checked";
        var lockVisibility = "";
        if (userLoggedIn()) {
            addCommentVisibility = "";

            if (pageMode == App.Const.PageMode.VISION_DETAILS &&
                App.Var.Model.loggedInUserId() ==
                App.Var.Model.currentVision().userId()) {
                deleteVisibility = "";
            }
            if (pageMode == App.Const.PageMode.VISION_PAGE) {
                closeVisibility = "hide";
                urlTarget = ""
            }
            if (this.model.isPublic()) {    
                isPrivate = "";
                lockVisibility = "Hidden";
            };
            if (this.model.hasParent()) {
                var parentUserVisibility = "";
                parentUserId = this.model.parentUser().userId();
                parentUserName = this.model.parentUser().fullName();
            }
        }
        // This is stored to be used when rendering comments
        this.urlTarget = urlTarget;

        var commentPrompt = this.model.getCommentPrompt(App.Var.Model.loggedInUserId());

        var variables = {
            userId: userId,
            name : this.model.user().fullName(),
            picture : this.model.picture().largeUrl(),
            text : linkify(this.model.text()),
            created: this.model.timeString(),
            userPicture : USER['picture'],
            addCommentVisibility: addCommentVisibility,
            deleteVisibility: deleteVisibility,
            isPrivate: isPrivate,
            lockVisibility: lockVisibility,
            closeVisibility: closeVisibility,
            urlTarget: urlTarget,
            parentUserVisibility: parentUserVisibility,
            parentUserId: parentUserId,
            parentUserName: parentUserName,
            commentPrompt: commentPrompt,
        }
        var template = _.template($("#VisionDetailsModalTemplate").html(),
                                  variables);
        $(this.el).html(template);

        $(this.el).find(this.sel.ADD_COMMENT).autosize();

        if (this.model.like() != null) {
            var likeView = new App.Backbone.View.Like(
                                                { model: this.model.like(),
                                                  parentView: this });
            $(this.el).find(this.sel.LIKE).append(likeView.el);
        }

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
    onNewComment: function() {
        $(this.sel.ADD_COMMENT).removeAttr("style");
    },

    toggleEditSubmit: function(e) {
        var text = $.trim($(this.el).find(this.sel.TEXT_INPUT).val());
        var textLength = text.length;
        var isPrivate = $(this.el).find(this.sel.PRIVACY_INPUT).is(":checked");
        var change = false;
        var invalid = false;
        if (text != this.model.text()) {
            change = true;
            if (textLength <= 0) {
                invalid = true;
            }
        }
        if (isPrivate == this.model.isPublic()) {
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

        if (DEBUG) {
            console.log("REPOST USERS: " + JSON.stringify(data.repostUsers));
            console.log("ORIG USER: " + JSON.stringify(data.rootUser));
            console.log("ORIG VISIONS: " + JSON.stringify(data.rootUserVisions));
        }
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

        if (!(typeof data.rootUser === 'undefined')) {
            var user = new App.Backbone.Model.User(data.rootUser);
            var visions = new App.Backbone.Model.VisionList(data.rootUserVisions);
            this.renderRootUserBox(user, visions);
        }
    },
    ajaxCommentsError: function(jqXHR, textStatus, errorThrown) {
        // still show comment container
        $(this.el).find(this.sel.COMMENTS_CONTAINER).show();
    },
    renderRootUserBox: function(user, visions) {
        var view = new App.Backbone.View.VisionDetailsRootUserBox(
                                                { model: user,
                                                  urlTarget: this.urlTarget,
                                                  visions: visions});
        $(this.el).find("#VisionDetailsRootUserContainer").empty().append(view.el);
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
        var isPublic = !($(this.el).find(this.sel.PRIVACY_INPUT).is(":checked"));

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
        if (data.errorMsg != "") {
            $(this.el).find(this.sel.EDIT_ERROR).html(data.errorMsg).show();
        } else if (this.model) {
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

    toggleDeleteConfirmation: function(e) {
        e.stopPropagation();
        e.preventDefault();

        var modal = $(this.el).find(this.sel.DELETE_CONFIRMATION).first();
        if (modal.is(":visible")) {
            modal.fadeOut();
        } else {
            modal.fadeIn();
        }
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
        var code = (e.keyCode ? e.keyCode : e.which);
        if (code == 13) {
            e.preventDefault();
            var text = $.trim($(this.sel.ADD_COMMENT).val());
            if (text.length > 0) {
                this.model.addVisionComment(text);
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
    privacyChange: function() {
        if (this.model.isPublic()) {
            $(this.el).find(this.sel.LOCK).hide();
        } else {
            $(this.el).find(this.sel.LOCK).show();
        }
    },
    showLikes: function(e) {
        App.Var.View.showVisionLikes(this.model.visionId());
    },
});

