App.Backbone.Model.VisionComment = Backbone.Model.extend({
    defaults: {
        id: -1,
        authorId: -1,
        text: "",
        name: "",
        picture: "",
        created: null,
    },
    initialize: function() {
        this.set({ created: dateFromUTC(this.get("created")) });
    },
    visionCommentId: function() { return this.get("id"); },
    authorId: function() { return this.get("authorId"); },
    text: function() { return this.get("text"); },
    name: function() { return this.get("name"); },
    picture: function() { return this.get("picture"); },
    created: function() { return this.get("created"); },
    timeString: function() {
        return timeFromToday(this.created());
    },

});

