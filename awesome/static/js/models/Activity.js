App.Backbone.Model.Activity = Backbone.Model.extend({
    defaults: {
        type: null,
        user: null,
        following: null,
        vision: null,
        newVision: false,
        likers: null,
        comments: null,
        commentLikers: null,
        recentAction: null,
    },
    constant: {
        type: {
            JOIN : "join",
            FOLLOW: "follow",
            VISION: "vision",
        },
        action: {
            ADD_VISION : "addVision",
            LIKE_VISION : "likeVision",
            COMMENT_ON_VISION : "commentOnVision",
            LIKE_VISION_COMMENT : "likeVisionComment",
        },
    },
    initialize: function() {
        this.set({
            user : new App.Backbone.Model.User(this.get("user")),
            following: new App.Backbone.Model.User(this.get("following")),
            vision: new App.Backbone.Model.Vision(this.get("vision")),
            likers: new App.Backbone.Model.UserList(this.get("likers")),
            comments: new App.Backbone.Model.VisionCommentList(this.get("comments")),
            commentLikers: new App.Backbone.Model.UserList(this.get("commentLikers")),
            visionComment: new App.Backbone.Model.VisionComment(this.get("visionComment")),
        });
    },
    type: function() { return this.get("type"); },
    recentAction: function() { return this.get("recentAction"); },
    user: function() { return this.get("user"); },
    following: function() { return this.get("following"); },
    vision: function() { return this.get("vision"); },
    newVision: function() { return this.get("newVision"); },
    likers: function() { return this.get("likers"); },
    comments: function() { return this.get("comments"); },
    commentLikers: function() { return this.get("commentLikers"); },

    typeJoin: function() { return this.type() == this.constant.type.JOIN; },
    typeFollow: function() { return this.type() == this.constant.type.FOLLOW; },
    typeVision: function() { return this.type() == this.constant.type.VISION; },

    recentActionAddVision: function() {
        return this.recentAction() == this.constant.action.ADD_VISION;
    },
    recentActionLikeVision: function() {
        return this.recentAction() == this.constant.action.LIKE_VISION;
    },
    recentActionCommentOnVision: function() {
        return this.recentAction() == this.constant.action.COMMENT_ON_VISION;
    },
    recentActionLikeVisionComment: function() {
        return this.recentAction() == this.constant.action.LIKE_VISION_COMMENT;
    },
});

// $eof
