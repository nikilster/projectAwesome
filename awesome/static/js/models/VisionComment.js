App.Backbone.Model.VisionComment = Backbone.Model.extend({
    defaults: {
        id: -1,
        authorId: -1,
        text: "",
        name: "",
        picture: "",
    },
    initialize: function() {
    },
    visionCommentId: function() { return this.get("id"); },
    authorId: function() { return this.get("authorId"); },
    text: function() { return this.get("text"); },
    name: function() { return this.get("name"); },
    picture: function() { return this.get("picture"); },
});

