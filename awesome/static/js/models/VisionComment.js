App.Backbone.Model.VisionComment = Backbone.Model.extend({
    defaults: {
        id: -1,
        authorId: -1,
        text: "",
        name: "",
        picture: "",
        created: null,
        like: null,
    },
    initialize: function() {
        _.bindAll(this, "ajaxLikeSuccess", "ajaxLikeError");

        this.set({ created: dateFromUTC(this.get("created")) });

        if (this.get("like") != null) {
            this.set({ like: new App.Backbone.Model.Like(this.get("like")) });
        }
    },
    visionCommentId: function() { return this.get("id"); },
    authorId: function() { return this.get("authorId"); },
    text: function() { return this.get("text"); },
    name: function() { return this.get("name"); },
    picture: function() { return this.get("picture"); },
    like: function() { return this.get("like"); },
    created: function() { return this.get("created"); },
    timeString: function() {
        return timeFromToday(this.created());
    },

    setLike: function(like, likeCount) {
        // USER MUST BE LOGGED IN
        if (userLoggedIn()) {
            this.like().set({userLike: like, likeCount: likeCount});
        }
    },
    toggleLike: function() {
        if (userLoggedIn() && this.like() != null) {
            if (this.like().userLike() == false) {
                this.ajaxLike(true);
            } else {
                this.ajaxLike(false);
            }
        }
    },
    ajaxLike: function(like) {
        if (DEBUG) console.log("LIKE: " + this.visionId());
        doAjax("/api/user/" + USER['id'] + "/like_vision_comment",
                JSON.stringify({
                                'visionCommentId' : this.visionCommentId(),
                                'like' : like,
                                }),
                this.ajaxLikeSuccess,
                this.ajaxLikeError
        );
    },
    ajaxLikeSuccess: function(data, textStatus, jqXHR) {
        this.setLike(data.like, data.likeCount);
    },
    ajaxLikeError: function(jqXHR, textStatus, errorThrown) {

    },
});

