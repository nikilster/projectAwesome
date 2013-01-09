
App.Backbone.View.VisionComment = Backbone.View.extend({
    className: "VisionComment",
    initialize: function() {
        _.bindAll(this, "gotoUser");
        this.render();
    },
    events: {
        "click .VisionCommentUserLink" : "gotoUser",
    },
    render: function() {
        var variables = { 'authorId' : this.model.authorId(),
                          'text': linkify(this.model.text()),
                          'name': this.model.name(),
                          'picture': this.model.picture()}
        var template = _.template($("#VisionCommentTemplate").html(),
                                  variables);
        $(this.el).html(template);

        return this;
    },
    gotoUser: function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (DEBUG) console.log("GOTO USER");
        App.Var.Router.navigate("/user/" + this.model.authorId(),
                                {trigger: true});
    },
});

