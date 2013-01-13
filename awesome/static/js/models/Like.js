App.Backbone.Model.Like = Backbone.Model.extend({
    defaults: {
        userLike: null,
        likeCount: -1,
    },
    initialize: function() {
    },
    userLike: function() { return this.get("userLike"); },
    likeCount: function() { return this.get("likeCount"); },
});

// $eof
