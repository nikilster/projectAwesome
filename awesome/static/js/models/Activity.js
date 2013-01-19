App.Backbone.Model.Activity = Backbone.Model.extend({
    defaults: {
        action: null,
        user: null,
        following: null,
        vision: null,
        visionComment: null,
    },
    constant: {
        action: {
            JOIN_SITE : "joinSite",
            UPDATE_PROFILE_PICTURE : "updateProfilePicture",
            UPDATE_DESCRIPTION: "updateDescription",

            ADD_VISION : "addVision",
            LIKE_VISION : "likeVision",
            COMMENT_ON_VISION : "commentOnVision",
            LIKE_VISION_COMMENT : "likeVisionComment",

            FOLLOW : "follow",
        },
    },
    initialize: function() {
        this.set({
            user : new App.Backbone.Model.User(this.get("user")),
            following: new App.Backbone.Model.User(this.get("following")),
            vision: new App.Backbone.Model.Vision(this.get("vision")),
            visionComment: new App.Backbone.Model.VisionComment(this.get("visionComment")),
        });
    },
    action: function() { return this.get("action"); },
    user: function() { return this.get("user"); },
    following: function() { return this.get("following"); },
    vision: function() { return this.get("vision"); },
    visionComment: function() { return this.get("visionComment"); },

    // Convenience functions on action
    actionJoinSite: function() {
        return this.action() == this.constant.action.JOIN_SITE;
    },
    actionAddVision: function() {
        return this.action() == this.constant.action.ADD_VISION;
    },
    actionLikeVision: function() {
        return this.action() == this.constant.action.LIKE_VISION;
    },
    actionCommentOnVision: function() {
        return this.action() == this.constant.action.COMMENT_ON_VISION;
    },
    actionLikeVisionComment: function() {
        return this.action() == this.constant.action.LIKE_VISION_COMMENT;
    },
    actionFollow: function() {
        return this.action() == this.constant.action.FOLLOW;
    },
});

// $eof
