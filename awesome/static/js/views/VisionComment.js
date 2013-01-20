
App.Backbone.View.VisionComment = Backbone.View.extend({
    className: "VisionComment",
    initialize: function() {
        _.bindAll(this, "gotoUser",
                        // From like view
                        "showLikes");
        this.render();
    },
    sel: {
        LIKE: ".VisionLikeInfo",
    },
    events: {
        "click .VisionCommentUserLink" : "gotoUser",
    },
    render: function() {
        var variables = { 'authorId' : this.model.authorId(),
                          'text': linkify(this.model.text()),
                          'name': this.model.author().fullName(),
                          'picture': this.model.author().picture()}
        var template = _.template($("#VisionCommentTemplate").html(),
                                  variables);
        $(this.el).html(template);

        if (this.model.like() != null) {
            var likeView = new App.Backbone.View.Like(
                                                { model: this.model.like(),
                                                  parentView: this });
            $(this.el).find(this.sel.LIKE).append(likeView.el);
        }

        return this;
    },
    gotoUser: function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (DEBUG) console.log("GOTO USER");
        App.Var.Router.navigate("/user/" + this.model.authorId(),
                                {trigger: true});
    },
    showLikes: function(e) {
        App.Var.View.showVisionCommentLikes(this.model.visionCommentId());
    },
});

