App.Backbone.Model.VisionComment = Backbone.Model.extend({
    defaults: {
        id: -1,
        authorId: -1,
        text: "",
        picture: "",
        created: null,
        like: null,
        author: null,
        picture: null,
    },
    initialize: function() {
        _.bindAll(this, "ajaxLikeSuccess", "ajaxLikeError");

        this.set({ author: new App.Backbone.Model.User(this.get("author")),
                   picture: new App.Backbone.Model.Picture(this.get("picture")),
                   created: dateFromUTC(this.get("created")) });

        if (this.get("like") != null) {
            this.set({ like: new App.Backbone.Model.Like(this.get("like")) });
        }
    },
    visionCommentId: function() { return this.get("id"); },
    author: function() { return this.get("author"); },
    authorId: function() { return this.get("authorId"); },
    text: function() { return this.get("text"); },
    like: function() { return this.get("like"); },
    created: function() { return this.get("created"); },
    timeString: function() {
        return timeFromToday(this.created());
    },
    picture: function() { return this.get("picture"); },
    hasPicture: function() {
        return (this.picture() != null) &&
               (this.picture().pictureId() > 0);
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

