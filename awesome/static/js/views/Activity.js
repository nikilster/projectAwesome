App.Backbone.View.Activity = Backbone.View.extend({
    tagName: "div",
    className: "Activity",
    sel: {
        JOIN_SITE_TEMPLATE: "#ActivityJoinSiteTemplate",
        ADD_VISION_TEMPLATE: "#ActivityAddVisionTemplate",
        LIKE_VISION_TEMPLATE: "#ActivityLikeVisionTemplate",
        COMMENT_ON_VISION_TEMPLATE: "#ActivityCommentOnVisionTemplate",
        LIKE_VISION_COMMENT_TEMPLATE: "#ActivityLikeVisionCommentTemplate",
        FOLLOW_TEMPLATE: "#ActivityFollowTemplate",

        // Links
        USER_LINK: ".UserLink",
        VISION_USER_LINK: ".VisionUserLink",
        AUTHOR_LINK: ".AuthorLink",
        FOLLOWING_USER_LINK: ".FollowingUserLink",
        VISION_LINK: ".VisionLink",
    },
    constant: {
    },
    initialize: function() {
        _.bindAll(this, "userLink",
                        "visionUserLink",
                        "authorLink",
                        "followingUserLink",
                        "visionLink",
                        "navigateToUser",
                        "navigateToVision");
        this.render();
    },
    events: function() {
        var _events = {};
        _events["click " + this.sel.USER_LINK] = "userLink";
        _events["click " + this.sel.VISION_USER_LINK] = "visionUserLink";
        _events["click " + this.sel.AUTHOR_LINK] = "authorLink";
        _events["click " + this.sel.FOLLOWING_USER_LINK] = "followingUserLink";
        _events["click " + this.sel.VISION_LINK] = "visionLink";
        return _events;
    },
    render: function() {
        if (this.model.actionJoinSite()) {
            var variables = { userId: this.model.user().userId(),
                              name: this.model.user().fullName(),
                              picture: this.model.user().picture(),
                            };
            var template = _.template($(this.sel.JOIN_SITE_TEMPLATE).html(),
                                      variables);
            $(this.el).html(template);
        } else if (this.model.actionAddVision()) {
            var variables = { userId: this.model.user().userId(),
                              name: this.model.user().fullName(),
                              picture: this.model.user().picture(),
                              visionId: this.model.vision().visionId(),
                              visionPicture: this.model.vision().picture().mediumUrl(),
                              visionText: this.model.vision().text(),
                            };
            var template = _.template($(this.sel.ADD_VISION_TEMPLATE).html(),
                                      variables);
            $(this.el).html(template);
        } else if (this.model.actionLikeVision()) {
            var variables = { userId: this.model.user().userId(),
                              name: this.model.user().fullName(),
                              picture: this.model.user().picture(),
                              visionUserId: this.model.vision().user().userId(),
                              visionUserName: this.model.vision().user().fullName(),
                              visionId: this.model.vision().visionId(),
                              visionPicture: this.model.vision().picture().mediumUrl(),
                              visionText: this.model.vision().text(),
                            };
            var template = _.template($(this.sel.LIKE_VISION_TEMPLATE).html(),
                                      variables);
            $(this.el).html(template);
        } else if (this.model.actionLikeVisionComment()) {
            var variables = { userId: this.model.user().userId(),
                              name: this.model.user().fullName(),
                              picture: this.model.user().picture(),
                              visionUserId: this.model.vision().user().userId(),
                              visionUserName: this.model.vision().user().fullName(),
                              visionId: this.model.vision().visionId(),
                              visionPicture: this.model.vision().picture().mediumUrl(),
                              visionText: this.model.vision().text(),
                              authorUserId: this.model.visionComment().author().userId(),
                              authorUserName: this.model.visionComment().author().fullName(),
                              commentText: this.model.visionComment().text(),
                            };
            var template = _.template($(this.sel.LIKE_VISION_COMMENT_TEMPLATE).html(),
                                      variables);
            $(this.el).html(template);
        } else if (this.model.actionCommentOnVision()) {
            var variables = { userId: this.model.user().userId(),
                              name: this.model.user().fullName(),
                              picture: this.model.user().picture(),
                              visionUserId: this.model.vision().user().userId(),
                              visionUserName: this.model.vision().user().fullName(),
                              visionId: this.model.vision().visionId(),
                              visionPicture: this.model.vision().picture().mediumUrl(),
                              visionText: this.model.vision().text(),
                              commentText: this.model.visionComment().text(),
                            };
            var template = _.template($(this.sel.COMMENT_ON_VISION_TEMPLATE).html(),
                                      variables);
            $(this.el).html(template);

        } else if (this.model.actionFollow()) {
            var variables = { userId: this.model.user().userId(),
                              name: this.model.user().fullName(),
                              picture: this.model.user().picture(),
                              followingUserId: this.model.following().userId(),
                              followingName: this.model.following().fullName(),
                            };
            var template = _.template($(this.sel.FOLLOW_TEMPLATE).html(),
                                      variables);
            $(this.el).html(template);
        }
        return this;
    },
    navigateToUser: function(e, userId) {
        e.preventDefault();
        e.stopPropagation();
        App.Var.Router.navigate("/user/" + userId, {trigger: true});
    },
    navigateToVision: function(e, visionModel) {
        e.preventDefault();
        e.stopPropagation();
        App.Var.Model.setCurrentVision(visionModel);
        App.Var.Router.navigate("/vision/" + visionModel.visionId(),
                                {trigger: true});
    },
    userLink: function(e) {
        this.navigateToUser(e, this.model.user().userId());
    },
    visionUserLink: function(e) {
        this.navigateToUser(e, this.model.vision().user().userId());
    },
    authorLink: function(e) {
        this.navigateToUser(e, this.model.visionComment().author().userId());
    },
    followingUserLink: function(e) {
        this.navigateToUser(e, this.model.following().userId());
    },
    visionLink: function(e) {
        this.navigateToVision(e, this.model.vision());
    },
});

// $eof
