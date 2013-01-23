App.Backbone.View.Activity = Backbone.View.extend({
    tagName: "div",
    className: "Activity",
    sel: {
        JOIN_TEMPLATE: "#ActivityJoinSiteTemplate",
        FOLLOW_TEMPLATE: "#ActivityFollowTemplate",

        ADD_VISION_TEMPLATE: "#ActivityAddVisionTemplate",
        COMMENT_ON_VISION_TEMPLATE: "#ActivityCommentOnVisionTemplate",
        LIKE_VISION_TEMPLATE: "#ActivityLikeVisionTemplate",
        LIKE_VISION_COMMENT_TEMPLATE: "#ActivityLikeVisionCommentTemplate",

        // Links
        USER_LINK: ".UserLink",
        VISION_USER_LINK: ".VisionUserLink",
        VISION_LIKER_LINK: ".VisionLikerLink",
        COMMENT_LIKER_LINK: ".CommentLikerLink",
        AUTHOR_LINK: ".AuthorLink",
        FOLLOWING_USER_LINK: ".FollowingUserLink",
        VISION_LINK: ".VisionLink",

        VISION_CONTAINER: ".VisionContainer",
    },
    constant: {
    },
    initialize: function() {
        _.bindAll(this, "userLink",
                        "visionUserLink",
                        "visionLikerLink",
                        "commentLikerLink",
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
        _events["click " + this.sel.VISION_LIKER_LINK] = "visionLikerLink";
        _events["click " + this.sel.COMMENT_LIKER_LINK] = "commentLikerLink";
        _events["click " + this.sel.AUTHOR_LINK] = "authorLink";
        _events["click " + this.sel.FOLLOWING_USER_LINK] = "followingUserLink";
        _events["click " + this.sel.VISION_LINK] = "visionLink";
        return _events;
    },
    render: function() {
        var time = this.model.timeString();
        if (this.model.typeJoin()) {
            // JOIN ACTIVITY
            var variables = { userId: this.model.user().userId(),
                              name: this.model.user().fullName(),
                              picture: this.model.user().picture(),
                              time: time,
                            };
            var template = _.template($(this.sel.JOIN_TEMPLATE).html(),
                                      variables);
            $(this.el).html(template);
        } else if (this.model.typeFollow()) {
            // FOLLOW ACTIVITY
            var variables = { userId: this.model.user().userId(),
                              name: this.model.user().fullName(),
                              picture: this.model.user().picture(),
                              followingUserId: this.model.following().userId(),
                              followingName: this.model.following().fullName(),
                              time: time,
                            };
            var template = _.template($(this.sel.FOLLOW_TEMPLATE).html(),
                                      variables);
            $(this.el).html(template);
        } else if (this.model.typeVision()) {
            // VISION-RELATED ACTIVITY
            if (this.model.recentActionAddVision()) {
                // Newly posted vision
                var variables = { userId: this.model.vision().user().userId(),
                                  name: this.model.vision().user().fullName(),
                                  picture: this.model.vision().user().picture(),
                                  visionId: this.model.vision().visionId(),
                                  time: time,
                                };
                var template = _.template(
                                        $(this.sel.ADD_VISION_TEMPLATE).html(),
                                        variables);
                $(this.el).html(template);
            } else if (this.model.recentActionCommentOnVision()) {
                var comments = this.model.comments();
                assert(comments.length > 0, "No comments");
                var comment = comments.at(0);
                var variables = {
                            userId: comment.author().userId(),
                            name: comment.author().fullName(),
                            picture: comment.author().picture(),
                            visionUserId: this.model.vision().user().userId(),
                            visionUserName: this.model.vision().user().fullName(),
                            visionId: this.model.vision().visionId(),
                            commentText: comment.text(),
                            time: time,
                            };
                var template = _.template($(this.sel.COMMENT_ON_VISION_TEMPLATE).html(), variables);
                $(this.el).html(template);
            } else if (this.model.recentActionLikeVision()) {
                var likers = this.model.likers();
                assert(likers.length > 0, "No likers");
                var likeUser = likers.at(0);
                var vision = this.model.vision();
                var variables = { 
                            userId: likeUser.userId(),
                            name: likeUser.fullName(),
                            picture: likeUser.picture(),
                            visionUserId: vision.user().userId(),
                            visionUserName: vision.user().fullName(),
                            visionId: vision.visionId(),
                            time: time,
                };
                var template = _.template(
                                    $(this.sel.LIKE_VISION_TEMPLATE).html(),
                                    variables);
                $(this.el).html(template);
            } else if (this.model.recentActionLikeVisionComment()) {
                var likers = this.model.commentLikers();
                assert(likers.length > 0, "No comment likers");
                var likeUser = likers.at(0);
                var vision = this.model.vision();
                var variables = {
                            userId: likeUser.userId(),
                            name: likeUser.fullName(),
                            picture: likeUser.picture(),
                            visionUserId: vision.user().userId(),
                            visionUserName: vision.user().fullName(),
                            visionId: vision.visionId(),
                            authorUserId: "",
                            authorUserName: "",
                            commentText: "",
                            time: time,
                };
                var template = _.template(
                            $(this.sel.LIKE_VISION_COMMENT_TEMPLATE).html(),
                            variables);
                $(this.el).html(template);
            } else {
                assert(false, "Unsupported vision action type");
            }
            // Now tack on vision view
            var view = new App.Backbone.View.Vision(
                                            { model: this.model.vision(),
                                              parentView: null });
            $(this.el).find(this.sel.VISION_CONTAINER).append(view.el);
        }
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
    visionLikerLink: function(e) {
        this.navigateToUser(e, this.model.likers().at(0).userId());
    },
    commentLikerLink: function(e) {
        this.navigateToUser(e, this.model.commentLikers().at(0).userId());
    },
    authorLink: function(e) {
        this.navigateToUser(e, this.model.comments().at(0).author().userId());
    },
    followingUserLink: function(e) {
        this.navigateToUser(e, this.model.following().userId());
    },
    visionLink: function(e) {
        this.navigateToVision(e, this.model.vision());
    },
});

// $eof
